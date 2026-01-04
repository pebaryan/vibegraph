from datetime import datetime
import uuid
import os
import json
from rdflib import Graph as RDFGraph

# Graph Management Model

class Graph:
    def __init__(self, graph_id, name, created_at):
        self.graph_id = graph_id
        self.name = name
        self.created_at = created_at
        self.data = {}
        # RDFLib graph instance for storing triples
        self.graph = RDFGraph()

    def to_dict(self):
        return {
            'graph_id': self.graph_id,
            'name': self.name,
            'created_at': self.created_at,
            'data': self.data
        }

    def serialize(self, directory):
        """Persist the RDF graph to a Turtle file inside the given directory."""
        if not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, f"{self.graph_id}.ttl")
        self.graph.serialize(file_path, format='turtle')

    @staticmethod
    def load_from_file(file_path, graph_id, name, created_at):
        """Load an RDF graph from a Turtle file and return a Graph instance."""
        graph = Graph(graph_id, name, created_at)
        if os.path.exists(file_path):
            graph.graph.parse(file_path, format='turtle')
        return graph

class GraphManager:
    def __init__(self, data_file='graph_data.json'):
        # Store metadata and actual Graph objects separately
        self.graphs = {}  # key: graph_id, value: metadata dict
        self.graph_objs = {}  # key: graph_id, value: Graph instance
        self.graph_id_counter = 0
        self.data_file = data_file
        self._load()

    def _load(self):
        """Load graph metadata and RDF data from storage."""
        # Load metadata
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for graph_id, meta in data.items():
                    graph = Graph(graph_id, meta.get('name', ''), meta.get('created_at', ''))
                    self.graphs[graph_id] = meta
                    self.graph_objs[graph_id] = graph
        # Load RDF data files
        data_dir = os.path.join(os.path.dirname(self.data_file), 'graphs_data')
        if os.path.isdir(data_dir):
            for fname in os.listdir(data_dir):
                if fname.endswith('.ttl'):
                    gid = fname[:-4]
                    if gid in self.graph_objs:
                        file_path = os.path.join(data_dir, fname)
                        self.graph_objs[gid] = Graph.load_from_file(file_path, gid, self.graphs[gid].get('name', ''), self.graphs[gid].get('created_at', ''))

    def _save(self):
        """Persist current graph metadata and RDF data to storage."""
        # Ensure data directory exists
        data_dir = os.path.join(os.path.dirname(self.data_file), 'graphs_data')
        os.makedirs(data_dir, exist_ok=True)
        # Save metadata
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.graphs, f, indent=2)
        # Save each graph's RDF data
        for gid, graph in self.graph_objs.items():
            graph.serialize(data_dir)

    def create_graph(self, name):
        """Create a new graph with a unique identifier"""
        graph_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        graph = Graph(graph_id, name, created_at)
        self.graphs[graph_id] = graph.to_dict()
        self.graph_objs[graph_id] = graph
        self._save()
        return graph.to_dict()

    def list_graphs(self):
        """List all available graphs with their metadata"""
        return [graph for graph in self.graphs.values()]

    def get_graph(self, graph_id):
        """Retrieve graph metadata for a specific graph ID"""
        return self.graphs.get(graph_id)

    def get_graph_object(self, graph_id):
        """Retrieve the Graph instance for a specific graph ID"""
        return self.graph_objs.get(graph_id)

    def delete_graph(self, graph_id):
        """Delete a graph by its ID"""
        if graph_id in self.graphs:
            del self.graphs[graph_id]
            self.graph_objs.pop(graph_id, None)
            self._save()
            return True
        return False

    def update_graph(self, graph_id, name=None):
        """Update the name of an existing graph"""
        if graph_id in self.graphs:
            if name is not None:
                self.graphs[graph_id]['name'] = name
            self._save()
            return True
        return False

    # Persist RDF graph data in Turtle format per graph

    def get_triples(self, graph_id):
        """Retrieve all triples from the RDF graph"""
        graph_obj = self.get_graph_object(graph_id)
        if not graph_obj:
            raise ValueError(f"Graph {graph_id} not found")
        return [{'subject': str(s), 'predicate': str(p), 'object': str(o)} for s, p, o in graph_obj.graph]

# Each graph's RDF data is stored in "graphs_data/<graph_id>.ttl"
