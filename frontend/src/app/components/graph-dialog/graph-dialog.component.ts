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
    format: ['ttl'],
    guessedFormat: [''],
    availableFormats: [],
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

  /**
   * Guess RDF format from file extension.
   */
  private guessFormat(file: File): string {
    const ext = file.name.split('.').pop()?.toLowerCase();
    const mapping: { [key: string]: string } = {
      ttl: 'ttl',
      turtle: 'ttl',
      trig: 'trig',
      nt: 'nt',
      rdf: 'xml',
      xml: 'xml',
      owl: 'xml',
      jsonld: 'jsonld',
      json: 'jsonld',
    };
    return mapping[ext ?? ''] ?? 'ttl';
  }

  /**
   * Update form controls when a file is selected.
   */
  onFileSelected(event: any) {
    const file = event.target.files[0];
    this.nameForm.patchValue({ file });
    const guessed = this.guessFormat(file);
    this.nameForm.patchValue({ guessedFormat: guessed, format: guessed });
    // expose supported formats for radio group
    this.nameForm.patchValue({
      availableFormats: ['ttl', 'trig', 'nt', 'xml', 'jsonld'],
    });
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
          const format = this.nameForm.get('format')?.value;
          this.graphService.uploadGraphFile(res.graph_id, this.nameForm.get('file')?.value as File, format).subscribe(() => {
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
