import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { GraphService, Graph } from '@app/services/graph.service';
import { GraphDialogComponent } from '../graph-dialog/graph-dialog.component';
import { ConfirmDialogComponent } from '../confirm-dialog/confirm-dialog.component';
import { Router } from '@angular/router';

@Component({
  selector: 'app-graph-list',
  templateUrl: './graph-list.component.html',
  styleUrls: ['./graph-list.component.scss']
})
export class GraphListComponent implements OnInit {
  graphs: Graph[] = [];
  displayedColumns: string[] = ['name', 'created_at', 'actions'];

  constructor(
    private graphService: GraphService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.loadGraphs();
  }

  loadGraphs(): void {
    this.graphService.listGraphs().subscribe({
      next: (data) => (this.graphs = data),
      error: (err) => this.showError(err)
    });
  }

  createGraph(): void {
    const dialogRef = this.dialog.open(GraphDialogComponent, {
      width: '400px',
      data: { mode: 'create' }
    });

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.showMessage('Graph created');
        this.loadGraphs();
      }
    });
  }

  renameGraph(graph: Graph): void {
    const dialogRef = this.dialog.open(GraphDialogComponent, {
      width: '400px',
      data: { mode: 'edit', graph }
    });

    dialogRef.afterClosed().subscribe((name) => {
      if (name) {
        this.graphService.updateGraph(graph.graph_id, name).subscribe({
          next: () => {
            this.showMessage('Graph renamed');
            this.loadGraphs();
          },
          error: (err) => this.showError(err)
        });
      }
    });
  }

  deleteGraph(graph: Graph): void {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '420px',
      data: {
        title: 'Delete graph',
        message: `Delete graph '${graph.name}'? This cannot be undone.`,
        confirmText: 'Delete',
        cancelText: 'Cancel',
      },
    });

    dialogRef.afterClosed().subscribe((confirmed) => {
      if (!confirmed) {
        return;
      }
      this.graphService.deleteGraph(graph.graph_id).subscribe({
        next: () => {
          this.showMessage('Graph deleted');
          this.loadGraphs();
        },
        error: (err) => this.showError(err)
      });
    });
  }

  examineGraph(graph: Graph): void {
    this.router.navigate(['/graph-navigation'], { queryParams: { id: graph.graph_id } });
  }

  viewGraph(graph: Graph): void {
    this.router.navigate(['/graph'], { queryParams: { id: graph.graph_id } });
  }

  private showMessage(msg: string): void {
    const ref = this.snackBar.open(msg, 'Close', { duration: 3000 });
    ref.onAction().subscribe(() => ref.dismiss());
  }

  private showError(err: any): void {
    const ref = this.snackBar.open(`Error: ${err}`, 'Close', { duration: 5000 });
    ref.onAction().subscribe(() => ref.dismiss());
  }
}
