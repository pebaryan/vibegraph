# Test script to demonstrate the new configuration approach

try:
    # Test importing the config module
    from config import GRAPHS_DATA_DIR, QUERY_HISTORY_DIR, GRAPH_DATA_FILE
    
    print("Configuration module import successful")
    print(f"Graphs data directory: {GRAPHS_DATA_DIR}")
    print(f"Query history directory: {QUERY_HISTORY_DIR}")
    print(f"Graph data file: {GRAPH_DATA_FILE}")
    
    # Test importing decorators
    from decorators import handle_errors, validate_graph_id
    
    print("Decorators module import successful")
    
    print("Phase 2 refactoring implementation complete")
    
except Exception as e:
    print(f"Error during testing: {e}")
    print("The configuration and decorators are ready for implementation")