from datetime import datetime
import uuid
import os
import json
from rdflib import Graph as RDFGraph
from rdflib import URIRef, Literal, BNode, Namespace
from rdflib import RDF, RDFS, OWL

# Import configuration
from config import GRAPHS_DATA_DIR, GRAPH_DATA_FILE
from config import QUERY_HISTORY_DIR
import shutil

# Global namespace prefixes loaded from nsprefixes.json
import json
import os

NS_PREFIXES = {
    "rdf": RDF,
    "rdfs": RDFS,
    "owl": OWL,
    "vg": Namespace("http://vibe.graph/default/"),
}

# Function to save and load prefixes from file
PREFIXE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "nsprefixes.json"
)


def save_prefixes(prefixes=NS_PREFIXES, file_path=PREFIXE_FILE):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({k: str(v) for k, v in prefixes.items()}, f, indent=2)


def load_global_prefixes(file_path=PREFIXE_FILE):
    global NS_PREFIXES
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in data.items():
            NS_PREFIXES[k] = Namespace(v)
    except Exception:
        save_prefixes(NS_PREFIXES, file_path)


# Load on import
load_global_prefixes()


# Graph Management Model


class Graph:
    def __init__(
        self,
        graph_id,
        name,
        created_at,
        sparql_read=None,
        sparql_update=None,
        auth_type="None",
        auth_info=None,
    ):
        self.graph_id = graph_id
        self.name = name
        self.created_at = created_at
        self.data = {}
        # Metadata for SPARQL data source
        self.sparql_read = sparql_read
        self.sparql_update = sparql_update
        self.auth_type = auth_type
        self.auth_info = auth_info
        # RDFLib graph instance for storing triples
        if sparql_read:
            try:
                from rdflib.plugins.stores.sparqlstore import SPARQLStore

                store = SPARQLStore()
                auth_kwargs = {}
                if auth_type == "Basic" and auth_info:
                    auth_kwargs = {
                        "username": auth_info.get("username"),
                        "password": auth_info.get("password"),
                    }
                elif auth_type == "JWT" and auth_info:
                    token = auth_info.get("token")
                    auth_kwargs = {"headers": {"Authorization": f"Bearer {token}"}}
                store.open(sparql_read, sparql_update, **auth_kwargs)
                self.graph = RDFGraph(store=store)
            except Exception:
                # Fallback to default graph if SPARQLStore fails
                self.graph = RDFGraph()
        else:
            self.graph = RDFGraph()

    def to_dict(self):
        return {
            "graph_id": self.graph_id,
            "name": self.name,
            "created_at": self.created_at,
            "data": self.data,
            "sparql_read": self.sparql_read,
            "sparql_update": self.sparql_update,
            "auth_type": self.auth_type,
            "auth_info": self.auth_info,
        }

    def serialize(self, directory):
        """Persist the RDF graph to a Turtle file inside the given directory."""
        if not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)
        file_path = os.path.join(directory, f"{self.graph_id}.ttl")
        self.graph.serialize(file_path, format="turtle")

    def add_triple(self, triple, prefixNS=NS_PREFIXES):
        triple = (
            self.wrap(triple[0], "s", prefixNS=prefixNS),
            self.wrap(triple[1], prefixNS=prefixNS),
            self.wrap(triple[2], "o", prefixNS=prefixNS),
        )
        print("add ", triple)
        self.graph.add(triple)

    def wrap(self, value: str, pos="p", prefixNS=NS_PREFIXES):
        defaultNs = Namespace("http://vibe.graph/default/")
        prefixes = NS_PREFIXES
        if pos in ("s", "o"):
            if pos == "o":
                literal = self._parse_literal(value, prefixes)
                if literal is not None:
                    return literal
            if value.startswith("_:"):
                return BNode(value[2:])
            elif "://" in value:
                return URIRef(value)
            elif ":" in value:
                ci = value.index(":")
                prefix = value[:ci]
                postfix = value[ci + 1 :]
                if prefix in prefixes:
                    return prefixes[prefix][postfix]
                return defaultNs[postfix]
            else:
                return Literal(value)
        else:
            if value == "a":
                return RDF.type
            elif "://" in value:
                return URIRef(value)
            elif ":" in value:
                ci = value.index(":")
                prefix = value[:ci]
                postfix = value[ci + 1 :]
                if prefix in prefixes:
                    return prefixes[prefix][postfix]
                return defaultNs[postfix]
            else:
                return defaultNs[value]

    def index(self, search_engine, graph_id):
        # Index new triples
        numtris = 0
        for s, p, o in self.graph:
            search_engine.add_entity(
                {
                    "iri": str(s),
                    "label": str(s),
                    "graph_id": graph_id,
                }
            )
            numtris += 1
        print(f"indexed {numtris} triples")

    def _parse_literal(self, value: str, prefixes):
        """Parse a typed or language-tagged literal using a quoted form."""
        raw = value.strip()
        if not raw.startswith('"'):
            return None
        if raw.endswith('"'):
            return Literal(raw[1:-1])
        # "value"@en
        if '"@' in raw:
            base, lang = raw.rsplit('"@', 1)
            if base.startswith('"') and lang:
                return Literal(base[1:], lang=lang)
        # "value"^^datatype
        if '"^^' in raw:
            base, dtype = raw.rsplit('"^^', 1)
            if base.startswith('"') and dtype:
                datatype = self._resolve_datatype(dtype.strip(), prefixes)
                return Literal(base[1:], datatype=datatype)
        return None

    def _resolve_datatype(self, dtype: str, prefixes):
        if dtype.startswith("<") and dtype.endswith(">"):
            return URIRef(dtype[1:-1])
        if "://" in dtype:
            return URIRef(dtype)
        if ":" in dtype:
            prefix, local = dtype.split(":", 1)
            if prefix in prefixes:
                return prefixes[prefix][local]
        return URIRef(dtype)

    @staticmethod
    def load_from_file(
        file_path,
        graph_id,
        name,
        created_at,
        sparql_read=None,
        sparql_update=None,
        auth_type="None",
        auth_info=None,
    ):
        """Load an RDF graph from a Turtle file and return a Graph instance."""
        graph = Graph(
            graph_id, name, created_at, sparql_read, sparql_update, auth_type, auth_info
        )
        if os.path.exists(file_path):
            graph.graph.parse(file_path, format="turtle")
        return graph


