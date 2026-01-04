# VibeGraph
A Web UI for RDFLib.
This repository contains a lightweight backend built with Flask and a frontend Angular application that lets users query and visualize RDF data.

## Local Setup

### Backend

```bash
# From the project root
pip install -r backend/requirements.txt
```

### Frontend

```bash
# From the frontend directory
cd frontend
npm install
```

## Docker Setup

Run the following command from the project root:

```bash
docker compose up --build
```

This will build the backend and frontend images, expose the backend on port **5000** and the frontend on port **4200**.

Once both containers are up, you can access:

- **Frontend**: <http://localhost:4200>
- **Backend API**: <http://localhost:5000>
- **Swagger UI**: <http://localhost:5000/apidocs>

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/graphs` | Create a new graph. Request body: `{"name": "my graph"}` |
| GET | `/api/graphs` | List all graphs |
| GET | `/api/graphs/<graph_id>` | Retrieve metadata for a graph |
| PUT | `/api/graphs/<graph_id>` | Update graph name. Request body: `{"name": "new name"}` |
| DELETE | `/api/graphs/<graph_id>` | Delete a graph |
| POST | `/api/graphs/<graph_id>/upload` | Upload an RDF file. Use `multipart/form-data` with field `file`. |
| POST | `/api/queries` | Execute a SPARQL query. Request body: `{"query": "SELECT …", "graph_id": "<id>"}` |
| GET | `/api/queries/history` | Get mock query history |
| GET | `/api/search` | Search entities. Request body: `{"query": "search text", "search_by": "label"}` |

---

## Example cURL commands

```bash
# Create a graph
curl -X POST http://localhost:5000/api/graphs \
     -H "Content-Type: application/json" \
     -d '{"name": "example"}'
```

```bash
# List graphs
curl http://localhost:5000/api/graphs
```

```bash
# Upload RDF file to graph with ID 1234
curl -X POST http://localhost:5000/api/graphs/1234/upload \
     -F "file=@/path/to/data.ttl"
```

```bash
# Execute a SPARQL query
curl -X POST http://localhost:5000/api/queries \
     -H "Content-Type: application/json" \
     -d '{"query": "SELECT ?s ?p ?o WHERE { ?s ?p ?o }", "graph_id": "1234"}'
```

```bash
# Search entities
curl -X POST http://localhost:5000/api/search \
     -H "Content-Type: application/json" \
     -d '{"query": "Entity 1", "search_by": "label"}'
```

```bash
# Get query history
curl http://localhost:5000/api/queries/history
```

---

For full API documentation and interactive Swagger UI, run the application and navigate to `http://localhost:5000/apidocs` once Swagger support is added.
