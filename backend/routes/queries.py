from flask import Blueprint, jsonify, request
import os
import json
import uuid
import datetime

# Directory to store query history
QUERY_HISTORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'query_history')
os.makedirs(QUERY_HISTORY_DIR, exist_ok=True)

from routes.graphs import graph_manager
from models.query import SPARQLQueryProcessor

# Initialize SPARQL query processor
sparql_processor = SPARQLQueryProcessor()

query_bp = Blueprint("query_bp", __name__)

# Routes for SPARQL query interface

# Execute a SPARQL query
@query_bp.route("/api/queries", methods=["POST"])
def execute_query():
    data = request.get_json()
    query = data.get("query")
    graph_id = data.get("graph_id")

    if not query:
        return jsonify({"error": "Query is required"}), 400
    if not graph_id:
        graphs = graph_manager.list_graphs()
        if len(graphs) == 0:
            return jsonify({"error": "no graph available"}), 404
        else:
            graph_id = graphs.pop().get('graph_id')
        # return jsonify({'error': 'Graph ID is required'}), 400

    # Retrieve the Graph instance
    graph_obj = graph_manager.get_graph_object(graph_id)
    if not graph_obj:
        return jsonify({"error": "Graph not found"}), 404

    try:
        # Execute the query against the RDF graph
        qres = graph_obj.graph.query(query)
        results = []
        print("query: ", query)
        print("result: ", qres, qres.vars)
        vars = qres.vars if qres.vars else []
        for row in qres:
            # Convert each row to a dict of variable name -> value
            if not qres.vars:
                vars = ['s', 'p', 'o']
                results.append({str(var): str(row[idx]) for idx,var in zip(range(3),'spo')})
            else:
                results.append({str(var): str(row[var]) for var in qres.vars})
        response = {"results": results, "count": len(results), "vars": vars}

        # Persist query history
        query_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        history_entry = {
            "query_id": query_id,
            "query": query,
            "timestamp": timestamp,
            "results": results
        }
        history_dir = os.path.join(QUERY_HISTORY_DIR, graph_id)
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)
        file_path = os.path.join(history_dir, f"{query_id}.json")
        with open(file_path, 'w') as f:
            json.dump(history_entry, f, default=str)

        # Include query_id in response for client reference
        response["query_id"] = query_id
        return jsonify(response), 200
    except Exception as e:
        print(e)
        e.printStackTrace()
        return jsonify({"error": str(e)}), 400

# Get query history
@query_bp.route("/api/queries/history/<graph_id>", methods=["GET"])
def get_query_history(graph_id):
    # Retrieve query history from persistent storage
    history = []
    history_dir = os.path.join(QUERY_HISTORY_DIR, graph_id)
    if os.path.isdir(history_dir):
        for filename in os.listdir(history_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(history_dir, filename), 'r') as f:
                        entry = json.load(f)
                        history.append(entry)
                except Exception:
                    continue
    # Sort by timestamp descending
    history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return jsonify({"history": history})

# Get query results by ID
@query_bp.route("/api/queries/<graph_id>/<query_id>", methods=["GET"])
def get_query_result(graph_id, query_id):
    # Retrieve the query result by ID from persistent storage
    history_dir = os.path.join(QUERY_HISTORY_DIR, graph_id)
    file_path = os.path.join(history_dir, f"{query_id}.json")
    if not os.path.isfile(file_path):
        return jsonify({"error": "Query not found"}), 404
    try:
        with open(file_path, 'r') as f:
            entry = json.load(f)
        return jsonify(entry)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

