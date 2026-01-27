import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app
from routes.graphs import graph_manager


# Test Graph Routes
class TestGraphRoutes:
    """Test suite for graph management routes"""

    def setup_method(self):
        """Setup test client and mock data"""
        self.app = app.test_client()
        self.app.testing = True
        # Clear any existing graphs for clean testing
        self.existing_graphs = graph_manager.list_graphs()

    def test_create_graph_success(self):
        """Test successful graph creation"""
        graph_data = {"name": "Test Graph"}

        response = self.app.post(
            "/api/graphs", data=json.dumps(graph_data), content_type="application/json"
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert "graph_id" in data
        assert data["name"] == "Test Graph"

    def test_create_graph_with_sparql(self):
        """Test graph creation with SPARQL configuration"""
        graph_data = {
            "name": "SPARQL Graph",
            "sparql_read": "http://example.com/read",
            "sparql_update": "http://example.com/update",
            "auth_type": "Basic",
            "auth_info": {"username": "user", "password": "pass"},
        }

        response = self.app.post(
            "/api/graphs", data=json.dumps(graph_data), content_type="application/json"
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["name"] == "SPARQL Graph"
        assert data["sparql_read"] == "http://example.com/read"

    def test_create_graph_missing_name(self):
        """Test graph creation with missing name"""
        graph_data = {}

        response = self.app.post(
            "/api/graphs", data=json.dumps(graph_data), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Name is required" in data["error"]

    def test_create_graph_invalid_json(self):
        """Test graph creation with invalid JSON"""
        response = self.app.post(
            "/api/graphs", data="invalid json", content_type="application/json"
        )

        assert response.status_code == 400

    def test_list_graphs(self):
        """Test listing all graphs"""
        response = self.app.get("/api/graphs")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_triples_success(self):
        """Test getting triples for existing graph"""
        # First create a graph
        graph_data = {"name": "Test Graph for Triples"}
        create_response = self.app.post(
            "/api/graphs", data=json.dumps(graph_data), content_type="application/json"
        )
        created_graph = json.loads(create_response.data)
        graph_id = created_graph["graph_id"]

        # Get triples for the graph
        response = self.app.get(f"/api/graphs/{graph_id}/triples")

        # Should return 200 or handle gracefully if graph has no triples
        assert response.status_code in [200, 400]

    def test_get_triples_nonexistent_graph(self):
        """Test getting triples for non-existent graph"""
        fake_graph_id = "nonexistent-graph-id"
        response = self.app.get(f"/api/graphs/{fake_graph_id}/triples")

        # Should handle error gracefully
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    @patch("routes.graphs.graph_manager")
    def test_get_triples_exception(self, mock_manager):
        """Test get triples when exception occurs"""
        # Make the manager raise an exception
        mock_manager.get_triples.side_effect = Exception("Test error")

        response = self.app.get("/api/graphs/test-id/triples")

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert "Test error" in data["error"]

    def test_graph_blueprint_registered(self):
        """Test that graph blueprint is properly registered"""
        # Check if graph_bp is registered in the app
        blueprint_names = [bp.name for bp in app.blueprints.values()]
        assert "graph_bp" in blueprint_names

    def test_create_graph_route_methods(self):
        """Test that routes accept correct HTTP methods"""
        # Test POST on /api/graphs
        response = self.app.post("/api/graphs")
        # Will fail due to missing data, but should not be 405 (Method Not Allowed)
        assert response.status_code != 405

        # Test GET on /api/graphs
        response = self.app.get("/api/graphs")
        assert response.status_code == 200

        # Test unsupported method
        response = self.app.put("/api/graphs")
        assert response.status_code == 405

    def test_list_graphs_with_existing_data(self):
        """Test listing graphs when graphs exist"""
        # Create a graph first
        graph_data = {"name": "Existing Graph"}
        self.app.post(
            "/api/graphs", data=json.dumps(graph_data), content_type="application/json"
        )

        # List graphs
        response = self.app.get("/api/graphs")

        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert any(g["name"] == "Existing Graph" for g in data)

    def test_create_graph_with_optional_params(self):
        """Test graph creation with various optional parameters"""
        # Test with minimal required params
        minimal_data = {"name": "Minimal Graph"}
        response = self.app.post(
            "/api/graphs",
            data=json.dumps(minimal_data),
            content_type="application/json",
        )
        assert response.status_code == 201

        # Test with all optional params as None
        full_data = {
            "name": "Full Params Graph",
            "sparql_read": None,
            "sparql_update": None,
            "auth_type": "None",
            "auth_info": None,
        }
        response = self.app.post(
            "/api/graphs", data=json.dumps(full_data), content_type="application/json"
        )
        assert response.status_code == 201

    def test_error_responses_format(self):
        """Test that error responses follow consistent format"""
        # Test missing name error
        response = self.app.post(
            "/api/graphs", data=json.dumps({}), content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
        assert isinstance(data["error"], str)

    def test_success_responses_format(self):
        """Test that success responses follow consistent format"""
        # Test successful creation response
        graph_data = {"name": "Format Test Graph"}
        response = self.app.post(
            "/api/graphs", data=json.dumps(graph_data), content_type="application/json"
        )

        assert response.status_code == 201
        data = json.loads(response.data)
        # Should contain expected fields
        expected_fields = ["graph_id", "name", "created_at", "auth_type"]
        for field in expected_fields:
            assert field in data

    def test_clear_all_graphs(self):
        """Test clearing all graphs"""
        graph_data = {"name": "Clear All Graph"}
        self.app.post(
            "/api/graphs", data=json.dumps(graph_data), content_type="application/json"
        )

        response = self.app.post(
            "/api/graphs/clear",
            data=json.dumps({"clear_history": True, "clear_index": True}),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get("cleared_history") is True
        assert data.get("cleared_index") is True

        list_response = self.app.get("/api/graphs")
        assert list_response.status_code == 200
        graphs = json.loads(list_response.data)
        assert graphs == []
