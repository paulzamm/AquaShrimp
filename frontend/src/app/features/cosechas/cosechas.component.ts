import { DatePipe, DecimalPipe } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';

import { Cosecha, CosechaCreate, CosechaUpdate, Piscina } from '../../core/models';
import { CosechaService } from '../../core/services/cosecha.service';
import { NotificationService } from '../../core/services/notification.service';
import { PiscinaService } from '../../core/services/piscina.service';
import { ConfirmDialogComponent } from '../../shared/components/confirm-dialog/confirm-dialog.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';
import { CosechaFormComponent } from './cosecha-form/cosecha-form.component';

interface ProduccionPorPiscina {
  codigo: string;
  totalKg: number;
  porcentaje: number;
}

@Component({
  selector: 'app-cosechas',
  standalone: true,
  imports: [DatePipe, DecimalPipe, LoadingSpinnerComponent, EmptyStateComponent, CosechaFormComponent, ConfirmDialogComponent],
  templateUrl: './cosechas.component.html',
})
export class CosechasComponent implements OnInit {
  private readonly cosechaService = inject(CosechaService);
  private readonly piscinaService = inject(PiscinaService);
  private readonly notifications = inject(NotificationService);

  readonly loading = signal(true);
  readonly cosechas = signal<Cosecha[]>([]);
  readonly piscinas = signal<Piscina[]>([]);

  readonly formOpen = signal(false);
  readonly enEdicion = signal<Cosecha | null>(null);
  readonly saving = signal(false);
  readonly aEliminar = signal<Cosecha | null>(null);

  private readonly piscinaPorId = computed(() => new Map(this.piscinas().map((p) => [p.id, p])));

  readonly biomasaTotal = computed(() => this.cosechas().reduce((sum, c) => sum + c.biomasa_kg, 0));

  readonly tallaPromedio = computed(() => {
    const valores = this.cosechas().map((c) => c.talla_promedio).filter((v): v is number => v != null);
    if (!valores.length) return null;
    return valores.reduce((sum, v) => sum + v, 0) / valores.length;
  });

  readonly produccionPorPiscina = computed<ProduccionPorPiscina[]>(() => {
    const piscinas = this.piscinaPorId();
    const totales = new Map<number, number>();
    for (const cosecha of this.cosechas()) {
      totales.set(cosecha.id_piscina, (totales.get(cosecha.id_piscina) ?? 0) + cosecha.biomasa_kg);
    }
    const max = Math.max(1, ...totales.values());
    return [...totales.entries()]
      .map(([idPiscina, totalKg]) => ({
        codigo: piscinas.get(idPiscina)?.codigo ?? `#${idPiscina}`,
        totalKg,
        porcentaje: (totalKg / max) * 100,
      }))
      .sort((a, b) => b.totalKg - a.totalKg)
      .slice(0, 6);
  });

  readonly cosechasOrdenadas = computed(() =>
    [...this.cosechas()].sort((a, b) => b.fecha_cosecha.localeCompare(a.fecha_cosecha)),
  );

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.loading.set(true);
    forkJoin({
      cosechas: this.cosechaService.list({ limit: 300 }),
      piscinas: this.piscinaService.list({ limit: 300 }),
    }).subscribe({
      next: ({ cosechas, piscinas }) => {
        this.cosechas.set(cosechas);
        this.piscinas.set(piscinas);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  codigoPiscina(idPiscina: number): string {
    return this.piscinaPorId().get(idPiscina)?.codigo ?? `#${idPiscina}`;
  }

  barHeight(porcentaje: number): number {
    return Math.max(8, porcentaje * 1.1);
  }

  abrirCrear(): void {
    this.enEdicion.set(null);
    this.formOpen.set(true);
  }

  abrirEditar(cosecha: Cosecha): void {
    this.enEdicion.set(cosecha);
    this.formOpen.set(true);
  }

  guardar(payload: CosechaCreate | CosechaUpdate): void {
    this.saving.set(true);
    const editing = this.enEdicion();
    const request = editing ? this.cosechaService.update(editing.id, payload) : this.cosechaService.create(payload as CosechaCreate);

    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.formOpen.set(false);
        this.notifications.success(editing ? 'Cosecha actualizada.' : 'Cosecha registrada.');
        this.cargar();
      },
      error: () => this.saving.set(false),
    });
  }

  confirmarEliminar(cosecha: Cosecha): void {
    this.aEliminar.set(cosecha);
  }

  eliminar(): void {
    const cosecha = this.aEliminar();
    if (!cosecha) return;
    this.cosechaService.delete(cosecha.id).subscribe({
      next: () => {
        this.notifications.success('Cosecha eliminada.');
        this.aEliminar.set(null);
        this.cargar();
      },
      error: () => this.aEliminar.set(null),
    });
  }
}
