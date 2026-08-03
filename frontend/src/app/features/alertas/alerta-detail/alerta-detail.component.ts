import { Component, EventEmitter, Input, OnChanges, Output, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

import { AccionCorrectivaCreate, Alerta, EstadoAlerta } from '../../../core/models';
import { AuthService } from '../../../core/services/auth.service';

export interface ResolverAlertaPayload {
  accion: AccionCorrectivaCreate;
  nuevoEstado: EstadoAlerta;
}

@Component({
  selector: 'app-alerta-detail',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './alerta-detail.component.html',
})
export class AlertaDetailComponent implements OnChanges {
  @Input() open = false;
  @Input() alerta: Alerta | null = null;
  @Input() saving = false;

  @Output() resolve = new EventEmitter<ResolverAlertaPayload>();
  @Output() cancelled = new EventEmitter<void>();

  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);

  readonly form = this.fb.nonNullable.group({
    descripcion: ['', Validators.required],
    resultado: [''],
    nuevoEstado: ['atendida' as EstadoAlerta, Validators.required],
  });

  ngOnChanges(): void {
    if (!this.alerta) {
      this.form.reset({ descripcion: '', resultado: '', nuevoEstado: 'atendida' });
    }
  }

  submit(): void {
    const idUsuario = this.authService.usuario()?.id;
    if (this.form.invalid || !this.alerta || !idUsuario) {
      this.form.markAllAsTouched();
      return;
    }
    const value = this.form.getRawValue();
    this.resolve.emit({
      accion: {
        id_alerta: this.alerta.id,
        id_usuario: idUsuario,
        descripcion: value.descripcion,
        resultado: value.resultado || null,
        estado: 'completada',
      },
      nuevoEstado: value.nuevoEstado,
    });
  }
}
