import { Component } from '@angular/core';
import { QueryService } from '@app/services/query.service';
import { AppState } from '@app/state/app.state';

@Component({
  selector: 'app-query-editor',
  templateUrl: './query-editor.component.html',
  styleUrls: ['./query-editor.component.css']
})
export class QueryEditorComponent {
  query: string = '';
  loading = false;
  error: string | null = null;

  constructor(private queryService: QueryService, public state: AppState) {}

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
