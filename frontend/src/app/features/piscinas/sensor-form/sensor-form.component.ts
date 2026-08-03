import { Component, EventEmitter, Input, OnChanges, Output, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { Sensor, SensorCreate, SensorUpdate } from '../../../core/models';

@Component({
  selector: 'app-sensor-form',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './sensor-form.component.html',
})
export class SensorFormComponent implements OnChanges {
  @Input() open = false;
  @Input() sensor: Sensor | null = null;
  @Input() idPiscina!: number;
  @Input() saving = false;

  @Output() save = new EventEmitter<SensorCreate | SensorUpdate>();
  @Output() cancelled = new EventEmitter<void>();

  private readonly fb = inject(FormBuilder);

  readonly form = this.fb.nonNullable.group({
    tipo: ['temperatura', Validators.required],
    ubicacion: [''],
    estado: ['activo', Validators.required],
    unidad_medida: ['°C', Validators.required],
    fecha_instalacion: [''],
  });

  ngOnChanges(): void {
    if (this.sensor) {
      this.form.patchValue({
        tipo: this.sensor.tipo,
        ubicacion: this.sensor.ubicacion ?? '',
        estado: this.sensor.estado,
        unidad_medida: this.sensor.unidad_medida,
        fecha_instalacion: this.sensor.fecha_instalacion ?? '',
      });
    } else {
      this.form.reset({ tipo: 'temperatura', ubicacion: '', estado: 'activo', unidad_medida: '°C', fecha_instalacion: '' });
    }
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    this.save.emit({
      id_piscina: this.idPiscina,
      ...value,
      tipo: value.tipo as SensorCreate['tipo'],
      estado: value.estado as SensorCreate['estado'],
      ubicacion: value.ubicacion || null,
      fecha_instalacion: value.fecha_instalacion || null,
    });
  }
}
