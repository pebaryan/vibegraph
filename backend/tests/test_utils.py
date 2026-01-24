import pytest
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app
from utils import (
    get_graph_metadata,
    get_graph_object,
    save_graph_changes,
    create_graph_metadata,
    validate_graph_id_format,
)


# Dummy graph_manager with minimal interface
class DummyGraphManager:
    def __init__(self, should_fail=False, graph_exists=False):
        self.should_fail = should_fail
        self.graph_exists = graph_exists

    def get_graph(self, graph_id):
        if self.should_fail:
            raise Exception("Test error")
        return {"id": graph_id} if self.graph_exists else None

    def get_graph_object(self, graph_id):
        if self.should_fail:
            raise Exception("Test error")
        return {"object": graph_id} if self.graph_exists else None

    def _save(self):
        if self.should_fail:
            raise Exception("Save error")


# Test get_graph_metadata - graph not found
def test_get_graph_metadata_not_found():
    gm = DummyGraphManager(graph_exists=False)
    with app.app_context():
        graph, err_resp, status = get_graph_metadata(gm, "nonexistent")
    assert graph is None
    assert status == 404
    assert err_resp is not None


# Test get_graph_metadata - graph found
def test_get_graph_metadata_found():
    gm = DummyGraphManager(graph_exists=True)
    with app.app_context():
        graph, err_resp, status = get_graph_metadata(gm, "existing")
    assert graph is not None
    assert err_resp is None
    assert status is None


# Test get_graph_metadata - exception handling
def test_get_graph_metadata_exception():
    gm = DummyGraphManager(should_fail=True)
    with app.app_context():
        graph, err_resp, status = get_graph_metadata(gm, "test")
    assert graph is None
    assert status == 500
    assert err_resp is not None


# Test get_graph_object - object not found
def test_get_graph_object_not_found():
    gm = DummyGraphManager(graph_exists=False)
    with app.app_context():
        obj, err_resp, status = get_graph_object(gm, "nonexistent")
    assert obj is None
    assert status == 404
    assert err_resp is not None


# Test get_graph_object - object found
def test_get_graph_object_found():
    gm = DummyGraphManager(graph_exists=True)
    with app.app_context():
        obj, err_resp, status = get_graph_object(gm, "existing")
    assert obj is not None
    assert err_resp is None
    assert status is None


# Test get_graph_object - exception handling
def test_get_graph_object_exception():
    gm = DummyGraphManager(should_fail=True)
    with app.app_context():
        obj, err_resp, status = get_graph_object(gm, "test")
    assert obj is None
    assert status == 500
    assert err_resp is not None


# Test save_graph_changes - success
def test_save_graph_changes_success():
    gm = DummyGraphManager(should_fail=False)
    result = save_graph_changes(gm)
    assert result[0] is True  # success flag
    assert len(result) == 2  # only success flag and None
    assert result[1] is None


# Test save_graph_changes - failure
def test_save_graph_changes_failure():
    gm = DummyGraphManager(should_fail=True)
    with app.app_context():
        result = save_graph_changes(gm)
        assert result[0] is False  # success flag
        assert len(result) == 3  # tuple with success, error response, and status
        assert result[2] == 500  # status code


# Test create_graph_metadata with minimal parameters
def test_create_graph_metadata_minimal():
    metadata = create_graph_metadata("Test Graph")

    assert metadata["name"] == "Test Graph"
    assert "graph_id" in metadata
    assert "created_at" in metadata
    assert metadata["sparql_read"] is None
    assert metadata["sparql_update"] is None
    assert metadata["auth_type"] == "None"
    assert metadata["auth_info"] is None


# Test create_graph_metadata with all parameters
def test_create_graph_metadata_full():
    metadata = create_graph_metadata(
        name="Full Graph",
        sparql_read="http://example.com/read",
        sparql_update="http://example.com/update",
        auth_type="Basic",
        auth_info={"username": "user", "password": "pass"},
    )

    assert metadata["name"] == "Full Graph"
    assert metadata["sparql_read"] == "http://example.com/read"
    assert metadata["sparql_update"] == "http://example.com/update"
    assert metadata["auth_type"] == "Basic"
    assert metadata["auth_info"] == {"username": "user", "password": "pass"}
    assert len(metadata["graph_id"]) > 0


# Test validate_graph_id_format - valid cases
def test_validate_graph_id_format_valid():
    assert validate_graph_id_format("a-b-c")
    assert validate_graph_id_format("123")
    assert validate_graph_id_format("graph-id")
    # Empty string doesn't pass the basic validation in the actual implementation


# Test validate_graph_id_format - invalid cases
def test_validate_graph_id_format_invalid():
    assert not validate_graph_id_format(None)
    assert not validate_graph_id_format(123)
    assert not validate_graph_id_format([])
    assert not validate_graph_id_format({})
