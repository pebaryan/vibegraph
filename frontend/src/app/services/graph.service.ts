import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

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
export class GraphService {
  private readonly apiHost = '//localhost:5000'
  private readonly baseUrl = this.apiHost + '/api/graphs';

  constructor(private http: HttpClient) {}

  listGraphs(): Observable<Graph[]> {
    return this.http.get<{ graphs: Graph[] }>(this.baseUrl).pipe(
      map((res) => res.graphs),
      catchError(this.handleError)
    );
  }

  getTriples(graphId: string): Observable<TripleResult> {
    return this.http.get<TripleResult>(`${this.baseUrl}/${graphId}/triples`).pipe(
      catchError(this.handleError)
    );
  }

  createTriple(graphId: string, triple: Triple): Observable<any> {
    return this.http.post(`${this.baseUrl}/${graphId}/triples`, triple).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Create a new graph. Accepts optional SPARQL and authentication details.
   * @param params Object containing graph creation parameters.
   */
  createGraph(params: {name: string, sparql_read?: string, sparql_update?: string, auth_type?: string, auth_info?: any}): Observable<Graph> {
    return this.http.post<Graph>(this.baseUrl, params).pipe(
      catchError(this.handleError)
    );
  }

  updateGraph(id: string, name: string): Observable<any> {
    return this.http.put(`${this.baseUrl}/${id}`, { name }).pipe(
      catchError(this.handleError)
    );
  }

  deleteGraph(id: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/${id}`).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Trigger a full re‑index of all graphs.
   * @returns Observable that completes when the server responds.
   */
  reindexAll(): Observable<any> {
    return this.http.post(`${this.baseUrl}/reindex`, {});
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
    return this.http.post(`${this.baseUrl}/${graphId}/upload`, formData).pipe(
      catchError(this.handleError)
    );
  }

  private handleError(error: HttpErrorResponse) {
    // In a real app, you might use a remote logging infrastructure
    let errorMsg = 'An unknown error occurred';
    if (error.error instanceof ErrorEvent) {
      // Client-side/network error
      errorMsg = `Network error: ${error.error.message}`;
    } else {
      // Backend returned an unsuccessful response code.
      errorMsg = error.error?.error || `Server returned code ${error.status}`;
    }
    return throwError(errorMsg);
  }
}
