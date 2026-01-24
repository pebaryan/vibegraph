import pytest
import sys
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.graph import (
    Graph,
    GraphManager,
    save_prefixes,
    load_global_prefixes,
    NS_PREFIXES,
)


# Test Graph class initialization
def test_graph_init_basic():
    """Test basic Graph initialization"""
    graph = Graph("test-id", "Test Graph", "2023-01-01")

    assert graph.graph_id == "test-id"
    assert graph.name == "Test Graph"
    assert graph.created_at == "2023-01-01"
    assert graph.data == {}
    assert graph.sparql_read is None
    assert graph.sparql_update is None
    assert graph.auth_type == "None"
    assert graph.auth_info is None


def test_graph_init_with_sparql():
    """Test Graph initialization with SPARQL configuration"""
    graph = Graph(
        "test-id",
        "Test Graph",
        "2023-01-01",
        sparql_read="http://example.com/read",
        sparql_update="http://example.com/update",
        auth_type="Basic",
        auth_info={"username": "user", "password": "pass"},
    )

    assert graph.sparql_read == "http://example.com/read"
    assert graph.sparql_update == "http://example.com/update"
    assert graph.auth_type == "Basic"
    assert graph.auth_info == {"username": "user", "password": "pass"}


def test_graph_to_dict():
    """Test Graph to_dict method"""
    graph = Graph("test-id", "Test Graph", "2023-01-01")
    result = graph.to_dict()

    expected = {
        "graph_id": "test-id",
        "name": "Test Graph",
        "created_at": "2023-01-01",
        "data": {},
        "sparql_read": None,
        "sparql_update": None,
        "auth_type": "None",
        "auth_info": None,
    }

    assert result == expected


def test_graph_serialize():
    """Test Graph serialize method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        graph = Graph("test-id", "Test Graph", "2023-01-01")
        graph.serialize(temp_dir)

        expected_file = os.path.join(temp_dir, "test-id.ttl")
        assert os.path.exists(expected_file)


def test_graph_add_triple():
    """Test Graph add_triple method"""
    graph = Graph("test-id", "Test Graph", "2023-01-01")

    # Test adding a simple triple
    triple = ("subject", "predicate", "object")
    graph.add_triple(triple)

    # Verify the triple was added
    triples = list(graph.graph)
    assert len(triples) > 0


def test_graph_wrap_subject():
    """Test Graph wrap method for subjects"""
    graph = Graph("test-id", "Test Graph", "2023-01-01")

    # Test blank node
    result = graph.wrap("_:blank1", "s")
    assert "blank1" in str(result)

    # Test URI
    result = graph.wrap("http://example.com/subject", "s")
    assert "http://example.com/subject" in str(result)

    # Test prefixed URI
    result = graph.wrap("rdf:type", "s")
    assert "rdf" in str(result) or "type" in str(result)


def test_graph_wrap_predicate():
    """Test Graph wrap method for predicates"""
    from rdflib import RDF

    graph = Graph("test-id", "Test Graph", "2023-01-01")

    # Test 'a' shortcut for rdf:type
    result = graph.wrap("a", "p")
    assert str(result) == str(RDF.type)

    # Test URI
    result = graph.wrap("http://example.com/predicate", "p")
    assert "http://example.com/predicate" in str(result)


def test_graph_wrap_object():
    """Test Graph wrap method for objects"""
    graph = Graph("test-id", "Test Graph", "2023-01-01")

    # Test blank node
    result = graph.wrap("_:blank1", "o")
    assert "blank1" in str(result)

    # Test literal
    result = graph.wrap("literal string", "o")
    assert "literal string" in str(result)


@patch("models.graph.print")
def test_graph_index(mock_print):
    """Test Graph index method"""
    graph = Graph("test-id", "Test Graph", "2023-01-01")

    # Add some triples to index
    graph.add_triple(("subject1", "predicate1", "object1"))
    graph.add_triple(("subject2", "predicate2", "object2"))

    # Mock search engine
    mock_search_engine = MagicMock()

    graph.index(mock_search_engine, "test-id")

    # Verify search engine was called
    assert mock_search_engine.add_entity.call_count > 0
    mock_print.assert_called()


def test_graph_load_from_file():
    """Test Graph load_from_file method"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ttl", delete=False) as f:
        # Write a simple TTL file
        f.write(
            '<http://example.com/subject> <http://example.com/predicate> "object" .\n'
        )
        temp_file = f.name

    try:
        graph = Graph.load_from_file(temp_file, "test-id", "Test Graph", "2023-01-01")

        assert graph.graph_id == "test-id"
        assert graph.name == "Test Graph"
        assert graph.created_at == "2023-01-01"
        # Verify triples were loaded
        triples = list(graph.graph)
        assert len(triples) > 0
    finally:
        os.unlink(temp_file)


