import { Injectable } from "@angular/core";
import { BehaviorSubject } from "rxjs";

@Injectable({ providedIn: "root" })
export class AppState {
  private historySubject = new BehaviorSubject<string[]>([]);
  history$ = this.historySubject.asObservable();

  private resultSubject = new BehaviorSubject<any>(null);
  result$ = this.resultSubject.asObservable();

  get history(): string[] {
    return this.historySubject.value;
  }
  get lastResult(): any {
    return this.resultSubject.value;
  }

  addToHistory(q: string) {
    const current = [...this.historySubject.value];
    if (!current.includes(q)) current.unshift(q);
    this.historySubject.next(current.slice(0, 20));
  }
  getLastResult() {
    return this.resultSubject;
  }
  setLastResult(res: any) {
    this.resultSubject.next(res);
  }
}
