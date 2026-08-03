import { Component, EventEmitter, Input, OnChanges, Output, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { Rol, RolCreate, RolUpdate } from '../../../core/models';

@Component({
  selector: 'app-rol-form',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './rol-form.component.html',
})
export class RolFormComponent implements OnChanges {
  @Input() open = false;
  @Input() rol: Rol | null = null;
  @Input() saving = false;

  @Output() save = new EventEmitter<RolCreate | RolUpdate>();
  @Output() cancelled = new EventEmitter<void>();

  private readonly fb = inject(FormBuilder);

  readonly form = this.fb.nonNullable.group({
    nombre_rol: ['', Validators.required],
    descripcion: [''],
    permisos: [''],
    estado: ['activo', Validators.required],
  });

  ngOnChanges(): void {
    if (this.rol) {
      this.form.patchValue({
        nombre_rol: this.rol.nombre_rol,
        descripcion: this.rol.descripcion ?? '',
        permisos: this.rol.permisos ?? '',
        estado: this.rol.estado,
      });
    } else {
      this.form.reset({ nombre_rol: '', descripcion: '', permisos: '', estado: 'activo' });
    }
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    this.save.emit({ ...value, descripcion: value.descripcion || null, permisos: value.permisos || null });
  }
}
