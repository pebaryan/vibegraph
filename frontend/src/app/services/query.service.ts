import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { BaseService } from './base.service';

@Injectable({ providedIn: "root" })
export class QueryService extends BaseService {
  private readonly baseUrl: string;

  constructor(http: HttpClient) {
    super(http);
    this.baseUrl = `${this.apiHost}/api/queries`;
  }
  
  execute(query: string): Observable<any> {
    return this.http.post<any>(this.baseUrl, { query });
  }

  executeSparql(query: string, accept: string): Observable<any> {
    return this.http.post<any>(`${this.apiHost}/sparql/query`, query, {
      headers: { Accept: accept, "Content-Type": "application/sparql-query" },
      responseType: "text" as "json",
    });
  }

  getHistory(graph_id: string): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/${graph_id}`);
  }
}
