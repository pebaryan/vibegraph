from flask import Blueprint, request, jsonify
from models.search import WhooshSearchEngine

search_bp = Blueprint("search_bp", __name__)

# Initialize search engine
search_engine = WhooshSearchEngine(path="search_index")

# Routes for full-text search


# Search entities
@search_bp.route("/api/search", methods=["POST"])
def search_entities():
    data = request.get_json()
    query = data.get("query")
    search_by = data.get("search_by", "label")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    # Execute the search
    results = search_engine.search(query, search_by)

    return jsonify(results), 200


# Dump all indexed documents
@search_bp.route("/api/search/dump", methods=["GET"])
def dump_index():
    if not search_engine.index:
        return jsonify({"error": "Index not created"}), 500
    results = []
    lexicon = {}
    with search_engine.index.searcher() as searcher:
        for doc in searcher.documents():
            results.append(doc)
        lexicon["iri"] = list(searcher.lexicon("iri"))
        lexicon["label"] = list(searcher.lexicon("label"))
    print(lexicon)
    return (
        jsonify({"count": len(results), "documents": results}),
        200,
    )
