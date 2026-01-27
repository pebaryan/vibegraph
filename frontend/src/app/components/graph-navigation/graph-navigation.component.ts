import { Component, OnInit } from "@angular/core";
import { MatTableDataSource } from "@angular/material/table";
import { GraphService, Triple } from "@app/services/graph.service";
import { QueryService } from "@app/services/query.service";
import { ActivatedRoute } from "@angular/router";
import { Prefix, PrefixService } from "@app/services/prefix.service";
import { FormControl } from "@angular/forms";
import { MatSnackBar } from "@angular/material/snack-bar";
import { MatDialog } from "@angular/material/dialog";
import { ConfirmDialogComponent } from "../confirm-dialog/confirm-dialog.component";

@Component({
  selector: "app-graph-navigation",
  templateUrl: "./graph-navigation.component.html",
  styleUrls: ["./graph-navigation.component.scss"],
})
export class GraphNavigationComponent implements OnInit {
  selectedEntity: any = null;
  displayedColumns: string[] = [];
  dataSource = new MatTableDataSource<Triple>([]);
  filterValue = "";

  graphId = "default";

  triples: Triple[] = [];
  newSubject = "";
  newPredicate = "";
  newObject = "";

  focus: string = "Graph entities";
  focusValue: string = "";
  prefixes: Prefix[] = [];
  priorityPredicateUris: string[] = [];
  labelCtrl = new FormControl("");
  useLangCtrl = new FormControl(false);
  langCtrl = new FormControl("");
  useDatatypeCtrl = new FormControl(false);
  datatypeCtrl = new FormControl("");
  savingLabel = false;

  constructor(
    private graphService: GraphService,
    private queryService: QueryService,
    private prefixService: PrefixService,
    private route: ActivatedRoute,
    private snackBar: MatSnackBar,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.graphId = this.route.snapshot.queryParamMap.get("id");
    this.loadFocus();
    this.prefixService.getPrefixes().subscribe((data) => {
      this.prefixes = data;
      this.priorityPredicateUris = this.resolvePriorityPredicateUris();
    });
    this.dataSource.filterPredicate = (data: any, filter: string) => {
      const term = filter.trim().toLowerCase();
      if (!term) return true;
      return Object.values(data).some((value) =>
        String(value).toLowerCase().includes(term)
      );
    };
  }

  loadFocus(){
    const value = this.route.snapshot.queryParamMap.get("focusValue") || this.focusValue;
    if (value) {
      this.focusValue = value;
      this.fetchTriplesByEntity(value);
    } else this.fetchClasses();
  }

