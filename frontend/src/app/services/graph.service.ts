import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { BaseService } from './base.service';

export interface Graph {
  graph_id: string;
  name: string;
  created_at: string;
  data?: any;
}

export interface Triple {
  subject: string;
  predicate: string;
  object: string;
}

export interface TripleResult {
  triples: Triple[];
}

@Injectable({
  providedIn: 'root',
})
export class GraphService extends BaseService {
  private readonly baseUrl: string;

  constructor(http: HttpClient) {
    super(http);
    this.baseUrl = `${this.apiHost}/api/graphs`;
  }

  listGraphs(): Observable<Graph[]> {
    return this.http.get<Graph[]>(this.baseUrl);
  }

  getTriples(graphId: string): Observable<TripleResult> {
    return this.http.get<TripleResult>(`${this.baseUrl}/${graphId}/triples`);
  }

  createTriple(graphId: string, triple: Triple): Observable<any> {
    return this.http.post(`${this.baseUrl}/${graphId}/triples`, triple);
  }

  deleteTriple(graphId: string, triple: Triple): Observable<any> {
    return this.http.post(`${this.baseUrl}/${graphId}/triples/delete`, triple);
  }

  /**
   * Create a new graph. Accepts optional SPARQL and authentication details.
   * @param params Object containing graph creation parameters.
   */
  createGraph(params: {name: string, sparql_read?: string, sparql_update?: string, auth_type?: string, auth_info?: any}): Observable<Graph> {
    return this.http.post<Graph>(this.baseUrl, params);
  }

  updateGraph(id: string, name: string): Observable<any> {
    return this.http.put(`${this.baseUrl}/${id}`, { name });
  }

  deleteGraph(id: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/${id}`);
  }

  /**
   * Trigger a full re‑index of all graphs.
   * @returns Observable that completes when the server responds.
   */
  reindexAll(): Observable<any> {
    return this.http.post(`${this.baseUrl}/reindex`, {});
  }

  /**
   * Clear all graphs, optionally clearing history and search index.
   */
  clearAll(options?: { clear_history?: boolean; clear_index?: boolean }): Observable<any> {
    return this.http.post(`${this.baseUrl}/clear`, options ?? {});
  }

  /**
   * Upload an RDF file to an existing graph.
   * @param graphId ID of the graph.
   * @param file File object to upload.
   * @param format RDF serialization format (e.g., 'turtle', 'trig', 'nt').
   */
  uploadGraphFile(graphId: string, file: File, format?: string): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    if (format) {
      formData.append('format', format);
    }
    return this.http.post(`${this.baseUrl}/${graphId}/upload`, formData);
  }
}
