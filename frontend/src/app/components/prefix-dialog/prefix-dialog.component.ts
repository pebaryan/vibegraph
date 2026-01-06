import { Component, Inject } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

export interface PrefixData {
  prefix: string;
  uri: string;
}

@Component({
  selector: 'app-prefix-dialog',
  templateUrl: './prefix-dialog.component.html',
  styleUrls: ['./prefix-dialog.component.scss'],
})
export class PrefixDialogComponent {
  form: FormGroup;
  isEdit: boolean;

  constructor(
    public dialogRef: MatDialogRef<PrefixDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: PrefixData,
    private fb: FormBuilder
  ) {
    this.isEdit = !!data.prefix;
    this.form = this.fb.group({
      prefix: [data.prefix, Validators.required],
      uri: [data.uri, Validators.required],
    });
  }

  onSave() {
    if (this.form.valid) {
      this.dialogRef.close(this.form.value);
    }
  }

  onCancel() {
    this.dialogRef.close();
  }
}
