import { Component, EventEmitter, Input, OnChanges, Output, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, ValidationErrors, ValidatorFn, Validators } from '@angular/forms';

import { ReporteGerencial, ReporteGerencialCreate, ReporteGerencialUpdate } from '../../../core/models';
import { AuthService } from '../../../core/services/auth.service';

const periodoValido: ValidatorFn = (group): ValidationErrors | null => {
  const inicio = group.get('periodo_inicio')?.value;
  const fin = group.get('periodo_fin')?.value;
  if (inicio && fin && fin < inicio) {
    return { periodoInvalido: true };
  }
  return null;
};

@Component({
  selector: 'app-reporte-form',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './reporte-form.component.html',
})
export class ReporteFormComponent implements OnChanges {
  @Input() open = false;
  @Input() reporte: ReporteGerencial | null = null;
  @Input() saving = false;

  @Output() save = new EventEmitter<ReporteGerencialCreate | ReporteGerencialUpdate>();
  @Output() cancelled = new EventEmitter<void>();

  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);

  readonly form = this.fb.nonNullable.group(
    {
      id_usuario: [null as number | null, [Validators.required, Validators.min(1)]],
      tipo_reporte: ['rendimiento', Validators.required],
      periodo_inicio: ['', Validators.required],
      periodo_fin: ['', Validators.required],
    },
    { validators: periodoValido },
  );

  ngOnChanges(): void {
    if (this.reporte) {
      this.form.patchValue({
        id_usuario: this.reporte.id_usuario,
        tipo_reporte: this.reporte.tipo_reporte,
        periodo_inicio: this.reporte.periodo_inicio,
        periodo_fin: this.reporte.periodo_fin,
      });
    } else {
      this.form.reset({
        id_usuario: this.authService.usuario()?.id ?? null,
        tipo_reporte: 'rendimiento',
        periodo_inicio: '',
        periodo_fin: '',
      });
    }
  }

  submit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.save.emit(this.form.getRawValue() as ReporteGerencialCreate);
  }
}
