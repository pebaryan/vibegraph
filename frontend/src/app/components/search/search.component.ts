import { Component, OnInit } from "@angular/core";
import { FormControl } from "@angular/forms";
import { debounceTime, distinctUntilChanged, switchMap } from "rxjs/operators";
import { SearchService } from "@app/services/search.service";
import { GraphService } from "@app/services/graph.service";
import { Prefix, PrefixService } from "@app/services/prefix.service";

@Component({
  selector: "app-search",
  templateUrl: "./search.component.html",
  styleUrls: ["./search.component.scss"],
})
export class SearchComponent implements OnInit {
  queryCtrl = new FormControl("");
  results: any[] = [];
  loading = false;
  error: string | null = null;
  readonly JSON = JSON;
  prefixes: Prefix[] = [];

  constructor(
    private prefixService: PrefixService,
    private searchService: SearchService
  ) {}

  ngOnInit(): void {
    this.queryCtrl.valueChanges
      .pipe(
        debounceTime(300),
        distinctUntilChanged(),
        switchMap((q) => this.performSearch(q))
      )
      .subscribe();
    this.prefixService.getPrefixes().subscribe((data) => {
      this.prefixes = data;
    });
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

  performSearch(q: string) {
    if (!q) {
      this.results = [];
      this.error = null;
      return [];
    }
    this.loading = true;
    this.error = null;
    return this.searchService.search(q).pipe(
      switchMap((res) => {
        console.log(res);
        this.results = res?.results ?? [];
        this.loading = false;
        return [];
      })
    );
  }
}
