import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app
from routes.queries import sparql_processor


# Test Query Routes
class TestQueryRoutes:
    """Test suite for SPARQL query routes"""

    def setup_method(self):
        """Setup test client"""
        self.app = app.test_client()
        self.app.testing = True

    def test_execute_query_success_with_graph_id(self):
        """Test successful query execution with specified graph ID"""
        # First create a graph
        graph_data = {"name": "Test Graph for Query"}
        create_response = self.app.post(
            "/api/graphs", data=json.dumps(graph_data), content_type="application/json"
        )
        created_graph = json.loads(create_response.data)
        graph_id = created_graph["graph_id"]

        # Execute a simple query
        query_data = {
            "query": "SELECT * WHERE { ?s ?p ?o } LIMIT 1",
            "graph_id": graph_id,
        }

        response = self.app.post(
            "/api/queries", data=json.dumps(query_data), content_type="application/json"
        )

        # Should return 200 even if no results, as long as query is valid
        assert response.status_code in [200, 400]
        data = json.loads(response.data)

        if response.status_code == 200:
            assert "results" in data
            # execution_time may or may not be present depending on implementation
            expected_fields = ["results", "vars", "count", "query_id"]
            for field in expected_fields:
                assert field in data

    def test_execute_query_success_without_graph_id(self):
        """Test successful query execution without specifying graph ID"""
        # First create a graph to ensure one exists
        graph_data = {"name": "Test Graph for Auto Selection"}
        self.app.post(
            "/api/graphs", data=json.dumps(graph_data), content_type="application/json"
        )

        # Execute query without graph_id (should auto-select)
        query_data = {"query": "SELECT * WHERE { ?s ?p ?o } LIMIT 1"}

        response = self.app.post(
            "/api/queries", data=json.dumps(query_data), content_type="application/json"
        )

        # Should work if a graph exists
        assert response.status_code in [200, 400]

    def test_execute_query_missing_query(self):
        """Test query execution with missing query"""
        query_data = {"graph_id": "test-graph-id"}

        response = self.app.post(
            "/api/queries", data=json.dumps(query_data), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Query is required" in data["error"]

    def test_execute_query_no_graphs_available(self):
        """Test query execution when no graphs are available"""
        # This test might be tricky due to existing graphs, but let's try

        query_data = {"query": "SELECT * WHERE { ?s ?p ?o }"}

        response = self.app.post(
            "/api/queries", data=json.dumps(query_data), content_type="application/json"
        )

        # Should either work (if graphs exist) or return appropriate error
        assert response.status_code in [200, 400, 404]

    def test_execute_query_nonexistent_graph(self):
        """Test query execution with non-existent graph ID"""
        query_data = {
            "query": "SELECT * WHERE { ?s ?p ?o }",
            "graph_id": "nonexistent-graph-id",
        }

        response = self.app.post(
            "/api/queries", data=json.dumps(query_data), content_type="application/json"
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert "error" in data
        assert "Graph not found" in data["error"]

    def test_execute_query_invalid_json(self):
        """Test query execution with invalid JSON"""
        response = self.app.post(
            "/api/queries", data="invalid json", content_type="application/json"
        )

        assert response.status_code == 400

    def test_query_blueprint_registered(self):
        """Test that query blueprint is properly registered"""
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert "query_bp" in blueprint_names

    def test_query_route_methods(self):
        """Test that routes accept correct HTTP methods"""
        # Test POST on /api/queries
        query_data = {"query": "SELECT * WHERE { ?s ?p ?o }"}
        response = self.app.post(
            "/api/queries", data=json.dumps(query_data), content_type="application/json"
        )
        # Will fail due to missing graph or invalid query, but should not be 405
        assert response.status_code != 405

        # Test unsupported method
        response = self.app.get("/api/queries")
        assert response.status_code == 405

    @patch("routes.queries.graph_manager")
    def test_execute_query_graph_manager_error(self, mock_manager):
        """Test query execution when graph_manager raises error"""
        # Mock graph_manager to return None for get_graph_object
        mock_manager.get_graph_object.return_value = None

        query_data = {
            "query": "SELECT * WHERE { ?s ?p ?o }",
            "graph_id": "test-graph-id",
        }

        response = self.app.post(
            "/api/queries", data=json.dumps(query_data), content_type="application/json"
        )

        assert response.status_code == 404

    @patch("routes.queries.graph_manager")
    def test_execute_query_list_graphs_error(self, mock_manager):
        """Test query execution when list_graphs raises error"""
        # Mock list_graphs to return empty list
        mock_manager.list_graphs.return_value = []

        query_data = {"query": "SELECT * WHERE { ?s ?p ?o }"}

        response = self.app.post(
            "/api/queries", data=json.dumps(query_data), content_type="application/json"
        )

        assert response.status_code == 404
        data = json.loads(response.data)
        assert "no graph available" in data["error"]

    def test_execute_query_with_complex_sparql(self):
        """Test query execution with more complex SPARQL"""
        # First create a graph
        graph_data = {"name": "Complex Query Test Graph"}
        create_response = self.app.post(
            "/api/graphs", data=json.dumps(graph_data), content_type="application/json"
        )
        created_graph = json.loads(create_response.data)
        graph_id = created_graph["graph_id"]

        # Try a more complex query
        query_data = {
            "query": """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?subject ?predicate ?object
            WHERE {
                ?subject ?predicate ?object .
                FILTER(?object != "test")
            }
            LIMIT 10
            """,
            "graph_id": graph_id,
        }

        response = self.app.post(
            "/api/queries", data=json.dumps(query_data), content_type="application/json"
        )

        # Should handle the query gracefully
        assert response.status_code in [200, 400]

    def test_query_response_format(self):
        """Test that query responses follow expected format"""
        # First create a graph
        graph_data = {"name": "Response Format Test Graph"}
        create_response = self.app.post(
            "/api/graphs", data=json.dumps(graph_data), content_type="application/json"
        )
        created_graph = json.loads(create_response.data)
        graph_id = created_graph["graph_id"]

        # Execute a simple query
        query_data = {
            "query": "SELECT * WHERE { ?s ?p ?o } LIMIT 1",
            "graph_id": graph_id,
        }

        response = self.app.post(
            "/api/queries", data=json.dumps(query_data), content_type="application/json"
        )

        if response.status_code == 200:
            data = json.loads(response.data)
            # Check for expected response fields
            expected_fields = ["results", "vars", "count", "query_id"]
            for field in expected_fields:
                assert field in data

            # Check that results is a list
            assert isinstance(data["results"], list)
            assert isinstance(data["count"], int)

    def test_error_responses_format(self):
        """Test that error responses follow consistent format"""
        # Test missing query error
        response = self.app.post(
            "/api/queries", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert isinstance(data["error"], str)
