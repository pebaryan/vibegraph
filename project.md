# Project Brief: GraphDB Web UI Clone for RDFLib

## Project Overview
This project aims to create a web-based user interface (UI) for interacting with RDF (Resource Description Framework) data stored in local files using the Python RDFLib library. The interface will function as a lightweight alternative to existing GraphDB solutions, focusing on core functionality for RDF data management, querying, visualization, and search.

## Core Features

### 1. Graph Management
- **Local File Storage**: Support for creating new graphs and uploading existing RDF files
- **Multiple Graph Support**: Ability to manage and switch between different RDF graphs

### 2. SPARQL Query Interface
- **Query Execution**: Full-featured SPARQL query editor with syntax highlighting
- **Query History**: Persistent storage of executed queries for later inspection and re-execution
- **Result Display**: Formatted display of query results in tabular and graphical formats

### 3. Graph Visualization
- **Interactive Visualization**: Node-link diagram representation of RDF triples
- **Manual Expansion**: Ability to manually add nodes by specifying IRIs
- **Automatic Expansion**: Option to expand the visualization by adding immediate neighbors of selected nodes
- **Visual Customization**: Node and edge styling options for better readability

### 4. Data Navigation
- **Tabular View**: Browse entities in a table format with filtering capabilities
- **Entity Details**: Detailed view of selected entities showing all properties

### 5. Full-Text Search
- **Whoosh Integration**: Fast full-text search across IRIs and labels
- **Search Filters**: Options to search by IRI, label, or both
- **Result Ranking**: Relevance-based sorting of search results

## Technical Stack

### Frontend
- Framework: angular
- Visualization: D3.js or Vis.js for graph rendering
- Styling: angular material

### Backend
- Web Framework: Flask
- RDF Processing: RDFLib (Python)
- Search Engine: Whoosh
- Data Storage: Local file system (Turtle, RDF/XML, or JSON-LD formats)

### Additional Components
- no need for authentication or advanced features like websocket

## User Workflow

1. **Initial Setup**
   - User creates a new graph or uploads an RDF file
   - System indexes the data for search

2. **Querying**
   - User writes SPARQL queries in the dedicated editor
   - Queries are executed and results displayed as tables
   - IRI in the result can be traversed to be inspected using navigation feature
   - Completed queries are saved to history

3. **Visualization**
   - User selects a starting node
   - Graph is rendered with options to expand
   - Manual node addition for custom exploration

4. **Navigation**
   - User switches between tabular and graphical views
   - Searches for specific entities

## Implementation Phases

### Phase 1: Core Backend
- Set up Flask backend
- Implement RDFLib integration for graph operations
- Create SPARQL endpoint
- Implement Whoosh indexing

### Phase 2: Frontend Foundation
- Set up React.js application
- Create basic UI layout with tabs for different views
- Implement SPARQL query editor with syntax highlighting
- Build query history management

### Phase 3: Visualization
- Integrate D3.js/Vis.js for graph rendering
- Implement node expansion logic
- Add manual node addition functionality

### Phase 4: Navigation and Search
- Build tabular view components
- Implement entity details panel
- Integrate Whoosh search functionality

### Phase 5: Polishing
- Add visual customization options
- Implement user preferences persistence
- Add export/import functionality for graphs
- Create documentation and tutorials

## Success Metrics
- Ability to load and manage RDF graphs from local files
- Correct execution of SPARQL queries with proper results display
- Functional graph visualization with expansion capabilities
- Operational full-text search across all entities
- Intuitive user interface with good performance

## Potential Challenges
- Handling large graphs efficiently in both storage and visualization
- Maintaining good performance with Whoosh indexing
- Creating an intuitive interface for SPARQL queries that may be complex for some users
- Balancing manual and automatic node expansion in the visualization

This project brief provides a comprehensive foundation for developing a functional GraphDB-like interface for RDFLib. The implementation can be prioritized based on specific user needs, with the most essential features being developed first.