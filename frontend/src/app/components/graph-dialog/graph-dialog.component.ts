import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FormBuilder, Validators } from '@angular/forms';

export interface GraphDialogData {
  mode: 'create' | 'edit';
  graph?: { graph_id: string; name: string; };
}

@Component({
  selector: 'app-graph-dialog',
  templateUrl: './graph-dialog.component.html',
  styleUrls: ['./graph-dialog.component.scss']
})
export class GraphDialogComponent {
  nameForm = this.fb.group({
    name: ['', Validators.required]
  });

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<GraphDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: GraphDialogData
  ) {
    if (data.mode === 'edit' && data.graph) {
      this.nameForm.patchValue({ name: data.graph.name });
    }
  }

  onSave(): void {
    if (this.nameForm.valid) {
      this.dialogRef.close(this.nameForm.value.name);
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}
