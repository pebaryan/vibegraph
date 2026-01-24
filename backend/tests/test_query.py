import pytest
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.query import SPARQLQueryProcessor


# Test SPARQLQueryProcessor class
class TestSPARQLQueryProcessor:
    """Test suite for SPARQLQueryProcessor"""

    def setup_method(self):
        """Setup test environment"""
        self.processor = SPARQLQueryProcessor()

    def test_init(self):
        """Test SPARQLQueryProcessor initialization"""
        assert self.processor.graph is not None
        assert isinstance(self.processor.query_results, dict)
        assert len(self.processor.query_results) == 0

    def test_execute_query_success(self):
        """Test successful query execution"""
        query = "SELECT * WHERE { ?s ?p ?o }"
        graph_id = "test-graph"

        result = self.processor.execute_query(query, graph_id)

        assert isinstance(result, dict)
        assert "query" in result
        assert result["query"] == query
        assert "results" in result
        assert isinstance(result["results"], list)
        assert "count" in result
        assert result["count"] == 2  # Based on mock implementation

    def test_execute_query_with_complex_query(self):
        """Test query execution with complex SPARQL"""
        complex_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT ?subject ?predicate ?object
        WHERE {
            ?subject ?predicate ?object .
            FILTER(?object != "test")
        }
        LIMIT 10
        """
        graph_id = "complex-graph"

        result = self.processor.execute_query(complex_query, graph_id)

        assert isinstance(result, dict)
        assert result["query"] == complex_query
        assert len(result["results"]) == 2  # Mock returns 2 results
        assert result["count"] == 2

    def test_execute_query_empty_query(self):
        """Test query execution with empty query"""
        result = self.processor.execute_query("", "test-graph")

        assert isinstance(result, dict)
        assert result["query"] == ""
        assert "results" in result
        assert "count" in result

    def test_execute_query_none_query(self):
        """Test query execution with None query"""
        result = self.processor.execute_query(None, "test-graph")

        assert isinstance(result, dict)
        assert result["query"] is None
        assert "results" in result

    def test_execute_query_different_graph_ids(self):
        """Test query execution with different graph IDs"""
        query = "SELECT * WHERE { ?s ?p ?o }"
        graph_ids = ["graph1", "graph2", "graph3"]

        for graph_id in graph_ids:
            result = self.processor.execute_query(query, graph_id)
            assert isinstance(result, dict)
            assert "query" in result
            assert "results" in result
            # Mock implementation doesn't use graph_id, but it should accept the parameter

    def test_execute_query_result_structure(self):
        """Test that execute_query returns expected result structure"""
        query = "SELECT * WHERE { ?s ?p ?o }"
        result = self.processor.execute_query(query, "test-graph")

        # Check result structure
        required_keys = ["query", "results", "count"]
        for key in required_keys:
            assert key in result

        # Check results structure
        if len(result["results"]) > 0:
            first_result = result["results"][0]
            result_keys = ["subject", "predicate", "object"]
            for key in result_keys:
                assert key in first_result

    def test_execute_query_result_content(self):
        """Test content of mock query results"""
        query = "SELECT * WHERE { ?s ?p ?o }"
        result = self.processor.execute_query(query, "test-graph")

        # Check mock result content
        assert len(result["results"]) == 2

        # Check first result
        first_result = result["results"][0]
        assert first_result["subject"] == "http://example.org/subject1"
        assert first_result["predicate"] == "http://example.org/predicate1"
        assert first_result["object"] == "http://example.org/object1"

        # Check second result
        second_result = result["results"][1]
        assert second_result["subject"] == "http://example.org/subject2"
        assert second_result["predicate"] == "http://example.org/predicate2"
        assert second_result["object"] == "http://example.org/object2"

    def test_graph_attribute_type(self):
        """Test that graph attribute is correct type"""
        assert hasattr(self.processor, "graph")
        # Should be an RDFLib Graph instance
        from rdflib import Graph

        assert isinstance(self.processor.graph, Graph)

    def test_query_results_attribute_type(self):
        """Test that query_results attribute is correct type"""
        assert hasattr(self.processor, "query_results")
        assert isinstance(self.processor.query_results, dict)

    def test_multiple_execute_queries(self):
        """Test executing multiple queries sequentially"""
        queries = [
            "SELECT * WHERE { ?s ?p ?o } LIMIT 1",
            "SELECT ?s WHERE { ?s ?p ?o }",
            "SELECT ?p WHERE { ?s ?p ?o }",
        ]

        results = []
        for query in queries:
            result = self.processor.execute_query(query, "test-graph")
            results.append(result)
            assert isinstance(result, dict)
            assert "query" in result
            assert "results" in result

        # All queries should return mock results
        for result in results:
            assert result["count"] == 2  # Mock implementation returns 2

    def test_concurrent_queries(self):
        """Test that processor can handle multiple different queries"""
        query1 = "SELECT ?s WHERE { ?s ?p ?o }"
        query2 = "SELECT ?p WHERE { ?s ?p ?o }"

        result1 = self.processor.execute_query(query1, "graph1")
        result2 = self.processor.execute_query(query2, "graph2")

        assert result1["query"] == query1
        assert result2["query"] == query2
        assert result1["count"] == result2["count"] == 2

    def test_query_parameter_types(self):
        """Test query execution with different parameter types"""
        test_cases = [
            ("string query", "string-graph"),
            ("", "empty-graph"),
            (None, "none-graph"),
            ("SELECT * WHERE { ?s ?p ?o }", 123),  # Non-string graph_id
        ]

        for query, graph_id in test_cases:
            result = self.processor.execute_query(query, graph_id)
            assert isinstance(result, dict)
            # Should handle various input types gracefully
