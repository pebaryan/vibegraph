from flask import jsonify, request
from backend.models.graph import GraphManager

# Initialize graph manager
graph_manager = GraphManager()

# Routes for graph management
# Create a new graph
@app.route('/api/graphs', methods=['POST'])
def create_graph():
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    result = graph_manager.create_graph(name)
    return jsonify(result), 201

# List all graphs
@app.route('/api/graphs', methods=['GET'])
def list_graphs():
    graphs = graph_manager.list_graphs()
    return jsonify({'graphs': graphs})

# Get a specific graph by ID
@app.route('/api/graphs/<graph_id>', methods=['GET'])
def get_graph(graph_id):
    graph = graph_manager.get_graph(graph_id)
    if graph:
        return jsonify(graph)
    return jsonify({'error': 'Graph not found'}), 404

# Delete a graph by ID
@app.route('/api/graphs/<graph_id>', methods=['DELETE'])
def delete_graph(graph_id):
    if graph_manager.delete_graph(graph_id):
        return jsonify({'message': 'Graph deleted successfully'}), 200
    return jsonify({'error': 'Graph not found'}), 404

# Update a graph name
@app.route('/api/graphs/<graph_id>', methods=['PUT'])
def update_graph(graph_id):
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400

    if graph_manager.update_graph(graph_id, name):
        return jsonify({'message': 'Graph name updated successfully'}), 200
    return jsonify({'error': 'Graph not found'}), 404