# Test GraphManager class
def test_graph_manager_init():
    """Test GraphManager initialization"""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = os.path.join(temp_dir, "test_graph_data.json")
        manager = GraphManager(data_file)

        # GraphManager loads existing graphs from GRAPHS_DATA_DIR by default
        # So we expect it to have loaded any existing TTL files
        assert isinstance(manager.graphs, dict)
        assert isinstance(manager.graph_objs, dict)
        assert manager.graph_id_counter == 0
        assert manager.data_file == data_file


def test_graph_manager_create_graph():
    """Test GraphManager create_graph method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = os.path.join(temp_dir, "test_graph_data.json")
        manager = GraphManager(data_file)

        graph_dict = manager.create_graph("Test Graph")

        assert graph_dict is not None
        graph_id = graph_dict["graph_id"]
        assert graph_id in manager.graphs
        assert graph_id in manager.graph_objs
        assert manager.graphs[graph_id]["name"] == "Test Graph"


def test_graph_manager_get_graph():
    """Test GraphManager get_graph method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = os.path.join(temp_dir, "test_graph_data.json")
        manager = GraphManager(data_file)

        # Create a graph first
        graph_dict = manager.create_graph("Test Graph")
        graph_id = graph_dict["graph_id"]

        # Get the graph
        graph = manager.get_graph(graph_id)

        assert graph is not None
        assert graph["graph_id"] == graph_id
        assert graph["name"] == "Test Graph"


def test_graph_manager_get_graph_not_found():
    """Test GraphManager get_graph method with non-existent graph"""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = os.path.join(temp_dir, "test_graph_data.json")
        manager = GraphManager(data_file)

        graph = manager.get_graph("nonexistent")
        assert graph is None


def test_graph_manager_get_graph_object():
    """Test GraphManager get_graph_object method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = os.path.join(temp_dir, "test_graph_data.json")
        manager = GraphManager(data_file)

        # Create a graph first
        graph_dict = manager.create_graph("Test Graph")
        graph_id = graph_dict["graph_id"]

        # Get the graph object
        graph_obj = manager.get_graph_object(graph_id)

        assert graph_obj is not None
        assert graph_obj.graph_id == graph_id


def test_graph_manager_delete_graph():
    """Test GraphManager delete_graph method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = os.path.join(temp_dir, "test_graph_data.json")
        manager = GraphManager(data_file)

        # Create a graph first
        graph_dict = manager.create_graph("Test Graph")
        graph_id = graph_dict["graph_id"]
        assert graph_id in manager.graphs

        # Delete the graph
        success = manager.delete_graph(graph_id)

        assert success is True
        assert graph_id not in manager.graphs
        assert graph_id not in manager.graph_objs


def test_graph_manager_delete_nonexistent_graph():
    """Test GraphManager delete_graph method with non-existent graph"""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = os.path.join(temp_dir, "test_graph_data.json")
        manager = GraphManager(data_file)

        success = manager.delete_graph("nonexistent")
        assert success is False


def test_graph_manager_list_graphs():
    """Test GraphManager list_graphs method"""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = os.path.join(temp_dir, "test_graph_data.json")
        manager = GraphManager(data_file)

        # Get initial count
        initial_graphs = manager.list_graphs()
        initial_count = len(initial_graphs)

        # Create some graphs
        manager.create_graph("Graph 1")
        manager.create_graph("Graph 2")

        graphs = manager.list_graphs()

        assert len(graphs) == initial_count + 2
        assert any(g["name"] == "Graph 1" for g in graphs)
        assert any(g["name"] == "Graph 2" for g in graphs)


def test_graph_manager_save_and_load():
    """Test GraphManager persistence"""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = os.path.join(temp_dir, "test_graph_data.json")

        # Create manager and add graph
        manager1 = GraphManager(data_file)
        graph_dict = manager1.create_graph("Test Graph")
        graph_id = graph_dict["graph_id"]
        manager1._save()

        # Create new manager and load data
        manager2 = GraphManager(data_file)

        assert graph_id in manager2.graphs
        assert manager2.graphs[graph_id]["name"] == "Test Graph"


# Test prefix management functions
def test_save_prefixes():
    """Test save_prefixes function"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        temp_file = f.name

    try:
        test_prefixes = {"test": "http://example.com/test/"}
        save_prefixes(test_prefixes, temp_file)

        # Verify file was created and contains correct data
        with open(temp_file, "r") as f:
            data = json.load(f)

        assert "test" in data
        assert data["test"] == "http://example.com/test/"
    finally:
        os.unlink(temp_file)


def test_load_global_prefixes():
    """Test load_global_prefixes function"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        # Write a custom prefixes file
        test_prefixes = {"custom": "http://custom.com/"}
        json.dump(test_prefixes, f)
        temp_file = f.name

    try:
        # Load the custom prefixes
        load_global_prefixes(temp_file)

        # Verify the prefixes were loaded into NS_PREFIXES
        assert "custom" in NS_PREFIXES
    finally:
        os.unlink(temp_file)
