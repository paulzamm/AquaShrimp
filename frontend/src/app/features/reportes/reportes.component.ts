import { DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';

import { ReporteGerencial, ReporteGerencialCreate, ReporteGerencialUpdate, TipoReporte } from '../../core/models';
import { NotificationService } from '../../core/services/notification.service';
import { ReporteGerencialService } from '../../core/services/reporte-gerencial.service';
import { ConfirmDialogComponent } from '../../shared/components/confirm-dialog/confirm-dialog.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';
import { ReporteFormComponent } from './reporte-form/reporte-form.component';

const ICONO_POR_TIPO: Record<TipoReporte, string> = {
  rendimiento: 'trending_up',
  alertas: 'notifications',
  alimentacion: 'set_meal',
};

@Component({
  selector: 'app-reportes',
  standalone: true,
  imports: [DatePipe, LoadingSpinnerComponent, EmptyStateComponent, ReporteFormComponent, ConfirmDialogComponent],
  templateUrl: './reportes.component.html',
})
export class ReportesComponent implements OnInit {
  private readonly reporteService = inject(ReporteGerencialService);
  private readonly notifications = inject(NotificationService);

  readonly loading = signal(true);
  readonly reportes = signal<ReporteGerencial[]>([]);
  readonly filtroTipo = signal<TipoReporte | ''>('');

  readonly formOpen = signal(false);
  readonly enEdicion = signal<ReporteGerencial | null>(null);
  readonly saving = signal(false);
  readonly aEliminar = signal<ReporteGerencial | null>(null);

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.loading.set(true);
    this.reporteService.list({ limit: 200, tipo_reporte: this.filtroTipo() || undefined }).subscribe({
      next: (reportes) => {
        this.reportes.set(reportes);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  onFiltroChange(value: string): void {
    this.filtroTipo.set(value as TipoReporte | '');
    this.cargar();
  }

  icono(tipo: TipoReporte): string {
    return ICONO_POR_TIPO[tipo] ?? 'description';
  }

  abrirCrear(): void {
    this.enEdicion.set(null);
    this.formOpen.set(true);
  }

  abrirEditar(reporte: ReporteGerencial): void {
    this.enEdicion.set(reporte);
    this.formOpen.set(true);
  }

  guardar(payload: ReporteGerencialCreate | ReporteGerencialUpdate): void {
    this.saving.set(true);
    const editing = this.enEdicion();
    const request = editing
      ? this.reporteService.update(editing.id, payload)
      : this.reporteService.create(payload as ReporteGerencialCreate);

    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.formOpen.set(false);
        this.notifications.success(editing ? 'Reporte actualizado.' : 'Reporte generado.');
        this.cargar();
      },
      error: () => this.saving.set(false),
    });
  }

  confirmarEliminar(reporte: ReporteGerencial): void {
    this.aEliminar.set(reporte);
  }

  eliminar(): void {
    const reporte = this.aEliminar();
    if (!reporte) return;
    this.reporteService.delete(reporte.id).subscribe({
      next: () => {
        this.notifications.success('Reporte eliminado.');
        this.aEliminar.set(null);
        this.cargar();
      },
      error: () => this.aEliminar.set(null),
    });
  }
}
