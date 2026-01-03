from flask import jsonify, request
from backend.models.query import SPARQLQueryProcessor

# Initialize SPARQL query processor
sparql_processor = SPARQLQueryProcessor()

# Routes for SPARQL query interface
# Execute a SPARQL query
@app.route('/api/queries', methods=['POST'])
def execute_query():
    data = request.get_json()
    query = data.get('query')
    graph_id = data.get('graph_id')

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    if not graph_id:
        return jsonify({'error': 'Graph ID is required'}), 400

    # Execute the query
    result = sparql_processor.execute_query(query, graph_id)

    # Format the results for display
    formatted_result = sparql_processor.format_results(result)

    return jsonify(formatted_result), 200

# Get query history
@app.route('/api/queries/history', methods=['GET'])
def get_query_history():
    # This is a simplified implementation - in a real application,
    # you would retrieve the query history from a persistent storage
    # For now, we'll just return a mock history
    mock_history = [
        {
            'query': 'SELECT ?s ?p ?o WHERE { ?s ?p ?o }',
            'graph_id': 'graph1',
            'timestamp': '2023-01-01T12:00:00Z',
            'results': [
                {'subject': 'http://example.org/subject1', 'predicate': 'http://example.org/predicate1', 'object': 'http://example.org/object1'}
            ]
        },
        {
            'query': 'SELECT ?s ?p ?o WHERE { ?s ?p ?o }',
            'graph_id': 'graph1',
            'timestamp': '2023-01-01T12:05:00Z',
            'results': [
                {'subject': 'http://example.org/subject2', 'predicate': 'http://example.org/predicate2', 'object': 'http://example.org/object2'}
            ]
        }
    ]

    return jsonify({'history': mock_history})

# Get query results by ID
@app.route('/api/queries/<query_id>', methods=['GET'])
def get_query_result(query_id):
    # This is a simplified implementation - in a real application,
    # you would retrieve the query result by ID from a persistent storage
    # For now, we'll just return a mock result
    mock_result = {
        'query_id': query_id,
        'query': 'SELECT ?s ?p ?o WHERE { ?s ?p ?o }',
        'graph_id': 'graph1',
        'timestamp': '2023-01-01T12:00:00Z',
        'results': [
            {'subject': 'http://example.org/subject1', 'predicate': 'http://example.org/predicate1', 'object': 'http://example.org/object1'}
        ]
    }

    return jsonify(mock_result)