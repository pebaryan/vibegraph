"""
SPARQL Endpoint for VibeGraph
This module provides a SPARQL endpoint that allows querying RDF data through the SPARQL protocol.
"""

from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest
from models.graph import GraphManager
from routes.search import search_engine

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

@sparql_bp.route("/sparql", methods=["GET", "POST"])
def sparql_endpoint():
    """Handle SPARQL queries."""
    try:
        # Parse the SPARQL query
        query = parse_sparql_query()
        
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
            "graph_id": graph_id
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@sparql_bp.route("/sparql", methods=["OPTIONS"])
def sparql_options():
    """Handle CORS preflight requests."""
    return jsonify({}), 200