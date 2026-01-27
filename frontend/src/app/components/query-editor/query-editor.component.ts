import { Component, OnInit } from "@angular/core";
import { QueryService } from "@app/services/query.service";
import { AppState } from "@app/state/app.state";
import { AfterViewInit } from "@angular/core";
import { Prefix, PrefixService } from "@app/services/prefix.service";

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
    public state: AppState
  ) {}

  ngOnInit() {
    this.prefixService.getPrefixes().subscribe({
      next: (data) => (this.prefixes = data),
      error: () => (this.prefixes = []),
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
        this.error = err?.error || "Execution failed";
      },
    });
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
