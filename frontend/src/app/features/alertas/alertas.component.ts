import { DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';

import { Alerta, EstadoAlerta, SeveridadAlerta } from '../../core/models';
import { AccionCorrectivaService } from '../../core/services/accion-correctiva.service';
import { AlertaService } from '../../core/services/alerta.service';
import { NotificationService } from '../../core/services/notification.service';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';
import { AlertaDetailComponent, ResolverAlertaPayload } from './alerta-detail/alerta-detail.component';

@Component({
  selector: 'app-alertas',
  standalone: true,
  imports: [DatePipe, LoadingSpinnerComponent, EmptyStateComponent, StatusBadgeComponent, AlertaDetailComponent],
  templateUrl: './alertas.component.html',
})
export class AlertasComponent implements OnInit {
  private readonly alertaService = inject(AlertaService);
  private readonly accionService = inject(AccionCorrectivaService);
  private readonly notifications = inject(NotificationService);

  readonly loading = signal(true);
  readonly alertas = signal<Alerta[]>([]);
  readonly filtroEstado = signal<EstadoAlerta | ''>('activa');
  readonly filtroSeveridad = signal<SeveridadAlerta | ''>('');

  readonly detalleAbierto = signal(false);
  readonly alertaSeleccionada = signal<Alerta | null>(null);
  readonly guardando = signal(false);

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.loading.set(true);
    this.alertaService
      .list({
        limit: 200,
        estado: this.filtroEstado() || undefined,
        severidad: this.filtroSeveridad() || undefined,
      })
      .subscribe({
        next: (alertas) => {
          this.alertas.set(alertas);
          this.loading.set(false);
        },
        error: () => this.loading.set(false),
      });
  }

  onEstadoChange(value: string): void {
    this.filtroEstado.set(value as EstadoAlerta | '');
    this.cargar();
  }

  onSeveridadChange(value: string): void {
    this.filtroSeveridad.set(value as SeveridadAlerta | '');
    this.cargar();
  }

  abrirDetalle(alerta: Alerta): void {
    this.alertaSeleccionada.set(alerta);
    this.detalleAbierto.set(true);
  }

  cerrarDetalle(): void {
    this.detalleAbierto.set(false);
    this.alertaSeleccionada.set(null);
  }

  resolver(payload: ResolverAlertaPayload): void {
    const alerta = this.alertaSeleccionada();
    if (!alerta) return;
    this.guardando.set(true);

    this.accionService.create(payload.accion).subscribe({
      next: () => {
        this.alertaService.update(alerta.id, { estado: payload.nuevoEstado }).subscribe({
          next: () => {
            this.guardando.set(false);
            this.notifications.success('Acción registrada y alerta actualizada.');
            this.cerrarDetalle();
            this.cargar();
          },
          error: () => this.guardando.set(false),
        });
      },
      error: () => this.guardando.set(false),
    });
  }
}
