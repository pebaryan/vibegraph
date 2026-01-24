import os
from flask import Blueprint, jsonify, request
from models.graph import GraphManager
from routes.search import search_engine
from decorators import handle_errors, validate_graph_id

# Initialize graph manager
graph_manager = GraphManager()

graph_bp = Blueprint("graph_bp", __name__)

# Routes for graph management


# Create a new graph
@graph_bp.route("/api/graphs", methods=["POST"])
def create_graph():
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "Name is required"}), 400

    # Optional SPARQL source parameters
    sparql_read = data.get("sparql_read")
    sparql_update = data.get("sparql_update")
    auth_type = data.get("auth_type", "None")
    auth_info = data.get("auth_info")
    result = graph_manager.create_graph(
        name, sparql_read, sparql_update, auth_type, auth_info
    )
    return jsonify(result), 201


# List all graphs
@graph_bp.route("/api/graphs", methods=["GET"])
def list_graphs():
    graphs = graph_manager.list_graphs()
    return jsonify({"graphs": graphs})


# Get triples for a graph
@graph_bp.route("/api/graphs/<graph_id>/triples", methods=["GET"])
def get_triples(graph_id):
    try:
        triples = graph_manager.get_triples(graph_id)
        return jsonify({"triples": triples})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@graph_bp.route("/api/graphs/<graph_id>/triples", methods=["POST"])
def add_triple(graph_id):
    data = request.get_json()
    try:
        if graph_manager.add_triple(
            graph_id, (data["subject"], data["predicate"], data["object"])
        ):
            return jsonify({"message": "triple added"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Upload RDF file for a graph
@graph_bp.route("/api/graphs/<graph_id>/upload", methods=["POST"])
def upload_graph(graph_id):
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    try:
        graph_obj = graph_manager.get_graph_object(graph_id)
        if not graph_obj:
            return jsonify({"error": "Graph not found"}), 404
        # Determine RDF format: use optional form field first
        filename = file.filename.lower()
        fmt = request.form.get("format")
        if not fmt:
            if filename.endswith(".ttl") or filename.endswith(".turtle"):
                fmt = "turtle"
            elif filename.endswith(".trig"):
                fmt = "trig"
            elif filename.endswith(".nt"):
                fmt = "nt"
            elif filename.endswith(".nt"):
                fmt = "nquads"
            elif (
                filename.endswith(".rdf")
                or filename.endswith(".owl")
                or filename.endswith("xml")
            ):
                fmt = "xml"
            else:
                fmt = "turtle"  # default fallback
        graph_obj.graph.parse(file, format=fmt)
        graph_manager._save()
        graph_manager.index_graph(graph_obj, search_engine)
        return jsonify({"message": "Graph uploaded"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Get a specific graph by ID
@graph_bp.route("/api/graphs/<graph_id>", methods=["GET"])
def get_graph(graph_id):
    graph = graph_manager.get_graph(graph_id)
    if graph:
        return jsonify(graph)
    return jsonify({"error": "Graph not found"}), 404


# Delete a graph by ID
@graph_bp.route("/api/graphs/<graph_id>", methods=["DELETE"])
def delete_graph(graph_id):
    if graph_manager.delete_graph(graph_id):
        return jsonify({"message": "Graph deleted successfully"}), 200


# Re‑index all graphs
@graph_bp.route("/api/graphs/reindex", methods=["POST"])
def reindex_all_graphs():
    try:
        count = graph_manager.reindex_all(search_engine)
        return jsonify({"message": f"Re‑indexed {count} graphs"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Update a graph name
@graph_bp.route("/api/graphs/<graph_id>", methods=["PUT"])
def update_graph(graph_id):
    data = request.get_json()
    name = data.get("name")
    if not name:
        return jsonify({"error": "Name is required"}), 400

    if graph_manager.update_graph(graph_id, name):
        return jsonify({"message": "Graph name updated successfully"}), 200
    return jsonify({"error": "Graph not found"}), 404
