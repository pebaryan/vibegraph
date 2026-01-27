"""
SPARQL Endpoint for VibeGraph
This module provides a SPARQL endpoint that allows querying RDF data through the SPARQL protocol.
"""

from flask import Blueprint, jsonify
from werkzeug.exceptions import BadRequest
from routes.sparql_enhanced import (
    parse_sparql_query,
    parse_sparql_update,
    get_query_type,
    sparql_query_endpoint,
    sparql_update_endpoint,
    sparql_info,
    sparql_options,
)

# Create SPARQL blueprint
sparql_bp = Blueprint("sparql_bp", __name__)

@sparql_bp.route("/sparql", methods=["GET", "POST"])
def sparql_endpoint():
    """Handle SPARQL queries (proxy to enhanced implementation)."""
    try:
        # Prefer explicit UPDATE parsing if present
        try:
            update = parse_sparql_update()
            if get_query_type(update) == "UPDATE":
                return sparql_update_endpoint()
        except BadRequest:
            pass

        query = parse_sparql_query()
        if get_query_type(query) == "UPDATE":
            return sparql_update_endpoint()
        return sparql_query_endpoint()
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@sparql_bp.route("/sparql/query", methods=["GET", "POST"])
def sparql_query_proxy():
    """Proxy to enhanced SPARQL read endpoint."""
    return sparql_query_endpoint()


@sparql_bp.route("/sparql/update", methods=["POST"])
def sparql_update_proxy():
    """Proxy to enhanced SPARQL update endpoint."""
    return sparql_update_endpoint()


@sparql_bp.route("/sparql/info", methods=["GET"])
def sparql_info_proxy():
    """Proxy to enhanced SPARQL info endpoint."""
    return sparql_info()


@sparql_bp.route("/sparql", methods=["OPTIONS"])
def sparql_options_proxy():
    """Proxy to enhanced SPARQL options endpoint."""
    return sparql_options()
