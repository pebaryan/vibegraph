from flask import Blueprint, jsonify, request
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
        
        for row in qres:
            # Convert each row to a dict of variable name -> value
            if not qres.vars:
                vars = ['s', 'p', 'o']
                results.append({str(var): str(row[idx]) for idx,var in zip(range(3),'spo')})
            else:
                vars = qres.vars
                results.append({str(var): str(row[var]) for var in qres.vars})
        response = {"results": results, "count": len(results), "vars": vars}
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Get query history
@query_bp.route("/api/queries/history", methods=["GET"])
def get_query_history():
    # This is a simplified implementation - in a real application,
    # you would retrieve the query history from a persistent storage
    # For now, we'll just return a mock history
    mock_history = [
        {
            "query": "SELECT ?s ?p ?o WHERE { ?s ?p ?o }",
            "graph_id": "graph1",
            "timestamp": "2023-01-01T12:00:00Z",
            "results": [
                {
                    "subject": "http://example.org/subject1",
                    "predicate": "http://example.org/predicate1",
                    "object": "http://example.org/object1",
                }
            ],
        },
        {
            "query": "SELECT ?s ?p ?o WHERE { ?s ?p ?o }",
            "graph_id": "graph1",
            "timestamp": "2023-01-01T12:05:00Z",
            "results": [
                {
                    "subject": "http://example.org/subject2",
                    "predicate": "http://example.org/predicate2",
                    "object": "http://example.org/object2",
                }
            ],
        },
    ]

    return jsonify({"history": mock_history})


# Get query results by ID
@query_bp.route("/api/queries/<query_id>", methods=["GET"])
def get_query_result(query_id):
    # This is a simplified implementation - in a real application,
    # you would retrieve the query result by ID from a persistent storage
    # For now, we'll just return a mock result
    mock_result = {
        "query_id": query_id,
        "query": "SELECT ?s ?p ?o WHERE { ?s ?p ?o }",
        "graph_id": "graph1",
        "timestamp": "2023-01-01T12:00:00Z",
        "results": [
            {
                "subject": "http://example.org/subject1",
                "predicate": "http://example.org/predicate1",
                "object": "http://example.org/object1",
            }
        ],
    }

    return jsonify(mock_result)
