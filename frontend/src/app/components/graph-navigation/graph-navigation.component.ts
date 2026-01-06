import { Component, OnInit } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { GraphService, Triple } from "@app/services/graph.service";
import { QueryService } from "@app/services/query.service";
import { ActivatedRoute } from "@angular/router";
import { Prefix, PrefixService } from "@app/services/prefix.service";
import {
  FormBuilder,
  FormControl,
  FormGroup,
  Validators,
} from "@angular/forms";

@Component({
  selector: "app-graph-navigation",
  templateUrl: "./graph-navigation.component.html",
  styleUrls: ["./graph-navigation.component.scss"],
})
export class GraphNavigationComponent implements OnInit {
  selectedEntity: any = null;
  displayedColumns: string[] = [];
  dataSource = new MatTableDataSource<Triple>([]);

  graphId = "default";

  triples: Triple[] = [];
  newSubject = "";
  newPredicate = "";
  newObject = "";

  focus: string = "Graph entities";
  focusValue: string = "";
  prefixes: Prefix[] = [];
  tripleForm: FormGroup;

  constructor(
    private graphService: GraphService,
    private queryService: QueryService,
    private prefixService: PrefixService,
    private route: ActivatedRoute,
    private fb: FormBuilder
  ) {}

  ngOnInit() {
    this.tripleForm = this.fb.group({
      subject: new FormControl("", Validators.required),
      predicate: new FormControl("", Validators.required),
      object: new FormControl("", Validators.required),
    });
    this.tripleForm.enable();
    this.graphId = this.route.snapshot.queryParamMap.get("id");
    this.loadFocus();
    this.prefixService.getPrefixes().subscribe((data) => {
      this.prefixes = data;
    });
  }

  loadFocus(){
    const value = this.route.snapshot.queryParamMap.get("focusValue");
    if (value) {
      this.focusValue = value;
      this.fetchTriplesByEntity(value);
    } else this.fetchClasses();
  }

  prefixIt(uri: string): string {
    var result = uri;
    this.prefixes.every((p) => {
      if (uri.startsWith(p.uri)) {
        result = uri.replace(p.uri, p.prefix + ":");
        return false;
      }
      return true;
    });
    return result;
  }

  /** Helper to format a term as a URI or literal */
  private formatTerm(term: string): string {
    if (term.startsWith("<") && term.endsWith(">")) return term;
    if (term.includes("http://") || term.includes("https://"))
      return `<${term}>`;
    return `"${term}"`;
  }

  /** Fetch all distinct classes */
  fetchClasses() {
    const query = `SELECT DISTINCT ?class WHERE { ?s a ?class }`;
    this.queryService.execute(query).subscribe((data) => {
      console.log(data);
      if (data.count == 0) this.fetchTriplesLimited();
      else {
        this.displayedColumns = ["class"];
        this.dataSource = new MatTableDataSource<Triple>(data.results);
      }
    });
  }

  fetchTriplesLimited(limit: number = 10) {
    const query = `SELECT * WHERE { ?s ?p ?o } LIMIT ${limit}`;
    this.queryService.execute(query).subscribe((data) => {
      const classes = data.results.map((b: any) => ({
        subject: b.s,
        predicate: b.p,
        object: b.o,
      }));
      this.triples = classes;
      this.displayedColumns = ["subject", "predicate", "object"];
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
      data.results.forEach((b: any) => {
        if (b.p === "http://www.w3.org/2000/01/rdf-schema#label")
          this.focus = b.o;
      });
      this.triples = data.results.map((b: any) => ({
        subject: b.s,
        predicate: b.p,
        object: b.o,
      }));
      this.displayedColumns = ["subject", "predicate", "object"];
      this.dataSource = new MatTableDataSource<Triple>(this.triples);
    });
  }

  /** Handle entity selection */
  selectEntity(column: string, value: string, e: any) {
    this.selectedEntity = { type: column, entity: value };
    this.focus = this.prefixIt(value);
    this.focusValue = value;
    this.fetchTriplesByEntity(value);
  }

  /** Add a new triple */
  addTriple() {
    console.log(this.tripleForm.getRawValue());
    this.graphService
      .createTriple(this.graphId, this.tripleForm.getRawValue())
      .subscribe(() => {
        this.tripleForm.patchValue({ subject: "", predicate: "", object: "" });
        this.loadFocus();
      });
  }
}
