from datetime import datetime
import uuid

# Graph Management Model

class Graph:
    def __init__(self, graph_id, name, created_at):
        self.graph_id = graph_id
        self.name = name
        self.created_at = created_at
        self.data = {}

    def to_dict(self):
        return {
            'graph_id': self.graph_id,
            'name': self.name,
            'created_at': self.created_at,
            'data': self.data
        }

class GraphManager:
    def __init__(self):
        self.graphs = {}
        self.graph_id_counter = 0

    def create_graph(self, name):
        """Create a new graph with a unique identifier"""
        graph_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        graph = Graph(graph_id, name, created_at)
        self.graphs[graph_id] = graph.to_dict()
        return graph.to_dict()

    def list_graphs(self):
        """List all available graphs with their metadata"""
        return [graph for graph in self.graphs.values()]

    def get_graph(self, graph_id):
        """Retrieve graph data for a specific graph ID"""
        if graph_id in self.graphs:
            return self.graphs[graph_id]
        return None

    def delete_graph(self, graph_id):
        """Delete a graph by its ID"""
        if graph_id in self.graphs:
            del self.graphs[graph_id]
            return True
        return False

    def update_graph(self, graph_id, name=None):
        """Update the name of an existing graph"""
        if graph_id in self.graphs:
            if name is not None:
                self.graphs[graph_id]['name'] = name
            return True
        return False