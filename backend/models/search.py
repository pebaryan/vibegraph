from whoosh.index import create_in, open_dir
from whoosh.fields import ID, TEXT, STORED, Schema
from whoosh.qparser import QueryParser
from whoosh.analysis import StandardAnalyzer
import os
import json
import uuid

# Whoosh Search Model

class WhooshSearchEngine:
    def __init__(self, path="search_index"):
        self.path = path
        self.index = None
        self.create_index()

    def create_index(self):
        """Create or open the Whoosh index and ensure it is persisted."""
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        # If the index directory already contains an index, open it
        if os.listdir(self.path):
            try:
                self.index = open_dir(self.path)
                return
            except Exception:
                pass

        # Define the schema for the index
        schema = Schema(
            id=ID(stored=True),
            iri=TEXT(stored=True),
            label=TEXT(stored=True),
        )

        # Create the index on disk
        self.index = create_in(self.path, schema)

    def add_entity(self, entity):
        """Add an entity to the search index"""
        # entity is expected to be a dict with keys: iri, label, properties (list of dicts)
        writer = self.index.writer()
        writer.add_document(
            id=str(uuid.uuid4()),
            iri=entity.get("iri", ""),
            label=entity.get("label", "")
        )
        writer.commit()

    def search(self, query, search_by="label"):
        """Search for entities using Whoosh"""
        # In a real application, you would parse the query and execute the search
        # against the Whoosh index

        # For demonstration purposes, we'll just return a mock result
        mock_results = [
            {
                "iri": "http://example.org/entity1",
                "label": "Entity 1",
                "properties": [
                    {
                        "predicate": "http://example.org/predicate1",
                        "object": "http://example.org/object1",
                    },
                    {
                        "predicate": "http://example.org/predicate2",
                        "object": "http://example.org/object2",
                    },
                ],
            },
            {
                "iri": "http://example.org/entity2",
                "label": "Entity 2",
                "properties": [
                    {
                        "predicate": "http://example.org/predicate3",
                        "object": "http://example.org/object3",
                    }
                ],
            },
        ]
        mock_results = self.get_results(query, search_by)

        return {
            "query": query,
            "search_by": search_by,
            "results": mock_results,
            "count": len(mock_results),
        }

    def get_results(self, query, search_by="label"):
        """Get search results for a query"""
        if not self.index:
            return {"error": "Index not created"}

        # Parse the query
        parser = QueryParser("label", schema=self.index.schema)
        query_obj = parser.parse(query)

        # Execute the search
        with self.index.searcher() as searcher:
            results = searcher.search(query_obj)

            # Convert results to a list of dictionaries
            formatted_results = []
            for result in results:
                formatted_results.append(
                    {
                        "iri": result["iri"],
                        "label": result["label"],
                    }
                )

            return {
                "query": query,
                "search_by": search_by,
                "results": formatted_results,
                "count": len(formatted_results),
            }
