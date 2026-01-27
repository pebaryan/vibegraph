import { Component, OnInit } from "@angular/core";
import { FormControl, Validators } from "@angular/forms";
import { GraphService, Graph } from "@app/services/graph.service";
import { LlmService } from "@app/services/llm.service";

interface ExtractedEntity {
  id: string;
  text: string;
  type?: string;
}

interface ExtractedRelationship {
  subject: string;
  predicate: string;
  object: string;
}

interface Recommendation {
  iri: string;
  label: string;
  prefixed?: string | null;
  score: number;
}

@Component({
  selector: "app-extract",
  templateUrl: "./extract.component.html",
  styleUrls: ["./extract.component.scss"],
})
export class ExtractComponent implements OnInit {
  textCtrl = new FormControl("", { nonNullable: true, validators: [Validators.required] });
  graphs: Graph[] = [];
  selectedGraphId: string | null = null;
  extracting = false;
  linking = false;
  error: string | null = null;

  entities: ExtractedEntity[] = [];
  relationships: ExtractedRelationship[] = [];
  selectedEntityIds = new Set<string>();
  recommendations: Record<string, Recommendation[]> = {};
  get hasRecommendations(): boolean {
    return Object.keys(this.recommendations).length > 0;
  }

  constructor(private graphService: GraphService, private llmService: LlmService) {}

  ngOnInit(): void {
    this.graphService.listGraphs().subscribe({
      next: (graphs) => {
        this.graphs = graphs;
        if (!this.selectedGraphId && graphs.length > 0) {
          this.selectedGraphId = graphs[0].graph_id;
        }
      },
      error: () => (this.graphs = []),
    });
  }

  get entityMap(): Record<string, string> {
    return this.entities.reduce((acc, entity) => {
      acc[entity.id] = entity.text;
      return acc;
    }, {} as Record<string, string>);
  }

  toggleAll(selectAll: boolean): void {
    this.selectedEntityIds.clear();
    if (selectAll) {
      this.entities.forEach((entity) => this.selectedEntityIds.add(entity.id));
    }
  }

  toggleEntity(entityId: string, checked: boolean): void {
    if (checked) {
      this.selectedEntityIds.add(entityId);
    } else {
      this.selectedEntityIds.delete(entityId);
    }
  }

  extract(): void {
    this.error = null;
    if (this.textCtrl.invalid) {
      this.error = "Enter text to extract entities.";
      return;
    }
    this.extracting = true;
    this.entities = [];
    this.relationships = [];
    this.selectedEntityIds.clear();
    this.recommendations = {};

    this.llmService.extractEntities(this.textCtrl.value).subscribe({
      next: (res) => {
        this.entities = Array.isArray(res?.entities) ? res.entities : [];
        this.relationships = Array.isArray(res?.relationships) ? res.relationships : [];
        this.entities.forEach((entity) => this.selectedEntityIds.add(entity.id));
      },
      error: (err) => {
        this.error = err?.error?.error || "Failed to extract entities.";
      },
      complete: () => (this.extracting = false),
    });
  }

  recommend(): void {
    this.error = null;
    if (!this.selectedGraphId) {
      this.error = "Select a graph for entity linking.";
      return;
    }
    const selected = this.entities.filter((entity) => this.selectedEntityIds.has(entity.id));
    if (!selected.length) {
      this.error = "Select at least one entity to link.";
      return;
    }
    this.linking = true;
    this.recommendations = {};

    this.llmService.linkEntities(this.selectedGraphId, selected).subscribe({
      next: (res) => {
        this.recommendations = res?.recommendations || {};
      },
      error: (err) => {
        this.error = err?.error?.error || "Failed to recommend entities.";
      },
      complete: () => (this.linking = false),
    });
  }
}
