/**
 * Base service class for common HTTP operations in VibeGraph frontend
 */

import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export abstract class BaseService {
  protected apiHost = 'http://localhost:5000';
  
  constructor(protected http: HttpClient) {}

  protected handleError(error: HttpErrorResponse) {
    let errorMsg = 'An unknown error occurred';
    if (error.error instanceof ErrorEvent) {
      // Client-side/network error
      errorMsg = `Network error: ${error.error.message}`;
    } else {
      // Backend returned an unsuccessful response code.
      errorMsg = error.error?.error || `Server returned code ${error.status}`;
    }
    return throwError(() => errorMsg);
  }
}

/**
 * API Configuration service for centralized API endpoints
 */
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class ApiConfigService {
  private readonly apiHost = 'http://localhost:5000';
  
  getApiHost(): string {
    return this.apiHost;
  }
  
  getGraphsBaseUrl(): string {
    return `${this.apiHost}/api/graphs`;
  }
  
  getQueriesBaseUrl(): string {
    return `${this.apiHost}/api/queries`;
  }
  
  getSearchBaseUrl(): string {
    return `${this.apiHost}/api/search`;
  }
}