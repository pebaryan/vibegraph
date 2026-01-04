import { Component } from '@angular/core';
import { QueryService } from '@app/services/query.service';
import { AppState } from '@app/state/app.state';

@Component({
  selector: 'app-query-editor',
  templateUrl: './query-editor.component.html',
  styleUrls: ['./query-editor.component.css']
})
import { AfterViewInit } from '@angular/core';
import * as monaco from 'monaco-editor';

export class QueryEditorComponent implements AfterViewInit {
  query: string = '';
  loading = false;
  error: string | null = null;
  public editorOptions = {
    theme: 'vs-light',
    language: 'sparql',
    automaticLayout: true
  };

  constructor(private queryService: QueryService, public state: AppState) {}

  ngAfterViewInit() {
    // Register SPARQL language if not already registered
    if (!monaco.languages.getLanguages().some(l => l.id === 'sparql')) {
      monaco.languages.register({ id: 'sparql' });
    }
  }

  execute() {
    this.loading = true;
    this.error = null;
    this.queryService.execute(this.query).subscribe(
      res => {
        this.loading = false;
        this.state.setLastResult(res);
        this.state.addToHistory(this.query);
      },
      err => {
        this.loading = false;
        this.error = err?.message || 'Execution failed';
      }
    );
  }
}
