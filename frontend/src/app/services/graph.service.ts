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

@Injectable({
  providedIn: 'root',
})
export class GraphService {
  private readonly baseUrl = '/api/graphs';

  constructor(private http: HttpClient) {}

  listGraphs(): Observable<Graph[]> {
    return this.http.get<{ graphs: Graph[] }>(this.baseUrl).pipe(
      map((res) => res.graphs),
      catchError(this.handleError)
    );
  }

  createGraph(name: string): Observable<Graph> {
    return this.http.post<Graph>(this.baseUrl, { name }).pipe(
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
