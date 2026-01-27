import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";
import { BaseService } from "./base.service";

export interface LlmConfig {
  enabled: boolean;
  provider: string;
  model: string;
  api_base: string;
  api_key?: string;
  temperature: number;
  max_tokens: number;
  has_api_key?: boolean;
}

@Injectable({ providedIn: "root" })
export class LlmService extends BaseService {
  private readonly baseUrl: string;

  constructor(http: HttpClient) {
    super(http);
    this.baseUrl = `${this.apiHost}/api/llm`;
  }

  getConfig(): Observable<LlmConfig> {
    return this.http.get<LlmConfig>(`${this.baseUrl}/config`);
  }

  updateConfig(config: Partial<LlmConfig>): Observable<LlmConfig> {
    return this.http.post<LlmConfig>(`${this.baseUrl}/config`, config);
  }

  generateSparql(question: string, graph_id?: string | null): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/sparql`, { question, graph_id });
  }

  repairSparql(query: string, error: string): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/repair`, { query, error });
  }

  extractEntities(text: string, graph_id?: string | null): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/extract`, { text, graph_id });
  }

  linkEntities(graph_id: string, entities: any[], limit: number = 5): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/link`, { graph_id, entities, limit });
  }
}
