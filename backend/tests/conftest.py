import pytest
import shutil
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from routes.graphs import graph_manager
from routes.search import search_engine


@pytest.fixture(scope="session", autouse=True)
def cleanup_graph_data_after_tests():
    yield
    graph_manager.clear_all(clear_history=True)
    # Reset search index to avoid dirty repo state
    shutil.rmtree(search_engine.path, ignore_errors=True)
    search_engine.create_index()
