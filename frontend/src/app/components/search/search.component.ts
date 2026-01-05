import { Component, OnInit } from '@angular/core';
import { FormControl } from '@angular/forms';
import { debounceTime, distinctUntilChanged, switchMap } from 'rxjs/operators';
import { SearchService } from '@app/services/search.service';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.scss']
})
export class SearchComponent implements OnInit {
  queryCtrl = new FormControl('');
  results: any[] = [];
  loading = false;
  error: string | null = null;
  readonly JSON=JSON

  constructor(private searchService: SearchService) {}

  ngOnInit(): void {
    this.queryCtrl.valueChanges.pipe(
      debounceTime(300),
      distinctUntilChanged(),
      switchMap((q) => this.performSearch(q))
    ).subscribe();
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
        console.log(res)
        this.results = res?.results ?? [];
        this.loading = false;
        return [];
      })
    );
  }
}
