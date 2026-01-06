import { Component, OnInit } from "@angular/core";
import { GraphService } from "../../services/graph.service";
import { PrefixService, Prefix } from "../../services/prefix.service";
import { MatDialog } from "@angular/material/dialog";
import { PrefixDialogComponent } from "../prefix-dialog/prefix-dialog.component";

@Component({
  selector: "app-settings",
  templateUrl: "./settings.component.html",
  styleUrls: ["./settings.component.scss"],
})
export class SettingsComponent implements OnInit {
  loading = false;
  prefixes: Prefix[] = [];
  loadingPrefixes = false;

  constructor(
    private graphService: GraphService,
    private prefixService: PrefixService,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.loadPrefixes();
  }

  reindexAll() {
    if (!confirm("Re‑index all graphs? This may take a few minutes.")) {
      return;
    }
    this.loading = true;
    this.graphService.reindexAll().subscribe(
      () => {
        this.loading = false;
        alert("Re‑indexed all graphs successfully.");
      },
      () => {
        this.loading = false;
        alert("Failed to re‑index graphs.");
      }
    );
  }

  loadPrefixes() {
    this.loadingPrefixes = true;
    this.prefixService.getPrefixes().subscribe(
      (data) => {
        this.prefixes = data;
        this.loadingPrefixes = false;
      },
      () => {
        this.loadingPrefixes = false;
      }
    );
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
}
