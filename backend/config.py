"""
Configuration module for VibeGraph application.
Centralizes all file paths, directories, and constants used throughout the application.
"""

import os
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base directory of the application
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Backend specific paths
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
DATA_DIR = os.path.join(BACKEND_DIR, "data")
GRAPH_DATA_FILE = os.path.join(DATA_DIR, "graph_data.json")
GRAPHS_DATA_DIR = os.path.join(DATA_DIR, "graphs_data")
QUERY_HISTORY_DIR = os.path.join(BACKEND_DIR, "query_history")
SEARCH_INDEX_DIR = os.path.join(BACKEND_DIR, "search_index")

# Frontend specific paths (for reference)
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
SRC_DIR = os.path.join(FRONTEND_DIR, "src")

# Default file extensions
DEFAULT_RDF_FORMATS = {
    "turtle": ".ttl",
    "trig": ".trig", 
    "nt": ".nt",
    "nquads": ".nq",
    "xml": ".rdf"
}

# Default namespaces
DEFAULT_NAMESPACES = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "vg": "http://vibe.graph/default/"
}

# API constants
API_VERSION = "v1"

# Log configuration details
logger.info(f"Configuration loaded. Base directory: {BASE_DIR}")
logger.info(f"Graph data file: {GRAPH_DATA_FILE}")
logger.info(f"Graphs data directory: {GRAPHS_DATA_DIR}")
logger.info(f"Query history directory: {QUERY_HISTORY_DIR}")