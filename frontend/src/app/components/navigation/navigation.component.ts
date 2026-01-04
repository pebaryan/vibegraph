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
  newSubject = "";
  newPredicate = "";
  newObject = "";

  constructor(
    private graphService: GraphService,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.fetchTriples();
  }

  fetchTriples() {
    this.graphId = this.route.snapshot.queryParams["id"] || this.graphId;
    this.graphService.getTriples(this.graphId).subscribe((data) => {
      this.triples = data.triples;
      this.displayedColumns = ["subject", "predicate", "object"];
      this.dataSource = new MatTableDataSource<Triple>(this.triples);
    });
  }

  selectEntity(column, value, e: any) {
    this.selectedEntity = { type: column, entity: value };
  }

  addTriple() {
    const triple = {
      subject: this.newSubject,
      predicate: this.newPredicate,
      object: this.newObject,
    };
    this.graphService.createTriple(this.graphId, triple).subscribe(() => {
      this.fetchTriples();
      this.newSubject = "";
      this.newPredicate = "";
      this.newObject = "";
    });
  }
}
