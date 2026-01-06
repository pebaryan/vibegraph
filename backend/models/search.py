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
            iri=ID(stored=True, unique=True, sortable=True),
            label=TEXT(stored=True, ),
            graph_id=ID(stored=True),
        )

        # Create the index on disk
        self.index = create_in(self.path, schema)

    def add_entity(self, entity):
        """Add an entity to the search index"""
        # entity is expected to be a dict with keys: iri, label, properties (list of dicts)
        writer = self.index.writer()
        writer.update_document(
            iri=entity.get("iri", ""),
            label=entity.get("label", ""),
            graph_id=entity.get("graph_id", ""),
        )
        writer.commit()

    def search(self, query, search_by="iri"):
        """Search for entities using Whoosh"""
        # In a real application, you would parse the query and execute the search
        # against the Whoosh index

        return self.get_results(query, search_by)

    def get_results(self, query, search_by="iri"):
        """Get search results for a query"""
        if not self.index:
            return {"error": "Index not created"}

        # Parse the query
        parser = QueryParser(search_by, schema=self.index.schema)
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
                        "graph_id": result["graph_id"],
                    }
                )

            return {
                "query": query,
                "search_by": search_by,
                "results": formatted_results,
                "count": len(formatted_results),
            }
