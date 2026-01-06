import { Component, OnInit } from "@angular/core";
import { GraphService } from "@app/services/graph.service";
import { QueryService } from "@app/services/query.service";
import { AppState } from "@app/state/app.state";
@Component({
  selector: "app-query-history",
  templateUrl: "./query-history.component.html",
  styleUrls: ["./query-history.component.scss"],
})
export class QueryHistoryComponent implements OnInit {
  graphs: any[] = [];
  queries: any[] = [];
  selectedGraph: string;
  constructor(
    public state: AppState,
    private graphService: GraphService,
    private queryService: QueryService
  ) {}
  ngOnInit(): void {
    this.graphService.listGraphs().subscribe((resp) => {
      console.log(resp);
      this.graphs = resp;
    });
  }
  loadHistory(graph_id) {
    console.log(graph_id);
    this.queryService.getHistory(graph_id).subscribe((resp) => {
      this.queries = resp;
    });
  }
}
