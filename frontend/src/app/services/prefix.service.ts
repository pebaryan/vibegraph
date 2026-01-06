import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface Prefix {
  prefix: string;
  uri: string;
}

@Injectable({
  providedIn: 'root',
})
export class PrefixService {
  private readonly apiHost = '//localhost:5000';
  private readonly baseUrl = this.apiHost + '/api/prefixes';

  constructor(private http: HttpClient) {}

  getPrefixes(): Observable<Prefix[]> {
    return this.http.get<Prefix[]>(this.baseUrl).pipe(catchError(this.handleError));
  }

  addPrefix(prefix: string, uri: string): Observable<any> {
    return this.http.post(this.baseUrl, { prefix, uri }).pipe(catchError(this.handleError));
  }

  updatePrefix(prefix: string, uri: string): Observable<any> {
    return this.http.put(`${this.baseUrl}/${prefix}`, { uri }).pipe(catchError(this.handleError));
  }

  deletePrefix(prefix: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/${prefix}`).pipe(catchError(this.handleError));
  }

  private handleError(error: HttpErrorResponse) {
    let errorMsg = 'An unknown error occurred';
    if (error.error instanceof ErrorEvent) {
      errorMsg = `Network error: ${error.error.message}`;
    } else {
      errorMsg = error.error?.error || `Server returned code ${error.status}`;
    }
    return throwError(errorMsg);
  }
}
