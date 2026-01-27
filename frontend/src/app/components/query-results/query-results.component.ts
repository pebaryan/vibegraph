import { Component, OnInit } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { Triple } from "@app/services/graph.service";
import { AppState } from "@app/state/app.state";
import { QueryService } from "@app/services/query.service";

@Component({
  selector: "app-query-results",
  templateUrl: "./query-results.component.html",
  styleUrls: ["./query-results.component.scss"],
})
export class QueryResultsComponent implements OnInit {
  selectedEntity: any = null;
  displayedColumns: string[] = [];
  dataSource = new MatTableDataSource<any>([]);
  rawResult: any = null;
  exportFormat: "csv" | "json" | "turtle" | "jsonld" | "rdfxml" | "ntriples" =
    "csv";
  lastQuery = "";
  lastQueryType: "SELECT" | "ASK" | "CONSTRUCT" | "DESCRIBE" | "UNKNOWN" = "UNKNOWN";

  constructor(public state: AppState, private queryService: QueryService) {}

  ngOnInit(): void {
    this.state.getLastResult().subscribe((result) => {
      let data = result;
      if (data != null) {
        this.rawResult = data;
        this.displayedColumns = data.vars;
        this.dataSource = new MatTableDataSource<any>(data.results);
        this.lastQuery = this.state.history[0] || this.lastQuery;
        this.lastQueryType = this.detectQueryType(this.lastQuery);
        this.exportFormat = this.canExport("csv") ? "csv" : "json";
      } else {
        this.rawResult = null;
        this.displayedColumns = [];
        this.dataSource = new MatTableDataSource<any>([]);
        this.lastQuery = "";
        this.lastQueryType = "UNKNOWN";
        this.exportFormat = "json";
      }
    });
  }

  selectEntity(column: string, value: string, e: any) {
    this.selectedEntity = { type: column, entity: value };
  }

  exportJson() {
    if (!this.rawResult) return;
    const content = JSON.stringify(this.rawResult, null, 2);
    this.downloadFile(
      content,
      "application/json",
      `query-results-${this.timestamp()}-${this.queryHash()}.json`
    );
  }

  exportCsv() {
    if (!this.canExport("csv")) {
      return;
    }
    const header = this.displayedColumns;
    const rows = this.dataSource.data.map((row) =>
      header.map((col) => this.csvEscape(row[col]))
    );
    const csv = [header.join(","), ...rows.map((r) => r.join(","))].join("\n");
    this.downloadFile(
      csv,
      "text/csv",
      `query-results-${this.timestamp()}-${this.queryHash()}.csv`
    );
  }

  exportSelected() {
    if (this.exportFormat === "csv") {
      this.exportCsv();
    } else if (this.exportFormat === "json") {
      this.exportJson();
    } else {
      this.exportRdf(this.exportFormat);
    }
  }

  canExport(
    format: "csv" | "json" | "turtle" | "jsonld" | "rdfxml" | "ntriples"
  ): boolean {
    if (format === "json") {
      return !!this.rawResult;
    }
    if (format !== "csv") {
      return (
        !!this.lastQuery &&
        (this.lastQueryType === "CONSTRUCT" ||
          this.lastQueryType === "DESCRIBE")
      );
    }
    return !!this.displayedColumns.length && this.dataSource.data.length > 0;
  }

  private csvEscape(value: any): string {
    if (value == null) return "";
    const str = String(value).replace(/"/g, '""');
    if (/[",\n]/.test(str)) {
      return `"${str}"`;
    }
    return str;
  }

  private downloadFile(content: string, type: string, filename: string) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  }

  private timestamp(): string {
    const now = new Date();
    const pad = (v: number) => v.toString().padStart(2, "0");
    return `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}-${pad(
      now.getHours()
    )}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
  }

  private queryHash(): string {
    const query =
      typeof this.rawResult?.query === "string"
        ? this.rawResult.query
        : this.state.history[0] || "";
    let hash = 0;
    for (let i = 0; i < query.length; i += 1) {
      hash = (hash << 5) - hash + query.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash).toString(16);
  }

  private exportRdf(format: "turtle" | "jsonld" | "rdfxml" | "ntriples") {
    if (!this.lastQuery) {
      return;
    }
    const acceptMap: Record<string, { accept: string; ext: string }> = {
      turtle: { accept: "text/turtle", ext: "ttl" },
      jsonld: { accept: "application/ld+json", ext: "jsonld" },
      rdfxml: { accept: "application/rdf+xml", ext: "rdf" },
      ntriples: { accept: "application/n-triples", ext: "nt" },
    };
    const target = acceptMap[format];
    this.queryService.executeSparql(this.lastQuery, target.accept).subscribe({
      next: (payload: string) => {
        this.downloadFile(
          payload,
          target.accept,
          `query-results-${this.timestamp()}-${this.queryHash()}.${target.ext}`
        );
      },
    });
  }

  private detectQueryType(query: string): "SELECT" | "ASK" | "CONSTRUCT" | "DESCRIBE" | "UNKNOWN" {
    if (!query) return "UNKNOWN";
    const stripped = query.replace(/#.*/gm, "").trim().toUpperCase();
    const keyword = stripped.match(
      /\b(SELECT|ASK|CONSTRUCT|DESCRIBE|INSERT|DELETE|WITH|LOAD|CLEAR|CREATE|DROP|COPY|MOVE|ADD)\b/
    );
    if (!keyword) return "UNKNOWN";
    if (["INSERT", "DELETE", "WITH", "LOAD", "CLEAR", "CREATE", "DROP", "COPY", "MOVE", "ADD"].includes(keyword[1])) {
      return "UNKNOWN";
    }
    return keyword[1] as "SELECT" | "ASK" | "CONSTRUCT" | "DESCRIBE";
  }
}
