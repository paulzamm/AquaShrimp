import { Component, EventEmitter, Input, OnChanges, Output, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { Rol, Usuario, UsuarioCreate, UsuarioUpdate } from '../../../core/models';

@Component({
  selector: 'app-usuario-form',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './usuario-form.component.html',
})
export class UsuarioFormComponent implements OnChanges {
  @Input() open = false;
  @Input() usuario: Usuario | null = null;
  @Input() roles: Rol[] = [];
  @Input() saving = false;

  @Output() save = new EventEmitter<UsuarioCreate | UsuarioUpdate>();
  @Output() cancelled = new EventEmitter<void>();

  readonly showPassword = signal(false);

  private readonly fb = inject(FormBuilder);

  readonly form = this.fb.nonNullable.group({
    nombre: ['', Validators.required],
    correo: ['', [Validators.required, Validators.email]],
    contrasena: [''],
    id_rol: [0, [Validators.required, Validators.min(1)]],
    estado: ['activo', Validators.required],
  });

  ngOnChanges(): void {
    if (this.usuario) {
      this.form.patchValue({
        nombre: this.usuario.nombre,
        correo: this.usuario.correo,
        contrasena: '',
        id_rol: this.usuario.id_rol,
        estado: this.usuario.estado,
      });
      this.form.controls.contrasena.clearValidators();
    } else {
      this.form.reset({ nombre: '', correo: '', contrasena: '', id_rol: 0, estado: 'activo' });
      this.form.controls.contrasena.setValidators([Validators.required, Validators.minLength(8)]);
    }
    this.form.controls.contrasena.updateValueAndValidity();
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    const payload: UsuarioCreate | UsuarioUpdate = { ...value };
    if (this.usuario && !value.contrasena) {
      delete (payload as UsuarioUpdate).contrasena;
    }
    this.save.emit(payload);
  }

  togglePassword(): void {
    this.showPassword.update((value) => !value);
  }
}
