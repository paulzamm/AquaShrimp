import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';

import {
  Piscina,
  RecomendacionAlimentacion,
  RecomendacionAlimentacionCreate,
  RecomendacionAlimentacionUpdate,
} from '../../core/models';
import { NotificationService } from '../../core/services/notification.service';
import { PiscinaService } from '../../core/services/piscina.service';
import { RecomendacionAlimentacionService } from '../../core/services/recomendacion-alimentacion.service';
import { ConfirmDialogComponent } from '../../shared/components/confirm-dialog/confirm-dialog.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';
import { AlimentacionFormComponent } from './alimentacion-form/alimentacion-form.component';

@Component({
  selector: 'app-alimentacion',
  standalone: true,
  imports: [
    LoadingSpinnerComponent,
    EmptyStateComponent,
    StatusBadgeComponent,
    AlimentacionFormComponent,
    ConfirmDialogComponent,
  ],
  templateUrl: './alimentacion.component.html',
})
export class AlimentacionComponent implements OnInit {
  private readonly recomendacionService = inject(RecomendacionAlimentacionService);
  private readonly piscinaService = inject(PiscinaService);
  private readonly notifications = inject(NotificationService);

  readonly loading = signal(true);
  readonly recomendaciones = signal<RecomendacionAlimentacion[]>([]);
  readonly piscinas = signal<Piscina[]>([]);

  readonly formOpen = signal(false);
  readonly enEdicion = signal<RecomendacionAlimentacion | null>(null);
  readonly saving = signal(false);
  readonly aEliminar = signal<RecomendacionAlimentacion | null>(null);

  private readonly piscinaPorId = computed(() => new Map(this.piscinas().map((p) => [p.id, p])));

  readonly pendientes = computed(() => this.recomendaciones().filter((r) => r.estado === 'pendiente'));
  readonly totalKgPendiente = computed(() => this.pendientes().reduce((sum, r) => sum + r.cantidad_kg, 0));
  readonly aplicadasCount = computed(
    () => this.recomendaciones().filter((r) => r.estado === 'aplicada').length,
  );

  readonly recomendacionesOrdenadas = computed(() =>
    [...this.recomendaciones()].sort((a, b) => (b.fecha_generacion ?? b.created_at).localeCompare(a.fecha_generacion ?? a.created_at)),
  );

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.loading.set(true);
    forkJoin({
      recomendaciones: this.recomendacionService.list({ limit: 300 }),
      piscinas: this.piscinaService.list({ limit: 300 }),
    }).subscribe({
      next: ({ recomendaciones, piscinas }) => {
        this.recomendaciones.set(recomendaciones);
        this.piscinas.set(piscinas);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  codigoPiscina(idPiscina: number): string {
    return this.piscinaPorId().get(idPiscina)?.codigo ?? `#${idPiscina}`;
  }

  abrirCrear(): void {
    this.enEdicion.set(null);
    this.formOpen.set(true);
  }

  abrirEditar(recomendacion: RecomendacionAlimentacion): void {
    this.enEdicion.set(recomendacion);
    this.formOpen.set(true);
  }

  cambiarEstado(recomendacion: RecomendacionAlimentacion, estado: RecomendacionAlimentacion['estado']): void {
    this.recomendacionService.update(recomendacion.id, { estado }).subscribe({
      next: () => {
        this.notifications.success(estado === 'aplicada' ? 'Recomendación aplicada.' : 'Recomendación rechazada.');
        this.cargar();
      },
    });
  }

  guardar(payload: RecomendacionAlimentacionCreate | RecomendacionAlimentacionUpdate): void {
    this.saving.set(true);
    const editing = this.enEdicion();
    const request = editing
      ? this.recomendacionService.update(editing.id, payload)
      : this.recomendacionService.create(payload as RecomendacionAlimentacionCreate);

    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.formOpen.set(false);
        this.notifications.success(editing ? 'Recomendación actualizada.' : 'Recomendación creada.');
        this.cargar();
      },
      error: () => this.saving.set(false),
    });
  }

  confirmarEliminar(recomendacion: RecomendacionAlimentacion): void {
    this.aEliminar.set(recomendacion);
  }

  eliminar(): void {
    const recomendacion = this.aEliminar();
    if (!recomendacion) return;
    this.recomendacionService.delete(recomendacion.id).subscribe({
      next: () => {
        this.notifications.success('Recomendación eliminada.');
        this.aEliminar.set(null);
        this.cargar();
      },
      error: () => this.aEliminar.set(null),
    });
  }
}
