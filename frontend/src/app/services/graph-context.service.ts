/**
 * Graph context service for managing graph state and operations
 */
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

export interface GraphContext {
  currentGraphId: string | null;
  currentGraphName: string | null;
}

@Injectable({
  providedIn: 'root'
})
export class GraphContextService {
  private _graphContext = new BehaviorSubject<GraphContext>({
    currentGraphId: null,
    currentGraphName: null
  });

  public graphContext$ = this._graphContext.asObservable();

  setCurrentGraph(graphId: string, graphName: string): void {
    this._graphContext.next({
      currentGraphId: graphId,
      currentGraphName: graphName
    });
  }

  clearCurrentGraph(): void {
    this._graphContext.next({
      currentGraphId: null,
      currentGraphName: null
    });
  }

  getCurrentGraphId(): string | null {
    return this._graphContext.value.currentGraphId;
  }

  getCurrentGraphName(): string | null {
    return this._graphContext.value.currentGraphName;
  }
}