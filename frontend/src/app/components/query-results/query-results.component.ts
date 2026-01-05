import { Component, OnInit } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { Triple } from "@app/services/graph.service";
import { AppState } from "@app/state/app.state";

@Component({
  selector: "app-query-results",
  templateUrl: "./query-results.component.html",
  styleUrls: ["./query-results.component.scss"],
})
export class QueryResultsComponent implements OnInit {
  selectedEntity: any = null;
  displayedColumns: string[] = [];
  dataSource = new MatTableDataSource<any>([]);

  constructor(public state: AppState) {}

  ngOnInit(): void {
    this.state.getLastResult().subscribe((result) => {
      let data = result;
      if (data != null) {
        this.displayedColumns = data.vars;
        this.dataSource = new MatTableDataSource<any>(data.results);
      }
    });
  }

  selectEntity(column: string, value: string, e: any) {
    this.selectedEntity = { type: column, entity: value };
  }
}
