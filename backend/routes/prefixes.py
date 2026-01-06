from flask import Blueprint, jsonify, request
from routes.graphs import graph_manager

prefixes_bp = Blueprint("prefixes_bp", __name__)

@prefixes_bp.route("/api/prefixes", methods=["GET"])
def get_prefixes():
    return jsonify(graph_manager.prefixes)

@prefixes_bp.route("/api/prefixes", methods=["POST"])
def add_prefix():
    data = request.get_json()
    prefix = data.get("prefix")
    uri = data.get("uri")
    if not prefix or not uri:
        return jsonify({"error": "prefix and uri required"}), 400
    try:
        graph_manager.add_prefix(prefix, uri)
        return jsonify({"message": "prefix added"}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@prefixes_bp.route("/api/prefixes/<string:prefix>", methods=["PUT"])
def update_prefix(prefix):
    data = request.get_json()
    uri = data.get("uri")
    if not uri:
        return jsonify({"error": "uri required"}), 400
    try:
        graph_manager.update_prefix(prefix, uri)
        return jsonify({"message": "prefix updated"})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@prefixes_bp.route("/api/prefixes/<string:prefix>", methods=["DELETE"])
def delete_prefix(prefix):
    try:
        if graph_manager.remove_prefix(prefix):
            return jsonify({"message": "prefix removed"})
        else:
            return jsonify({"error": "prefix not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 400
