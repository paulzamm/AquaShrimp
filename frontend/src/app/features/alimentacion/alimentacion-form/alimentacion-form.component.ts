import { Component, EventEmitter, Input, OnChanges, Output, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import {
  Piscina,
  RecomendacionAlimentacion,
  RecomendacionAlimentacionCreate,
  RecomendacionAlimentacionUpdate,
} from '../../../core/models';

@Component({
  selector: 'app-alimentacion-form',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './alimentacion-form.component.html',
})
export class AlimentacionFormComponent implements OnChanges {
  @Input() open = false;
  @Input() recomendacion: RecomendacionAlimentacion | null = null;
  @Input() piscinas: Piscina[] = [];
  @Input() saving = false;

  @Output() save = new EventEmitter<RecomendacionAlimentacionCreate | RecomendacionAlimentacionUpdate>();
  @Output() cancelled = new EventEmitter<void>();

  private readonly fb = inject(FormBuilder);

  readonly form = this.fb.nonNullable.group({
    id_piscina: [0, [Validators.required, Validators.min(1)]],
    cantidad_kg: [0, [Validators.required, Validators.min(0.1)]],
    frecuencia: ['diaria', Validators.required],
    criterio: [''],
    estado: ['pendiente' as RecomendacionAlimentacion['estado'], Validators.required],
  });

  ngOnChanges(): void {
    if (this.recomendacion) {
      this.form.patchValue({
        id_piscina: this.recomendacion.id_piscina,
        cantidad_kg: this.recomendacion.cantidad_kg,
        frecuencia: this.recomendacion.frecuencia,
        criterio: this.recomendacion.criterio ?? '',
        estado: this.recomendacion.estado,
      });
    } else {
      this.form.reset({ id_piscina: 0, cantidad_kg: 0, frecuencia: 'diaria', criterio: '', estado: 'pendiente' });
    }
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    this.save.emit({ ...value, criterio: value.criterio || null });
  }
}
