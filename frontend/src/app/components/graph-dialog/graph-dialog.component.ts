import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FormBuilder, Validators } from '@angular/forms';
import { GraphService } from '../services/graph.service';

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
    name: ['', Validators.required],
    dataSource: ['none'],
    file: [null],
    sparqlRead: [''],
    sparqlUpdate: [''],
    authType: ['None'],
    username: [''],
    password: [''],
    token: ['']
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
    if (this.nameForm.valid) {
      const form = this.nameForm.value;
      const payload: any = {
        name: form.name,
        sparql_read: form.sparqlRead || undefined,
        sparql_update: form.sparqlUpdate || undefined,
        auth_type: form.authType,
        auth_info: form.authType !== 'None' ? {
          username: form.authInfo?.username,
          password: form.authInfo?.password,
          token: form.authInfo?.token
        } : undefined
      };
      const url = '/api/graphs';
      if (this.data.mode === 'create') {
        this.http.post(url, payload).subscribe((res: any) => {
          if (form.dataSource === 'file' && this.nameForm.get('file')?.value) {
            const fd = new FormData();
            fd.append('file', this.nameForm.get('file')?.value);
            this.http.post(`/api/graphs/${res.graph_id}/upload`, fd).subscribe(() => {
              this.dialogRef.close(res);
            });
          } else {
            this.dialogRef.close(res);
          }
        });
      } else {
        // edit not implemented
        this.dialogRef.close();
      }
    }
  }

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
