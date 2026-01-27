import { Component, Inject } from "@angular/core";
import { MAT_SNACK_BAR_DATA, MatSnackBarRef } from "@angular/material/snack-bar";

export interface SnackbarData {
  message: string;
  actionText?: string;
}

@Component({
  selector: "app-snackbar",
  templateUrl: "./snackbar.component.html",
  styleUrls: ["./snackbar.component.scss"],
})
export class SnackbarComponent {
  message: string;
  actionText: string;

  constructor(
    private snackBarRef: MatSnackBarRef<SnackbarComponent>,
    @Inject(MAT_SNACK_BAR_DATA) data: SnackbarData
  ) {
    this.message = data.message;
    this.actionText = data.actionText || "Dismiss";
  }

  dismiss() {
    this.snackBarRef.dismiss();
  }
}
