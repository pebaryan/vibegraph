"""
Utility functions for VibeGraph application.
Provides common functions and operations used across the backend.
"""

from uuid import uuid4
from datetime import datetime
from flask import jsonify
from config import GRAPH_DATA_FILE, GRAPHS_DATA_DIR


def get_graph_metadata(graph_manager, graph_id):
    """
    Retrieve graph metadata with error handling.
    """
    try:
        graph = graph_manager.get_graph(graph_id)
        if not graph:
            return None, jsonify({"error": "Graph not found"}), 404
        return graph, None, None
    except Exception as e:
        return None, jsonify({"error": str(e)}), 500


def get_graph_object(graph_manager, graph_id):
    """
    Retrieve graph object with error handling.
    """
    try:
        graph_obj = graph_manager.get_graph_object(graph_id)
        if not graph_obj:
            return None, jsonify({"error": "Graph not found"}), 404
        return graph_obj, None, None
    except Exception as e:
        return None, jsonify({"error": str(e)}), 500


def save_graph_changes(graph_manager):
    """
    Save graph changes with error handling.
    """
    try:
        graph_manager._save()
        return True, None
    except Exception as e:
        return False, jsonify({"error": str(e)}), 500


def create_graph_metadata(
    name, sparql_read=None, sparql_update=None, auth_type="None", auth_info=None
):
    """
    Create graph metadata dictionary.
    """
    graph_id = str(uuid4())
    created_at = datetime.now().isoformat()

    return {
        "graph_id": graph_id,
        "name": name,
        "created_at": created_at,
        "sparql_read": sparql_read,
        "sparql_update": sparql_update,
        "auth_type": auth_type,
        "auth_info": auth_info,
    }


def validate_graph_id_format(graph_id):
    """
    Validate that a graph_id has the correct format.
    """
    # Basic validation - could be expanded
    if not graph_id or not isinstance(graph_id, str):
        return False
    return True
