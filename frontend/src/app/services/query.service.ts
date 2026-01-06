import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";

@Injectable({ providedIn: "root" })
export class QueryService {
  private readonly apiHost = "//localhost:5000";
  private readonly baseUrl = this.apiHost + "/api/queries";

  constructor(private http: HttpClient) {}
  execute(query: string): Observable<any> {
    return this.http.post<any>(this.baseUrl, { query });
  }

  getHistory(graph_id: string): Observable<any> {
    return this.http.get<any>(this.baseUrl + "/" + graph_id);
  }
}
