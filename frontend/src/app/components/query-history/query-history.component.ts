import { Component } from '@angular/core';
import { AppState } from '@app/state/app.state';
@Component({
  selector: 'app-query-history',
  templateUrl: './query-history.component.html',
  styleUrls: ['./query-history.component.css']
})
export class QueryHistoryComponent {
  constructor(public state: AppState) {}
}