  clearFocus() {
    this.focusValue = "";
    this.selectedEntity = null;
    this.filterValue = "";
    this.dataSource.filter = "";
    this.labelCtrl.setValue("");
    this.useLangCtrl.setValue(false);
    this.langCtrl.setValue("");
    this.useDatatypeCtrl.setValue(false);
    this.datatypeCtrl.setValue("");
    this.fetchClasses();
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

  private resolvePriorityPredicateUris(): string[] {
    const stored = localStorage.getItem("predicatePriorityPrefixes");
    const raw = stored && stored.trim().length > 0 ? stored : "rdf,rdfs,owl";
    const entries = raw
      .split(",")
      .map((p) => p.trim())
      .filter((p) => p.length > 0);
    const uris: string[] = [];
    entries.forEach((entry) => {
      if (entry.includes("http://") || entry.includes("https://")) {
        uris.push(entry);
        return;
      }
      const match = this.prefixes.find((p) => p.prefix === entry);
      if (match) {
        uris.push(match.uri);
      }
    });
    return uris;
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
      this.displayedColumns = ["subject", "predicate", "object", "actions"];
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
      this.triples = this.orderTriplesByFocus(this.triples, term);
      this.displayedColumns = ["subject", "predicate", "object", "actions"];
      this.dataSource = new MatTableDataSource<Triple>(this.triples);
    });
  }

  /** Handle entity selection */
  selectEntity(column: string, value: string, e: any) {
    this.selectedEntity = { type: column, entity: value };
    this.focus = this.prefixIt(value);
    this.focusValue = value;
    this.labelCtrl.setValue("");
    this.useLangCtrl.setValue(false);
    this.langCtrl.setValue("");
    this.useDatatypeCtrl.setValue(false);
    this.datatypeCtrl.setValue("");
    this.fetchTriplesByEntity(value);
  }

  private orderTriplesByFocus(triples: Triple[], focus: string): Triple[] {
    if (!focus) return triples;
    const rank = (t: Triple) => {
      if (t.subject === focus) return 0;
      if (t.predicate === focus) return 1;
      if (t.object === focus) return 2;
      return 3;
    };
    const isSemanticPred = (predicate: string) =>
      this.priorityPredicateUris.some((uri) => predicate.startsWith(uri));

    return [...triples].sort((a, b) => {
      const ra = rank(a);
      const rb = rank(b);
      if (ra !== rb) return ra - rb;
      if (ra === 0) {
        const aSem = isSemanticPred(a.predicate);
        const bSem = isSemanticPred(b.predicate);
        if (aSem !== bSem) return aSem ? -1 : 1;
      }
      return 0;
    });
  }

  isFocusedCell(value: any): boolean {
    if (!this.focusValue || value == null) {
      return false;
    }
    return String(value) === this.focusValue;
  }

  isLiteral(value: any): boolean {
    if (value == null) return false;
    const str = String(value);
    if (str.startsWith("_:")) return false;
    if (str.includes("://")) return false;
    if (str.includes(":") && !str.includes(" ")) return false;
    return true;
  }

  displayValue(column: string, value: any): string {
    if (column === "object" && this.isLiteral(value)) {
      return `"${value}"`;
    }
    return this.prefixIt(value);
  }

  applyFilter(value: string) {
    this.filterValue = value;
    this.dataSource.filter = value.trim().toLowerCase();
  }

  addLabel() {
    const label = (this.labelCtrl.value || "").toString().trim();
    if (!this.focusValue) {
      this.snackBar.open("Select an entity first.", "Dismiss", { duration: 4000 });
      return;
    }
    if (!label) {
      this.snackBar.open("Label cannot be empty.", "Dismiss", { duration: 4000 });
      return;
    }
    if (this.useLangCtrl.value && this.useDatatypeCtrl.value) {
      this.snackBar.open("Choose either language tag or datatype.", "Dismiss", {
        duration: 4000,
      });
      return;
    }
    if (this.useLangCtrl.value && !this.langCtrl.value) {
      this.snackBar.open("Language tag is required.", "Dismiss", {
        duration: 4000,
      });
      return;
    }
    if (this.useDatatypeCtrl.value && !this.datatypeCtrl.value) {
      this.snackBar.open("Datatype is required.", "Dismiss", {
        duration: 4000,
      });
      return;
    }
    this.savingLabel = true;
    const lang = (this.langCtrl.value || "").toString().trim();
    const dtype = (this.datatypeCtrl.value || "").toString().trim();
    let objectValue = label;
    if (this.useLangCtrl.value) {
      objectValue = `"${label}"@${lang}`;
    } else if (this.useDatatypeCtrl.value) {
      objectValue = `"${label}"^^${dtype}`;
    }
    this.graphService
      .createTriple(this.graphId, {
        subject: this.focusValue,
        predicate: "rdfs:label",
        object: objectValue,
      })
      .subscribe({
        next: () => {
          this.savingLabel = false;
          this.labelCtrl.setValue("");
          this.useLangCtrl.setValue(false);
          this.langCtrl.setValue("");
          this.useDatatypeCtrl.setValue(false);
          this.datatypeCtrl.setValue("");
          this.snackBar.open("Label added.", "Dismiss", { duration: 3000 });
          this.loadFocus();
        },
        error: () => {
          this.savingLabel = false;
          this.snackBar.open("Failed to add label.", "Dismiss", { duration: 4000 });
        },
      });
  }

  toggleLang(useLang: boolean) {
    if (useLang) {
      this.useDatatypeCtrl.setValue(false);
      this.datatypeCtrl.setValue("");
    }
  }

  toggleDatatype(useDatatype: boolean) {
    if (useDatatype) {
      this.useLangCtrl.setValue(false);
      this.langCtrl.setValue("");
    }
  }

  deleteTriple(row: Triple) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: "420px",
      data: {
        title: "Delete triple",
        message: "Delete this triple? This cannot be undone.",
        confirmText: "Delete",
        cancelText: "Cancel",
      },
    });

    dialogRef.afterClosed().subscribe((confirmed) => {
      if (!confirmed) return;
      this.graphService.deleteTriple(this.graphId, row).subscribe({
        next: () => {
          this.snackBar.open("Triple deleted.", "Dismiss", { duration: 3000 });
          this.loadFocus();
        },
        error: () => {
          this.snackBar.open("Failed to delete triple.", "Dismiss", {
            duration: 4000,
          });
        },
      });
    });
  }
}
