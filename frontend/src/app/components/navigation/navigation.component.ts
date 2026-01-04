import { Component } from "@angular/core";
import { OnInit } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { GraphService, Triple } from "@app/services/graph.service";
import { ActivatedRoute } from "@angular/router";

@Component({
  selector: "app-navigation",
  templateUrl: "./navigation.component.html",
  styleUrls: ["./navigation.component.scss"],
})
export class NavigationComponent implements OnInit {
  selectedEntity: any = null;
  displayedColumns: string[] = [];
  dataSource = new MatTableDataSource<Triple>([]);

  graphId: string = "default";

  triples: Triple[] = [];

  constructor(
    private graphService: GraphService,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.graphId = this.route.snapshot.queryParams["id"] || this.graphId;
    this.graphService.getTriples(this.graphId).subscribe((data) => {
      this.triples = data.triples;
      this.displayedColumns = ["subject", "predicate", "object"];
      this.dataSource = new MatTableDataSource<Triple>(this.triples);
    });
  }

  selectEntity(column, value, e: any) {
    this.selectedEntity = { type: column, entity: value, e: e };
  }
}
