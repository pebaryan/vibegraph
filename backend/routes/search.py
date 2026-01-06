from flask import Blueprint, request, jsonify
from models.search import WhooshSearchEngine

search_bp = Blueprint('search_bp', __name__)

# Initialize search engine
search_engine = WhooshSearchEngine(path="search_index")

# Routes for full-text search

# Search entities
@search_bp.route('/api/search', methods=['POST'])
def search_entities():
    data = request.get_json()
    query = data.get('query')
    search_by = data.get('search_by', 'iri')

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    # Execute the search
    results = search_engine.search(query, search_by)

    return jsonify(results), 200

# Get search results by ID
@search_bp.route('/api/search/<search_id>', methods=['GET'])
def get_search_result(search_id):
    # This is a simplified implementation - in a real application,
    # you would retrieve the search result by ID from a persistent storage
    # For now, we'll just return a mock result
    mock_result = {
        'search_id': search_id,
        'query': 'search for entities',
        'search_by': '',
        'results': [
            {
                'iri': 'http://example.org/entity1',
                'label': 'Entity 1',
                'properties': [
                    {'predicate': 'http://example.org/predicate1', 'object': 'http://example.org/object1'},
                    {'predicate': 'http://example.org/predicate2', 'object': 'http://example.org/object2'}
                ]
            }
        ]
    }

    return jsonify(mock_result)

    # Dump all indexed documents
    @search_bp.route('/api/search/dump', methods=['GET'])
    def dump_index():
        if not search_engine.index:
            return jsonify({'error': 'Index not created'}), 500
        results = []
        with search_engine.index.searcher() as searcher:
            for doc in searcher.documents():
                results.append(doc)
        return jsonify({'count': len(results), 'documents': results}), 200