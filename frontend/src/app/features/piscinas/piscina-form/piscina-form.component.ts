import { Component, EventEmitter, Input, OnChanges, Output, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { Piscina, PiscinaCreate, PiscinaUpdate } from '../../../core/models';

@Component({
  selector: 'app-piscina-form',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './piscina-form.component.html',
})
export class PiscinaFormComponent implements OnChanges {
  @Input() open = false;
  @Input() piscina: Piscina | null = null;
  @Input() saving = false;

  @Output() save = new EventEmitter<PiscinaCreate | PiscinaUpdate>();
  @Output() cancelled = new EventEmitter<void>();

  private readonly fb = inject(FormBuilder);

  readonly form = this.fb.nonNullable.group({
    codigo: ['', Validators.required],
    ubicacion: ['', Validators.required],
    area_m2: [0, [Validators.required, Validators.min(0.01)]],
    profundidad: [0, [Validators.required, Validators.min(0.01)]],
    estado: ['activa', Validators.required],
    fecha_inicio_ciclo: [''],
  });

  ngOnChanges(): void {
    if (this.piscina) {
      this.form.patchValue({
        codigo: this.piscina.codigo,
        ubicacion: this.piscina.ubicacion,
        area_m2: this.piscina.area_m2,
        profundidad: this.piscina.profundidad,
        estado: this.piscina.estado,
        fecha_inicio_ciclo: this.piscina.fecha_inicio_ciclo ?? '',
      });
    } else {
      this.form.reset({ codigo: '', ubicacion: '', area_m2: 0, profundidad: 0, estado: 'activa', fecha_inicio_ciclo: '' });
    }
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    this.save.emit({
      ...value,
      estado: value.estado as PiscinaCreate['estado'],
      fecha_inicio_ciclo: value.fecha_inicio_ciclo || null,
    });
  }
}