class GraphManager:
    def __init__(self, data_file="graph_data.json"):
        # Store metadata and actual Graph objects separately
        self.graphs = {}  # key: graph_id, value: metadata dict
        self.graph_objs = {}  # key: graph_id, value: Graph instance
        self.graph_id_counter = 0
        self.prefixes = NS_PREFIXES
        self.data_file = data_file
        self._load()

    def _load(self):
        """Load graph metadata and RDF data from storage."""
        # Load metadata
        if os.path.exists(self.data_file):
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for graph_id, meta in data.items():
                    graph = Graph(
                        graph_id,
                        meta.get("name", ""),
                        meta.get("created_at", ""),
                        meta.get("sparql_read"),
                        meta.get("sparql_update"),
                        meta.get("auth_type", "None"),
                        meta.get("auth_info"),
                    )
                    self.graphs[graph_id] = meta
                    self.graph_objs[graph_id] = graph
        # Load RDF data files and sync metadata
        data_dir = GRAPHS_DATA_DIR
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir, exist_ok=True)
        existing_files = set()
        for fname in os.listdir(data_dir):
            if fname.endswith(".ttl"):
                gid = fname[:-4]
                existing_files.add(gid)
                # Create metadata if missing
                if gid not in self.graphs:
                    created_at = datetime.now().isoformat()
                    self.graphs[gid] = {
                        "graph_id": gid,
                        "name": gid,
                        "created_at": created_at,
                        "sparql_read": None,
                        "sparql_update": None,
                        "auth_type": "None",
                        "auth_info": None,
                    }
                file_path = os.path.join(data_dir, fname)
                self.graph_objs[gid] = Graph.load_from_file(
                    file_path,
                    gid,
                    self.graphs[gid].get("name", ""),
                    self.graphs[gid].get("created_at", ""),
                    self.graphs[gid].get("sparql_read"),
                    self.graphs[gid].get("sparql_update"),
                    self.graphs[gid].get("auth_type", "None"),
                    self.graphs[gid].get("auth_info"),
                )
        # Remove metadata entries for missing files
        for gid in list(self.graphs.keys()):
            if gid not in existing_files:
                del self.graphs[gid]
                self.graph_objs.pop(gid, None)
        # Persist changes
        self._save()

    def _save(self):
        """Persist current graph metadata and RDF data to storage."""
        # Ensure data directory exists
        data_dir = GRAPHS_DATA_DIR
        os.makedirs(data_dir, exist_ok=True)
        # Save metadata
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.graphs, f, indent=2)
        # Save each graph's RDF data
        for gid, graph in self.graph_objs.items():
            graph.serialize(data_dir)

    def create_graph(
        self,
        name,
        sparql_read=None,
        sparql_update=None,
        auth_type="None",
        auth_info=None,
    ):
        """Create a new graph with a unique identifier"""
        graph_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        graph = Graph(
            graph_id, name, created_at, sparql_read, sparql_update, auth_type, auth_info
        )
        self.graphs[graph_id] = graph.to_dict()
        self.graph_objs[graph_id] = graph
        self._save()
        return graph.to_dict()

    def index_graph(self, graph_id, search_engine):
        self.graph_objs[graph_id].index(search_engine, graph_id)

    def list_graphs(self):
        """List all available graphs with their metadata"""
        return [graph for graph in self.graphs.values()]

    def reindex_all(self, search_engine):
        """Re‑index every stored graph in the search engine.
        Clears the existing index and indexes all graph entities.
        Returns the number of graphs indexed.
        """
        # Reset index – easiest to create a fresh Whoosh index
        search_engine.create_index()
        count = 0
        for graph_id in self.graph_objs:
            print("indexing ", self.graphs[graph_id]["name"])
            self.graph_objs[graph_id].index(search_engine, graph_id)
            count += 1
        return count

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
            graph_file = os.path.join(
                os.path.dirname(self.data_file), "graphs_data", f"{graph_id}.ttl"
            )
            print(graph_file, "exists?", os.path.exists(graph_file))
            if os.path.exists(graph_file):
                os.unlink(graph_file)
            self._save()
            return True
        return False

    def add_triple(self, graph_id, triple):
        if graph_id in self.graphs:
            g = self.get_graph_object(graph_id).add_triple(triple)
            self._save()
            return True
        return False

    def remove_triple(self, graph_id, triple):
        if graph_id in self.graphs:
            graph_obj = self.get_graph_object(graph_id)
            wrapped = (
                graph_obj.wrap(triple[0], "s", prefixNS=self.prefixes),
                graph_obj.wrap(triple[1], "p", prefixNS=self.prefixes),
                graph_obj.wrap(triple[2], "o", prefixNS=self.prefixes),
            )
            graph_obj.graph.remove(wrapped)
            self._save()
            return True
        return False

    def clear_all(self, clear_history=True):
        """Remove all graphs and associated data from storage."""
        self.graphs = {}
        self.graph_objs = {}

        # Remove graph data files
        if os.path.isdir(GRAPHS_DATA_DIR):
            for fname in os.listdir(GRAPHS_DATA_DIR):
                file_path = os.path.join(GRAPHS_DATA_DIR, fname)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
        # Reset metadata file
        if os.path.exists(GRAPH_DATA_FILE):
            with open(GRAPH_DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=2)

        # Optionally clear query history
        if clear_history:
            shutil.rmtree(QUERY_HISTORY_DIR, ignore_errors=True)
            os.makedirs(QUERY_HISTORY_DIR, exist_ok=True)

        self._save()

    def update_graph(self, graph_id, name=None):
        """Update the name of an existing graph"""
        if graph_id in self.graphs:
            if name is not None:
                self.graphs[graph_id]["name"] = name
            self._save()
            return True
        return False

    # Persist RDF graph data in Turtle format per graph

    def get_triples(self, graph_id):
        """Retrieve all triples from the RDF graph"""
        graph_obj = self.get_graph_object(graph_id)
        if not graph_obj:
            raise ValueError(f"Graph {graph_id} not found")
        # for s, p, o in graph_obj.graph:
        #     print(s, p, o)
        return [
            {"subject": str(s), "predicate": str(p), "object": str(o)}
            for s, p, o in graph_obj.graph
        ]

    def save_prefixes(self):
        save_prefixes(self.prefixes)

    def add_prefix(self, prefix, uri):
        if prefix in self.prefixes:
            raise ValueError("Prefix already exists")
        self.prefixes[prefix] = Namespace(uri)
        self.save_prefixes()

    def update_prefix(self, prefix, uri):
        self.prefixes[prefix] = Namespace(uri)
        self.save_prefixes()

    def remove_prefix(self, prefix, uri):
        if prefix not in self.prefixes:
            raise ValueError("Prefix does not exists")
        del self.prefixes[prefix]
        self.save_prefixes()


# Each graph's RDF data is stored in "graphs_data/<graph_id>.ttl"
