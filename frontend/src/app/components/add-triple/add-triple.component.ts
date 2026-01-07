import { Component, Input, Output, EventEmitter } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { GraphService, Triple } from '@app/services/graph.service';

@Component({
  selector: 'app-add-triple',
  templateUrl: './add-triple.component.html',
  styleUrls: ['./add-triple.component.scss']
})
export class AddTripleComponent {
  @Input() graphId!: string;
  @Output() tripleAdded = new EventEmitter<void>();

  tripleForm: FormGroup;

  constructor(private graphService: GraphService, private fb: FormBuilder) {
    this.tripleForm = this.fb.group({
      subject: new FormControl('', Validators.required),
      predicate: new FormControl('', Validators.required),
      object: new FormControl('', Validators.required)
    });
  }

  addTriple() {
    this.graphService
      .createTriple(this.graphId, this.tripleForm.getRawValue() as Triple)
      .subscribe(() => {
        this.tripleForm.patchValue({ subject: '', predicate: '', object: '' });
        this.tripleAdded.emit();
      });
  }
}
