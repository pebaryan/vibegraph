import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { GraphService, Triple } from '@app/services/graph.service';
import { SearchService } from '@app/services/search.service';
import { QueryService } from '@app/services/query.service';
import { Prefix, PrefixService } from '@app/services/prefix.service';
import { Observable, of } from 'rxjs';
import { debounceTime, distinctUntilChanged, map, switchMap } from 'rxjs/operators';

@Component({
  selector: 'app-add-triple',
  templateUrl: './add-triple.component.html',
  styleUrls: ['./add-triple.component.scss']
})
export class AddTripleComponent implements OnInit {
  @Input() graphId!: string;
  @Output() tripleAdded = new EventEmitter<void>();

  tripleForm: FormGroup;
  prefixes: Prefix[] = [];
  subjectOptions$: Observable<any[]> = of([]);
  objectOptions$: Observable<any[]> = of([]);
  predicateOptions: string[] = [];
  filteredPredicateOptions$: Observable<string[]> = of([]);

  constructor(
    private graphService: GraphService,
    private searchService: SearchService,
    private queryService: QueryService,
    private prefixService: PrefixService,
    private fb: FormBuilder
  ) {
    this.tripleForm = this.fb.group({
      subject: new FormControl('', Validators.required),
      predicate: new FormControl('', Validators.required),
      object: new FormControl('', Validators.required)
    });
  }

  ngOnInit(): void {
    this.prefixService.getPrefixes().subscribe((data) => {
      this.prefixes = data;
      this.setupAutocomplete();
      this.loadPredicates();
    });
  }

  private setupAutocomplete() {
    this.subjectOptions$ = this.tripleForm.get('subject')!.valueChanges.pipe(
      debounceTime(200),
      distinctUntilChanged(),
      switchMap((value: string) => this.searchEntities(value))
    );

    this.objectOptions$ = this.tripleForm.get('object')!.valueChanges.pipe(
      debounceTime(200),
      distinctUntilChanged(),
      switchMap((value: string) => this.searchEntities(value))
    );

    this.filteredPredicateOptions$ = this.tripleForm.get('predicate')!.valueChanges.pipe(
      debounceTime(100),
      distinctUntilChanged(),
      map((value: string) => this.filterPredicates(value))
    );
  }

  private searchEntities(value: string): Observable<any[]> {
    const term = (value || '').toString().trim();
    if (!term || term.length < 2) {
      return of([]);
    }
    return this.searchService.search(term).pipe(
      map((res) => (res?.results ?? []).map((r: any) => this.toSuggestion(r)))
    );
  }

  private toSuggestion(result: any) {
    const iri = result?.iri || '';
    const prefixed = this.prefixIt(iri);
    const label = result?.label && result.label !== iri ? result.label : prefixed;
    return {
      value: prefixed,
      label,
      sub: result?.label ? prefixed : ''
    };
  }

  private loadPredicates() {
    const query = 'SELECT DISTINCT ?p WHERE { ?s ?p ?o } LIMIT 200';
    this.queryService.execute(query).subscribe({
      next: (data) => {
        const preds = (data?.results ?? []).map((b: any) => b.p);
        this.predicateOptions = preds.map((p: string) => this.prefixIt(p));
      },
      error: () => {
        this.predicateOptions = [];
      }
    });
  }

  private filterPredicates(value: string): string[] {
    const term = (value || '').toString().toLowerCase();
    if (!term) return this.predicateOptions.slice(0, 20);
    return this.predicateOptions.filter((p) => p.toLowerCase().includes(term)).slice(0, 50);
  }

  private prefixIt(uri: string): string {
    let result = uri;
    this.prefixes.every((p) => {
      if (uri.startsWith(p.uri)) {
        result = uri.replace(p.uri, p.prefix + ':');
        return false;
      }
      return true;
    });
    return result;
  }

  addTriple() {
    this.graphService
      .createTriple(this.graphId, this.tripleForm.getRawValue() as Triple)
      .subscribe(() => {
        this.tripleForm.patchValue({ subject: '', predicate: '', object: '' });
        this.tripleAdded.emit();
      });
  }
}
