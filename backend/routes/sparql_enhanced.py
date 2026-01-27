"""
Enhanced SPARQL Endpoint with Separate Read/Write Operations
This module provides dedicated endpoints for SPARQL read and write operations.
"""

from flask import Blueprint, request, jsonify, Response
from werkzeug.exceptions import BadRequest
from routes.graphs import graph_manager
import re
from rdflib.query import Result
import pyparsing


# Create SPARQL blueprint
sparql_bp = Blueprint("sparql_bp", __name__)

SPARQL_QUERY_CONTENT_TYPE = "application/sparql-query"
SPARQL_UPDATE_CONTENT_TYPE = "application/sparql-update"


def _content_type():
    if not request.content_type:
        return ""
    return request.content_type.split(";")[0].strip().lower()


def _read_raw_body():
    data = request.get_data(cache=False, as_text=True)
    if data is not None:
        data = data.strip()
    return data or None


def _parse_request_param(param_name):
    """Parse SPARQL parameter from GET or POST in a SPARQL-protocol-friendly way."""
    if request.method == "GET":
        return request.args.get(param_name)

    # POST: prefer JSON for app clients
    if request.is_json:
        data = request.get_json(silent=True) or {}
        value = data.get(param_name)
        if value:
            return value
        return None

    content_type = _content_type()
    if content_type in ("application/x-www-form-urlencoded", "multipart/form-data"):
        value = request.form.get(param_name)
        if value:
            return value
        return None

    if content_type in (SPARQL_QUERY_CONTENT_TYPE, SPARQL_UPDATE_CONTENT_TYPE):
        return _read_raw_body()

    # Fallbacks for non-standard clients
    value = request.args.get(param_name)
    if value:
        return value
    return _read_raw_body()


def parse_sparql_query():
    """Parse SPARQL query from request."""
    query = _parse_request_param("query")
    if not query:
        raise BadRequest("SPARQL query parameter 'query' is required")
    return query


def parse_sparql_update():
    """Parse SPARQL update from request."""
    update = _parse_request_param("update")
    if not update:
        # Compatibility for clients sending update in "query"
        update = _parse_request_param("query")
    if not update:
        raise BadRequest("SPARQL update parameter 'update' is required")
    return update

def get_query_type(query):
    """Determine the type of SPARQL query."""
    stripped = re.sub(r"(?m)#.*$", "", query).strip()
    keyword_re = re.compile(
        r"(?i)\b(prefix|base|select|construct|describe|ask|insert|delete|with|load|clear|create|drop|copy|move|add)\b"
    )
    update_keywords = {
        "INSERT",
        "DELETE",
        "WITH",
        "LOAD",
        "CLEAR",
        "CREATE",
        "DROP",
        "COPY",
        "MOVE",
        "ADD",
    }
    for match in keyword_re.finditer(stripped):
        keyword = match.group(1).upper()
        if keyword in ("PREFIX", "BASE"):
            continue
        if keyword in update_keywords:
            return "UPDATE"
        return keyword
    return "UNKNOWN"


def _get_graph_id():
    graph_id = request.args.get("graph_id")
    if not graph_id and request.is_json:
        data = request.get_json(silent=True) or {}
        graph_id = data.get("graph_id")
    if not graph_id:
        graph_id = request.form.get("graph_id")
    if not graph_id:
        default_graph = request.args.get("default-graph-uri")
        if default_graph:
            graph_id = default_graph
    return graph_id


def _serialize_select_or_ask(qres):
    supported = {
        "application/sparql-results+json": "json",
        "application/json": "json",
        "application/sparql-results+xml": "xml",
        "text/csv": "csv",
        "text/tab-separated-values": "tsv",
    }
    accept = request.accept_mimetypes
    best = accept.best_match(list(supported.keys())) if accept else None
    if not best:
        best = "application/sparql-results+json"
    result_format = supported.get(best, "json")
    serialized = qres.serialize(format=result_format)
    if isinstance(serialized, bytes):
        serialized = serialized.decode("utf-8")
    return Response(serialized, status=200, content_type=best)


def _serialize_graph_result(qres):
    graph = qres
    if isinstance(qres, Result):
        graph = qres.graph
    if graph is None:
        raise ValueError("No graph data available for CONSTRUCT/DESCRIBE result")
    supported = [
        "text/turtle",
        "application/ld+json",
        "application/rdf+xml",
        "application/n-triples",
        "application/n-quads",
    ]
    accept = request.accept_mimetypes
    best = accept.best_match(supported) if accept else None
    if not best:
        best = "text/turtle"
    format_map = {
        "text/turtle": "turtle",
        "application/ld+json": "json-ld",
        "application/rdf+xml": "xml",
        "application/n-triples": "nt",
        "application/n-quads": "nquads",
    }
    rdf_format = format_map.get(best, "turtle")
    serialized = graph.serialize(format=rdf_format)
    if isinstance(serialized, bytes):
        serialized = serialized.decode("utf-8")
    return Response(serialized, status=200, content_type=best)

@sparql_bp.route("/sparql/query", methods=["GET", "POST"])
def sparql_query_endpoint():
    """Handle SPARQL read queries (SELECT, CONSTRUCT, DESCRIBE, ASK)."""
    try:
        # Parse the SPARQL query
        query = parse_sparql_query()
        print(pyparsing.__version__)
        # Determine query type
        query_type = get_query_type(query)
        if query_type == "UPDATE":
            return jsonify({"error": "Write operations not allowed on query endpoint"}), 400
        
        # Extract graph_id from request parameters or use default
        graph_id = _get_graph_id()
        
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
        if query_type in ("SELECT", "ASK"):
            return _serialize_select_or_ask(qres)
        if query_type in ("CONSTRUCT", "DESCRIBE"):
            return _serialize_graph_result(qres)
        return jsonify({"error": "Unsupported query type"}), 400
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@sparql_bp.route("/sparql/update", methods=["POST"])
def sparql_update_endpoint():
    """Handle SPARQL update queries (INSERT, DELETE, WITH)."""
    try:
        # Parse the SPARQL query
        query = parse_sparql_update()
        
        # Determine query type
        query_type = get_query_type(query)
        if query_type != "UPDATE":
            return jsonify({"error": "Read operations not allowed on update endpoint"}), 400
        
        # Extract graph_id from request parameters or use default
        graph_id = _get_graph_id()
        
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
        return Response(status=204)
        
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
