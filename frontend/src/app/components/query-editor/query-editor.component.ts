import { Component, OnInit } from "@angular/core";
import { QueryService } from "@app/services/query.service";
import { AppState } from "@app/state/app.state";
import { AfterViewInit } from "@angular/core";
import { Prefix, PrefixService } from "@app/services/prefix.service";
import { LlmService } from "@app/services/llm.service";
import { FormControl } from "@angular/forms";
import { GraphService, Graph } from "@app/services/graph.service";

@Component({
  selector: "app-query-editor",
  templateUrl: "./query-editor.component.html",
  styleUrls: ["./query-editor.component.scss"],
})
export class QueryEditorComponent implements AfterViewInit, OnInit {
  query: string = "SELECT * WHERE { ?s ?p ?o. }";
  loading = false;
  error: string | null = null;
  prefixes: Prefix[] = [];
  selectedHistory: string | null = null;
  questionCtrl = new FormControl("");
  generating = false;
  autoRepairCtrl = new FormControl(false);
  repairing = false;
  graphs: Graph[] = [];
  selectedGraphId: string | null = null;
  llmReplacements: Record<string, string> = {};
  llmInfo: string | null = null;
  templates = [
    {
      name: "Select (basic)",
      query: "SELECT ?s ?p ?o WHERE {\n  ?s ?p ?o .\n} LIMIT 50",
    },
    {
      name: "Ask (exists)",
      query: "ASK WHERE {\n  ?s ?p ?o .\n}",
    },
    {
      name: "Construct",
      query: "CONSTRUCT {\n  ?s ?p ?o .\n} WHERE {\n  ?s ?p ?o .\n} LIMIT 50",
    },
  ];
  public editorOptions = {
    theme: "vs-light",
    language: "sparql",
    scrollBeyondLastLine: false, // Prevents extra empty space at the bottom
    scrollbar: {
      alwaysConsumeMouseWheel: false, // This is the key setting!
    },
  };

  constructor(
    private queryService: QueryService,
    private prefixService: PrefixService,
    private llmService: LlmService,
    private graphService: GraphService,
    public state: AppState
  ) {}

  ngOnInit() {
    this.prefixService.getPrefixes().subscribe({
      next: (data) => (this.prefixes = data),
      error: () => (this.prefixes = []),
    });
    this.graphService.listGraphs().subscribe({
      next: (graphs) => {
        this.graphs = graphs;
        if (!this.selectedGraphId && graphs.length > 0) {
          this.selectedGraphId = graphs[0].graph_id;
        }
      },
      error: () => (this.graphs = []),
    });
  }

  ngAfterViewInit() {
    // Register SPARQL language if not already registered
    // if (!monaco.languages.getLanguages().some(l => l.id === 'sparql')) {
    //   monaco.languages.register({ id: 'sparql' });
    // }
  }

  execute() {
    this.loading = true;
    this.error = null;
    this.queryService.execute(this.query).subscribe({
      next: (res) => {
        this.loading = false;
        this.state.setLastResult(res);
        this.state.addToHistory(this.query);
      },
      error: (err) => {
        this.loading = false;
        this.error = this.formatError(err, "Execution failed");
        if (this.autoRepairCtrl.value) {
          this.repairQuery();
        }
      },
    });
  }

  generateFromQuestion() {
    const question = (this.questionCtrl.value || "").toString().trim();
    if (!question) {
      this.error = "Question is required.";
      return;
    }
    this.generating = true;
    this.error = null;
    this.llmReplacements = {};
    this.llmInfo = null;
    this.llmService.generateSparql(question, this.selectedGraphId).subscribe({
      next: (res) => {
        this.generating = false;
        if (res?.query) {
          this.query = res.query;
          if (res?.replacements && Object.keys(res.replacements).length > 0) {
            this.llmReplacements = res.replacements;
            this.llmInfo = "LLM auto‑replaced unknown terms.";
          }
        } else {
          this.error = "LLM did not return a query.";
        }
      },
      error: (err) => {
        this.generating = false;
        this.error = this.formatError(err, "Failed to generate query.");
      },
    });
  }

  repairQuery() {
    if (!this.query || !this.error) {
      this.error = this.error || "No error to repair.";
      return;
    }
    this.repairing = true;
    this.llmService.repairSparql(this.query, this.error).subscribe({
      next: (res) => {
        this.repairing = false;
        if (res?.query) {
          this.query = res.query;
          this.error = "Query repaired. Review before running.";
        } else {
          this.error = "LLM did not return a repaired query.";
        }
      },
      error: (err) => {
        this.repairing = false;
        this.error = this.formatError(err, "Failed to repair query.");
      },
    });
  }

  private formatError(err: any, fallback: string): string {
    if (!err) return fallback;
    if (typeof err.error === "string") return err.error;
    if (typeof err.message === "string") return err.message;
    if (err.error) {
      try {
        return JSON.stringify(err.error);
      } catch {
        return fallback;
      }
    }
    return fallback;
  }

  insertTemplate(template: string) {
    this.query = template;
  }

  insertPrefix(prefix: Prefix) {
    const line = `PREFIX ${prefix.prefix}: <${prefix.uri}>`;
    this.addPrefixes([line]);
  }

  insertAllPrefixes() {
    if (!this.prefixes.length) {
      return;
    }
    const lines = this.prefixes.map((p) => `PREFIX ${p.prefix}: <${p.uri}>`);
    this.addPrefixes(lines);
  }

  loadHistory() {
    if (this.selectedHistory) {
      this.query = this.selectedHistory;
    }
  }

  private addPrefixes(linesToAdd: string[]) {
    const queryText = this.query || "";
    const lines = queryText.split("\n");
    let i = 0;
    while (i < lines.length && lines[i].trim() === "") {
      i += 1;
    }
    let prefixEnd = i;
    while (
      prefixEnd < lines.length &&
      lines[prefixEnd].trim().toUpperCase().startsWith("PREFIX ")
    ) {
      prefixEnd += 1;
    }
    const existing = new Set(
      lines.slice(i, prefixEnd).map((line) => line.trim())
    );
    const newLines = linesToAdd.filter((line) => !existing.has(line));
    if (!newLines.length) {
      return;
    }
    const before = lines.slice(0, prefixEnd);
    const after = lines.slice(prefixEnd);
    const needsBlank =
      after.length > 0 && after[0].trim() !== "";
    const separator = needsBlank ? [""] : [];
    this.query = [...before, ...newLines, ...separator, ...after].join("\n");
  }
}
