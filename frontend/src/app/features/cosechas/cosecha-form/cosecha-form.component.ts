import { Component, EventEmitter, Input, OnChanges, Output, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { Cosecha, CosechaCreate, CosechaUpdate, Piscina } from '../../../core/models';

@Component({
  selector: 'app-cosecha-form',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './cosecha-form.component.html',
})
export class CosechaFormComponent implements OnChanges {
  @Input() open = false;
  @Input() cosecha: Cosecha | null = null;
  @Input() piscinas: Piscina[] = [];
  @Input() saving = false;

  @Output() save = new EventEmitter<CosechaCreate | CosechaUpdate>();
  @Output() cancelled = new EventEmitter<void>();

  private readonly fb = inject(FormBuilder);

  readonly form = this.fb.nonNullable.group({
    id_piscina: [0, [Validators.required, Validators.min(1)]],
    fecha_cosecha: ['', Validators.required],
    biomasa_kg: [0, [Validators.required, Validators.min(0.1)]],
    talla_promedio: [null as number | null],
    rendimiento: [null as number | null, [Validators.min(0), Validators.max(100)]],
    observaciones: [''],
  });

  ngOnChanges(): void {
    if (this.cosecha) {
      this.form.patchValue({
        id_piscina: this.cosecha.id_piscina,
        fecha_cosecha: this.cosecha.fecha_cosecha,
        biomasa_kg: this.cosecha.biomasa_kg,
        talla_promedio: this.cosecha.talla_promedio ?? null,
        rendimiento: this.cosecha.rendimiento ?? null,
        observaciones: this.cosecha.observaciones ?? '',
      });
    } else {
      this.form.reset({
        id_piscina: 0,
        fecha_cosecha: '',
        biomasa_kg: 0,
        talla_promedio: null,
        rendimiento: null,
        observaciones: '',
      });
    }
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    this.save.emit({ ...value, observaciones: value.observaciones || null });
  }
}
