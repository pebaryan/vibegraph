"""
Enhanced SPARQL Endpoint with Separate Read/Write Operations
This module provides dedicated endpoints for SPARQL read and write operations.
"""

from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from models.graph import GraphManager
from routes.search import search_engine
import re

# Initialize GraphManager
graph_manager = GraphManager()

# Create SPARQL blueprint
sparql_bp = Blueprint("sparql_bp", __name__)

def parse_sparql_query():
    """Parse SPARQL query from request."""
    if request.method == "GET":
        query = request.args.get("query")
        if not query:
            raise BadRequest("SPARQL query parameter 'query' is required")
    else:  # POST
        if not request.is_json:
            raise BadRequest("Content-Type must be application/json")
        data = request.get_json()
        query = data.get("query")
        if not query:
            raise BadRequest("SPARQL query is required in request body")
    return query

def get_query_type(query):
    """Determine the type of SPARQL query."""
    query_upper = query.strip().upper()
    if query_upper.startswith("SELECT"):
        return "SELECT"
    elif query_upper.startswith("CONSTRUCT"):
        return "CONSTRUCT"
    elif query_upper.startswith("DESCRIBE"):
        return "DESCRIBE"
    elif query_upper.startswith("ASK"):
        return "ASK"
    elif query_upper.startswith("INSERT") or query_upper.startswith("DELETE") or query_upper.startswith("WITH"):
        return "UPDATE"
    else:
        return "UNKNOWN"

@sparql_bp.route("/sparql/query", methods=["GET", "POST"])
def sparql_query_endpoint():
    """Handle SPARQL read queries (SELECT, CONSTRUCT, DESCRIBE, ASK)."""
    try:
        # Parse the SPARQL query
        query = parse_sparql_query()
        
        # Determine query type
        query_type = get_query_type(query)
        if query_type == "UPDATE":
            return jsonify({"error": "Write operations not allowed on query endpoint"}), 400
        
        # Extract graph_id from request parameters or use default
        graph_id = request.args.get("graph_id") or request.json.get("graph_id") if request.is_json else None
        
        # If no graph_id specified, try to use first available graph
        if not graph_id:
            graphs = graph_manager.list_graphs()
            if not graphs:
                return jsonify({"error": "No graphs available"}), 404
            graph_id = graphs[0]["graph_id"]
        
        # Get the graph object
        graph_obj = graph_manager.get_graph_object(graph_id)
        if not graph_obj:
            return jsonify({"error": "Graph not found"}), 404
        
        # Execute the SPARQL query
        qres = graph_obj.graph.query(query)
        
        # Convert results to JSON format
        results = []
        vars = qres.vars if qres.vars else []
        
        for row in qres:
            if not qres.vars:
                # For SELECT queries without variables, use default variable names
                vars = ['s', 'p', 'o']
                results.append({str(var): str(row[idx]) for idx,var in zip(range(3),'spo')})
            else:
                results.append({str(var): str(row[var]) for var in qres.vars})
        
        return jsonify({
            "results": results,
            "count": len(results),
            "vars": vars,
            "graph_id": graph_id,
            "query_type": query_type
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@sparql_bp.route("/sparql/update", methods=["POST"])
def sparql_update_endpoint():
    """Handle SPARQL update queries (INSERT, DELETE, WITH)."""
    try:
        # Parse the SPARQL query
        query = parse_sparql_query()
        
        # Determine query type
        query_type = get_query_type(query)
        if query_type != "UPDATE":
            return jsonify({"error": "Read operations not allowed on update endpoint"}), 400
        
        # Extract graph_id from request parameters or use default
        graph_id = request.args.get("graph_id") or request.json.get("graph_id") if request.is_json else None
        
        # If no graph_id specified, try to use first available graph
        if not graph_id:
            graphs = graph_manager.list_graphs()
            if not graphs:
                return jsonify({"error": "No graphs available"}), 404
            graph_id = graphs[0]["graph_id"]
        
        # Get the graph object
        graph_obj = graph_manager.get_graph_object(graph_id)
        if not graph_obj:
            return jsonify({"error": "Graph not found"}), 404
        
        # Execute the SPARQL update
        # Note: RDFLib supports SPARQL UPDATE operations
        graph_obj.graph.update(query)
        
        return jsonify({
            "message": "Update executed successfully",
            "graph_id": graph_id,
            "query_type": query_type
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@sparql_bp.route("/sparql", methods=["OPTIONS"])
def sparql_options():
    """Handle CORS preflight requests."""
    return jsonify({}), 200

# Additional helper endpoints for query information
@sparql_bp.route("/sparql/info", methods=["GET"])
def sparql_info():
    """Return information about SPARQL endpoint capabilities."""
    return jsonify({
        "read_endpoint": "/sparql/query",
        "update_endpoint": "/sparql/update",
        "supported_operations": ["SELECT", "CONSTRUCT", "DESCRIBE", "ASK", "INSERT", "DELETE", "WITH"],
        "description": "Dedicated SPARQL endpoints for read and write operations"
    }), 200