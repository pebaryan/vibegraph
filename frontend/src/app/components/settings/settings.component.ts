import { Component, OnInit } from "@angular/core";
import { GraphService } from "../../services/graph.service";
import { PrefixService, Prefix } from "../../services/prefix.service";
import { MatDialog } from "@angular/material/dialog";
import { PrefixDialogComponent } from "../prefix-dialog/prefix-dialog.component";
import { MatSnackBar } from "@angular/material/snack-bar";
import { ConfirmDialogComponent } from "../confirm-dialog/confirm-dialog.component";
import { SnackbarComponent } from "../snackbar/snackbar.component";
import { FormControl } from "@angular/forms";

@Component({
  selector: "app-settings",
  templateUrl: "./settings.component.html",
  styleUrls: ["./settings.component.scss"],
})
export class SettingsComponent implements OnInit {
  loading = false;
  clearing = false;
  prefixes: Prefix[] = [];
  loadingPrefixes = false;
  predicatePriorityCtrl = new FormControl("rdf,rdfs,owl");

  constructor(
    private graphService: GraphService,
    private prefixService: PrefixService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.loadPrefixes();
    const stored = localStorage.getItem("predicatePriorityPrefixes");
    if (stored) {
      this.predicatePriorityCtrl.setValue(stored);
    }
  }

  reindexAll() {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: "420px",
      data: {
        title: "Re-index all graphs",
        message: "Re-index all graphs? This may take a few minutes.",
        confirmText: "Re-index",
        cancelText: "Cancel",
      },
    });

    dialogRef.afterClosed().subscribe((confirmed) => {
      if (!confirmed) {
        return;
      }
      this.loading = true;
      this.graphService.reindexAll().subscribe(
        () => {
          this.loading = false;
          this.openSnack("Re‑indexed all graphs successfully.");
        },
        () => {
          this.loading = false;
          this.openSnack("Failed to re‑index graphs.");
        }
      );
    });
  }

  clearAllGraphs() {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: "420px",
      data: {
        title: "Clear all graphs",
        message:
          "This deletes all graphs, their triples, and query history. This cannot be undone.",
        confirmText: "Clear All",
        cancelText: "Cancel",
      },
    });

    dialogRef.afterClosed().subscribe((confirmed) => {
      if (!confirmed) {
        return;
      }
      this.clearing = true;
      this.graphService
        .clearAll({ clear_history: true, clear_index: true })
        .subscribe({
          next: () => {
            this.clearing = false;
            this.openSnack("All graphs cleared.");
          },
          error: () => {
            this.clearing = false;
            this.openSnack("Failed to clear graphs.");
          },
        });
    });
  }

  private openSnack(message: string) {
    this.snackBar.openFromComponent(SnackbarComponent, {
      data: { message, actionText: "Dismiss" },
      duration: 4000,
    });
  }

  loadPrefixes() {
    this.loadingPrefixes = true;
    this.prefixService.getPrefixes().subscribe({
      next: (data) => {
        this.prefixes = data;
        this.loadingPrefixes = false;
      },
      error: () => {
        this.loadingPrefixes = false;
      },
    });
  }

  editPrefix(prefix: Prefix) {
    const dialogRef = this.dialog.open(PrefixDialogComponent, {
      width: "400px",
      data: { ...prefix },
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.prefixService
          .updatePrefix(result.prefix, result.uri)
          .subscribe(() => this.loadPrefixes());
      }
    });
  }

  deletePrefix(prefix: Prefix) {
    if (!confirm(`Delete prefix ${prefix.prefix}?`)) return;
    this.prefixService
      .deletePrefix(prefix.prefix)
      .subscribe(() => this.loadPrefixes());
  }

  addPrefix() {
    const dialogRef = this.dialog.open(PrefixDialogComponent, {
      width: "400px",
      data: { prefix: "", uri: "" },
    });
    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.prefixService
          .addPrefix(result.prefix, result.uri)
          .subscribe(() => this.loadPrefixes());
      }
    });
  }

  savePredicatePriority() {
    const value = (this.predicatePriorityCtrl.value || "").toString().trim();
    localStorage.setItem("predicatePriorityPrefixes", value);
    this.openSnack("Predicate priority updated.");
  }
}
