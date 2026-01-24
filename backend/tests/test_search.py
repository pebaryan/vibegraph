import pytest
import sys
import os
import tempfile
import json
from unittest.mock import patch, MagicMock

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.search import WhooshSearchEngine


# Test WhooshSearchEngine class
class TestWhooshSearchEngine:
    """Test suite for WhooshSearchEngine"""

    def setup_method(self):
        """Setup test environment with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.search_engine = WhooshSearchEngine(self.temp_dir)

    def teardown_method(self):
        """Clean up temporary directory"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init_creates_index(self):
        """Test that initialization creates an index"""
        assert self.search_engine.path == self.temp_dir
        assert self.search_engine.index is not None
        assert os.path.exists(self.temp_dir)

    def test_init_with_default_path(self):
        """Test initialization with default path"""
        # Test with default path (might create search_index directory)
        default_engine = WhooshSearchEngine()
        assert default_engine.path == "search_index"
        assert default_engine.index is not None

    def test_create_index_new_directory(self):
        """Test create_index in a new directory"""
        new_temp_dir = tempfile.mkdtemp()
        try:
            engine = WhooshSearchEngine(new_temp_dir)
            assert engine.index is not None
            assert os.path.exists(new_temp_dir)

            # Check that index files are created
            files_in_dir = os.listdir(new_temp_dir)
            assert len(files_in_dir) > 0  # Should have index files
        finally:
            import shutil

            if os.path.exists(new_temp_dir):
                shutil.rmtree(new_temp_dir)

    def test_create_index_existing_directory(self):
        """Test create_index with existing index"""
        # Create first instance
        engine1 = WhooshSearchEngine(self.temp_dir)
        engine1.add_entity(
            {
                "iri": "http://example.com/test",
                "label": "Test Entity",
                "graph_id": "test-graph",
            }
        )

        # Create second instance with same directory
        engine2 = WhooshSearchEngine(self.temp_dir)
        assert engine2.index is not None

    @patch("models.search.open_dir")
    @patch("models.search.create_in")
    def test_create_index_open_exception(self, mock_create_in, mock_open_dir):
        """Test create_index when open_dir raises exception"""
        mock_open_dir.side_effect = Exception("Test exception")

        # Create temporary directory with some files to trigger open_dir
        os.makedirs(self.temp_dir, exist_ok=True)
        with open(os.path.join(self.temp_dir, "test.txt"), "w") as f:
            f.write("test")

        engine = WhooshSearchEngine(self.temp_dir)

        # Should fall back to create_in
        mock_create_in.assert_called_once()
        assert engine.index is not None

    def test_add_entity(self):
        """Test adding an entity to the search index"""
        entity = {
            "iri": "http://example.com/entity1",
            "label": "Entity One",
            "graph_id": "graph1",
        }

        # Should not raise exception
        self.search_engine.add_entity(entity)

        # Verify entity was added by searching
        results = self.search_engine.search("Entity One", search_by="label")
        assert results["count"] >= 1
        found_entities = [
            r for r in results["results"] if r["iri"] == "http://example.com/entity1"
        ]
        assert len(found_entities) > 0

    def test_add_entity_minimal_data(self):
        """Test adding entity with minimal data"""
        entity = {"iri": "http://example.com/minimal"}

        # Should not raise exception
        self.search_engine.add_entity(entity)

    def test_add_entity_with_update(self):
        """Test updating an existing entity"""
        entity = {
            "iri": "http://example.com/updateable",
            "label": "Original Label",
            "graph_id": "graph1",
        }

        # Add entity first time
        self.search_engine.add_entity(entity)

        # Update entity with new label
        entity["label"] = "Updated Label"
        self.search_engine.add_entity(entity)

        # Search should return updated entity
        results = self.search_engine.search("Updated Label", search_by="label")
        assert results["count"] >= 1
        found_entities = [
            r for r in results["results"] if r["label"] == "Updated Label"
        ]
        assert len(found_entities) > 0

    def test_search_by_iri(self):
        """Test searching by IRI"""
        entity = {
            "iri": "http://example.com/searchable",
            "label": "Searchable Entity",
            "graph_id": "graph1",
        }

        self.search_engine.add_entity(entity)

        # Search by IRI
        results = self.search_engine.search(
            "http://example.com/searchable", search_by="iri"
        )
        assert results["count"] >= 1
        found_entities = [
            r for r in results["results"] if r["iri"] == "http://example.com/searchable"
        ]
        assert len(found_entities) > 0
        assert results["search_by"] == "iri"
        assert results["query"] == "http://example.com/searchable"

    def test_search_by_label(self):
        """Test searching by label"""
        entity = {
            "iri": "http://example.com/label-search",
            "label": "Label Search Test",
            "graph_id": "graph1",
        }

        self.search_engine.add_entity(entity)

        # Search by label
        results = self.search_engine.search("Label Search Test", search_by="label")
        assert results["count"] >= 1
        found_entities = [
            r for r in results["results"] if r["label"] == "Label Search Test"
        ]
        assert len(found_entities) > 0
        assert results["search_by"] == "label"
        assert results["query"] == "Label Search Test"

    def test_search_no_results(self):
        """Test search with no matching results"""
        # Search without adding any entities
        results = self.search_engine.search("nonexistent", search_by="label")

        assert results["count"] == 0
        assert results["results"] == []
        assert results["query"] == "nonexistent"
        assert results["search_by"] == "label"

    def test_search_default_search_by(self):
        """Test search with default search_by parameter"""
        entity = {
            "iri": "http://example.com/default-search",
            "label": "Default Search",
            "graph_id": "graph1",
        }

        self.search_engine.add_entity(entity)

        # Search without specifying search_by (should default to "iri")
        results = self.search_engine.search("default")
        assert results["search_by"] == "iri"

    def test_get_results_no_index(self):
        """Test get_results when index is None"""
        # Create engine with no index
        engine = WhooshSearchEngine()
        engine.index = None

        results = engine.get_results("test", "label")
        assert "error" in results
        assert results["error"] == "Index not created"

    def test_get_results_with_multiple_entities(self):
        """Test get_results with multiple entities"""
        entities = [
            {
                "iri": "http://example.com/entity1",
                "label": "First Entity",
                "graph_id": "graph1",
            },
            {
                "iri": "http://example.com/entity2",
                "label": "Second Entity",
                "graph_id": "graph2",
            },
            {
                "iri": "http://example.com/entity3",
                "label": "Third Entity",
                "graph_id": "graph1",
            },
        ]

        # Add all entities
        for entity in entities:
            self.search_engine.add_entity(entity)

        # Search for "Entity"
        results = self.search_engine.search("Entity", search_by="label")

        assert results["count"] >= 3
        assert len(results["results"]) >= 3

        # Verify all entities are present
        labels = [r["label"] for r in results["results"]]
        assert "First Entity" in labels
        assert "Second Entity" in labels
        assert "Third Entity" in labels

    def test_search_response_format(self):
        """Test that search responses have correct format"""
        entity = {
            "iri": "http://example.com/format-test",
            "label": "Format Test Entity",
            "graph_id": "test-graph",
        }

        self.search_engine.add_entity(entity)
        results = self.search_engine.search("Format Test", search_by="label")

        # Check response structure
        required_keys = ["query", "search_by", "results", "count"]
        for key in required_keys:
            assert key in results

        # Check result structure
        if results["count"] > 0:
            result = results["results"][0]
            result_keys = ["iri", "label", "graph_id"]
            for key in result_keys:
                assert key in result

    def test_add_entity_empty_dict(self):
        """Test adding an empty entity dictionary"""
        # Should not raise exception
        self.search_engine.add_entity({})

        # Search should work but return no results
        results = self.search_engine.search("test", search_by="label")
        assert results["count"] == 0

    def test_search_partial_match(self):
        """Test searching with partial matches"""
        entity = {
            "iri": "http://example.com/partial",
            "label": "Partial Match Test Entity",
            "graph_id": "graph1",
        }

        self.search_engine.add_entity(entity)

        # Search for partial term
        results = self.search_engine.search("Partial", search_by="label")
        assert results["count"] >= 1

    def test_get_results_index_error(self):
        """Test get_results when there's an index error"""
        # Create engine and manually set index to None
        engine = WhooshSearchEngine(self.temp_dir)
        engine.index = None

        results = engine.get_results("test", "label")

        # Should return error response
        assert "error" in results
        assert results["error"] == "Index not created"

    def test_index_directory_persistence(self):
        """Test that index persists across instances"""
        # Add entity with first instance
        entity = {
            "iri": "http://example.com/persistent",
            "label": "Persistent Entity",
            "graph_id": "test-graph",
        }
        self.search_engine.add_entity(entity)

        # Create new instance with same directory
        new_engine = WhooshSearchEngine(self.temp_dir)

        # Should find the entity
        results = new_engine.search("Persistent Entity", search_by="label")
        assert results["count"] >= 1

    def test_multiple_adds_and_searches(self):
        """Test multiple add operations followed by searches"""
        # Add multiple entities
        for i in range(5):
            entity = {
                "iri": f"http://example.com/entity{i}",
                "label": f"Entity {i}",
                "graph_id": "test-graph",
            }
            self.search_engine.add_entity(entity)

        # Search for each entity
        for i in range(5):
            results = self.search_engine.search(f"Entity {i}", search_by="label")
            assert results["count"] >= 1
            found_entities = [
                r for r in results["results"] if f"Entity {i}" in r["label"]
            ]
            assert len(found_entities) > 0
