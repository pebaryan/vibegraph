import { Component, Inject } from '@angular/core';
// import { HttpClient } from '@angular/common/http';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { GraphService } from '../../services/graph.service';
import { FormBuilder, Validators } from '@angular/forms';

export interface GraphDialogData {
  mode: 'create' | 'edit';
  graph?: { graph_id: string; name: string; };
}

@Component({
  selector: 'app-graph-dialog',
  templateUrl: './graph-dialog.component.html',
  styleUrls: ['./graph-dialog.component.scss'],
})
export class GraphDialogComponent {
  nameForm = this.fb.group({
    name: ['', Validators.required],
    dataSource: ['none'],
    file: [null],
    sparqlRead: [''],
    sparqlUpdate: [''],
    authType: ['None'],
    username: [''],
    password: [''],
    token: [''],
  });

  constructor(
    private fb: FormBuilder,
    private graphService: GraphService,
    public dialogRef: MatDialogRef<GraphDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: GraphDialogData
  ) {
    if (data.mode === 'edit' && data.graph) {
      this.nameForm.patchValue({ name: data.graph.name });
    }
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    this.nameForm.patchValue({ file });
  }

  onSave(): void {
    if (!this.nameForm.valid) {
      return;
    }

    const form = this.nameForm.value;
    const payload: any = {
      name: form.name,
      sparql_read: form.sparqlRead || undefined,
      sparql_update: form.sparqlUpdate || undefined,
      auth_type: form.authType,
      auth_info:
        form.authType !== 'None'
          ? {
              username: form.username,
              password: form.password,
              token: form.token,
            }
          : undefined,
    };


    if (this.data.mode === 'create') {
      this.graphService.createGraph(payload).subscribe((res: any) => {
        if (form.dataSource === 'file' && this.nameForm.get('file')?.value) {
          this.graphService.uploadGraphFile(res.graph_id, this.nameForm.get('file')?.value as File).subscribe(() => {
            this.dialogRef.close(res);
          });
        } else {
          this.dialogRef.close(res);
        }
      });
    } else {
      // For edit mode, simply close with updated values for now
      this.dialogRef.close(this.nameForm.value);
    }
  }

  onCancel(): void {
    this.dialogRef.close();
  }
}
