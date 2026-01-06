import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class SearchService {
  private readonly apiHost = '//localhost:5000'
  private readonly baseUrl = this.apiHost + '/api/search';

  constructor(private http: HttpClient) {}

  search(query: string): Observable<any> {
    return this.http.post<any>(this.baseUrl, { query });
  }
}
