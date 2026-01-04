import { Component } from '@angular/core';
import { AppState } from '@app/state/app.state';

@Component({
  selector: 'app-query-results',
  templateUrl: './query-results.component.html',
  styleUrls: ['./query-results.component.scss']
})
export class QueryResultsComponent {
  constructor(public state: AppState) {}
}
