import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({providedIn:'root'})
export class QueryService {
  private apiUrl = 'http://localhost:5000/api/queries';
  constructor(private http: HttpClient) {}
  execute(query: string): Observable<any> {
    return this.http.post<any>(this.apiUrl, { query });
  }
}
