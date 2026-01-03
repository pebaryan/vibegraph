from whoosh.index import create_in, Index
from whoosh.fields import ID, TEXT, STORED
from whoosh.qparser import QueryParser
from whoosh.analysis import StandardTokenizer
import os
import json

# Whoosh Search Model

class WhooshSearchEngine:
    def __init__(self, path="search_index"):
        self.path = path
        self.index = None
        self.create_index()

    def create_index(self):
        """Create or open the Whoosh index"""
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        # Define the schema for the index
        schema = [
            ID("id", stored=True),
            TEXT("iri", stored=True),
            TEXT("label", stored=True),
            TEXT("properties", stored=True)
        ]

        # Create the index
        self.index = create_in(self.path, schema)

    def add_entity(self, entity):
        """Add an entity to the search index"""
        # In a real application, you would parse the RDF data to extract entities
        # and their properties

        # For demonstration purposes, we'll just add a mock entity
        mock_entity = {
            'iri': 'http://example.org/entity1',
            'label': 'Entity 1',
            'properties': [
                {'predicate': 'http://example.org/predicate1', 'object': 'http://example.org/object1'},
                {'predicate': 'http://example.org/predicate2', 'object': 'http://example.org/object2'}
            ]
        }

        # Add the entity to the index
        writer = self.index.writer()
        writer.add_document(
            id=str(uuid.uuid4()),
            iri=mock_entity['iri'],
            label=mock_entity['label'],
            properties=json.dumps(mock_entity['properties'])
        )
        writer.commit()

    def search(self, query, search_by='label'):
        """Search for entities using Whoosh"""
        # In a real application, you would parse the query and execute the search
        # against the Whoosh index

        # For demonstration purposes, we'll just return a mock result
        mock_results = [
            {
                'iri': 'http://example.org/entity1',
                'label': 'Entity 1',
                'properties': [
                    {'predicate': 'http://example.org/predicate1', 'object': 'http://example.org/object1'},
                    {'predicate': 'http://example.org/predicate2', 'object': 'http://example.org/object2'}
                ]
            },
            {
                'iri': 'http://example.org/entity2',
                'label': 'Entity 2',
                'properties': [
                    {'predicate': 'http://example.org/predicate3', 'object': 'http://example.org/object3'}
                ]
            }
        ]

        return {
            'query': query,
            'search_by': search_by,
            'results': mock_results,
            'count': len(mock_results)
        }

    def get_results(self, query, search_by='label'):
        """Get search results for a query"""
        if not self.index:
            return {'error': 'Index not created'}

        # Parse the query
        parser = QueryParser("label", schema=self.index.schema)
        query_obj = parser.parse(query)

        # Execute the search
        with self.index.searcher() as searcher:
            results = searcher.search(query_obj)

            # Convert results to a list of dictionaries
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'iri': result['iri'],
                    'label': result['label'],
                    'properties': json.loads(result['properties'])
                })

            return {
                'query': query,
                'search_by': search_by,
                'results': formatted_results,
                'count': len(formatted_results)
            }