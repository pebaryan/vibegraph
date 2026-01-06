import { Component } from '@angular/core';
import { GraphService } from '../../services/graph.service';

@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent {
  loading = false;

  constructor(private graphService: GraphService) {}

  reindexAll() {
    if (!confirm('Re‑index all graphs? This may take a few minutes.')) {
      return;
    }
    this.loading = true;
    this.graphService.reindexAll().subscribe(
      () => {
        this.loading = false;
        alert('Re‑indexed all graphs successfully.');
      },
      () => {
        this.loading = false;
        alert('Failed to re‑index graphs.');
      }
    );
  }
}
