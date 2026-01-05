import { Component, OnInit } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { GraphService, Triple } from "@app/services/graph.service";
import { QueryService } from "@app/services/query.service";
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

  graphId = "default";

  triples: Triple[] = [];
  newSubject = "";
  newPredicate = "";
  newObject = "";

  constructor(
    private graphService: GraphService,
    private queryService: QueryService,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.fetchClasses();
  }

  /** Helper to format a term as a URI or literal */
  private formatTerm(term: string): string {
    if (term.startsWith("<") && term.endsWith(">")) return term;
    if (term.includes("http://") || term.includes("https://")) return `<${term}>`;
    return `"${term}"`;
  }

  /** Fetch all distinct classes */
  fetchClasses() {
    const query = `SELECT DISTINCT ?class WHERE { ?s a ?class }`;
    this.queryService.execute(query).subscribe((data) => {
      const classes = data.results.bindings.map((b: any) => ({
        subject: b.class.value,
        predicate: "",
        object: "",
      }));
      this.triples = classes;
      this.displayedColumns = ["class"];
      this.dataSource = new MatTableDataSource<Triple>(this.triples);
    });
  }

  /** Fetch triples that contain the selected term */
  fetchTriplesByEntity(term: string) {
    const query = `
      SELECT ?s ?p ?o WHERE {
        ?s ?p ?o .
        FILTER ( ?s = ${this.formatTerm(term)} ||
                ?p = ${this.formatTerm(term)} ||
                ?o = ${this.formatTerm(term)} )
      }
    `;
    this.queryService.execute(query).subscribe((data) => {
      const triples = data.results.bindings.map((b: any) => ({
        subject: b.s.value,
        predicate: b.p.value,
        object: b.o.value,
      }));
      this.triples = triples;
      this.displayedColumns = ["subject", "predicate", "object"];
      this.dataSource = new MatTableDataSource<Triple>(this.triples);
    });
  }

  /** Handle entity selection */
  selectEntity(column: string, value: string, e: any) {
    this.selectedEntity = { type: column, entity: value };
    this.fetchTriplesByEntity(value);
  }

  /** Add a new triple */
  addTriple() {
    const triple = {
      subject: this.newSubject,
      predicate: this.newPredicate,
      object: this.newObject,
    };
    this.graphService.createTriple(this.graphId, triple).subscribe(() => {
      this.fetchClasses();
      this.newSubject = "";
      this.newPredicate = "";
      this.newObject = "";
    });
  }
}
