import { DatePipe } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { ChartData } from 'chart.js';
import { forkJoin } from 'rxjs';

import { LecturaSensor, Piscina, PiscinaCreate, PiscinaUpdate, Sensor, SensorCreate, SensorUpdate } from '../../core/models';
import { LecturaService } from '../../core/services/lectura.service';
import { NotificationService } from '../../core/services/notification.service';
import { PiscinaService } from '../../core/services/piscina.service';
import { SensorService } from '../../core/services/sensor.service';
import { ConfirmDialogComponent } from '../../shared/components/confirm-dialog/confirm-dialog.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';
import { LineChartComponent } from '../../shared/components/line-chart/line-chart.component';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';
import { PiscinaFormComponent } from './piscina-form/piscina-form.component';
import { SensorFormComponent } from './sensor-form/sensor-form.component';

@Component({
  selector: 'app-piscinas',
  standalone: true,
  imports: [
    DatePipe,
    LoadingSpinnerComponent,
    EmptyStateComponent,
    StatusBadgeComponent,
    LineChartComponent,
    PiscinaFormComponent,
    SensorFormComponent,
    ConfirmDialogComponent,
  ],
  templateUrl: './piscinas.component.html',
})
export class PiscinasComponent implements OnInit {
  private readonly piscinaService = inject(PiscinaService);
  private readonly sensorService = inject(SensorService);
  private readonly lecturaService = inject(LecturaService);
  private readonly notifications = inject(NotificationService);

  readonly loading = signal(true);
  readonly piscinas = signal<Piscina[]>([]);
  readonly selectedId = signal<number | null>(null);

  readonly sensoresSeleccionada = signal<Sensor[]>([]);
  readonly lecturasSeleccionada = signal<LecturaSensor[]>([]);
  readonly loadingDetalle = signal(false);

  readonly piscinaFormOpen = signal(false);
  readonly piscinaEnEdicion = signal<Piscina | null>(null);
  readonly savingPiscina = signal(false);
  readonly piscinaAEliminar = signal<Piscina | null>(null);

  readonly sensorFormOpen = signal(false);
  readonly sensorEnEdicion = signal<Sensor | null>(null);
  readonly savingSensor = signal(false);
  readonly sensorAEliminar = signal<Sensor | null>(null);

  readonly selected = computed(() => this.piscinas().find((p) => p.id === this.selectedId()) ?? null);

  readonly ultimasLecturas = computed(() =>
    [...this.lecturasSeleccionada()]
      .sort((a, b) => (b.fecha_hora ?? b.created_at).localeCompare(a.fecha_hora ?? a.created_at))
      .slice(0, 6),
  );

  readonly chartData = computed<ChartData<'line'>>(() => {
    const sensores = new Map(this.sensoresSeleccionada().map((s) => [s.id, s]));
    const porTipo = new Map<string, LecturaSensor[]>();
    for (const lectura of this.lecturasSeleccionada()) {
      const tipo = sensores.get(lectura.id_sensor)?.tipo;
      if (!tipo) continue;
      const arr = porTipo.get(tipo) ?? [];
      arr.push(lectura);
      porTipo.set(tipo, arr);
    }

    const labelsSet = new Set<string>();
    for (const lecturas of porTipo.values()) {
      for (const l of lecturas) labelsSet.add(l.fecha_hora ?? l.created_at);
    }
    const labels = [...labelsSet].sort();
    const palette: Record<string, string> = { temperatura: '#00696c', oxigeno_disuelto: '#004655', ph: '#226150' };

    const datasets = [...porTipo.entries()].map(([tipo, lecturas]) => {
      const porFecha = new Map(lecturas.map((l) => [l.fecha_hora ?? l.created_at, l.valor]));
      return {
        label: tipo.replace('_', ' '),
        data: labels.map((label) => porFecha.get(label) ?? null),
        borderColor: palette[tipo] ?? '#6f797c',
        backgroundColor: (palette[tipo] ?? '#6f797c') + '33',
        tension: 0.3,
      };
    });

    return {
      labels: labels.map((l) => new Date(l).toLocaleString('es-EC', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' })),
      datasets,
    };
  });

  ngOnInit(): void {
    this.cargarPiscinas();
  }

  private cargarPiscinas(selectAfter?: number): void {
    this.piscinaService.list({ limit: 200 }).subscribe({
      next: (piscinas) => {
        this.piscinas.set(piscinas);
        this.loading.set(false);
        const target = selectAfter ?? piscinas[0]?.id ?? null;
        if (target) this.select(target);
      },
      error: () => this.loading.set(false),
    });
  }

  select(id: number): void {
    this.selectedId.set(id);
    this.loadingDetalle.set(true);
    forkJoin({
      sensores: this.sensorService.listByPiscina(id),
      lecturas: this.lecturaService.list({ limit: 300 }),
    }).subscribe({
      next: ({ sensores, lecturas }) => {
        this.sensoresSeleccionada.set(sensores);
        const idsSensores = new Set(sensores.map((s) => s.id));
        this.lecturasSeleccionada.set(lecturas.filter((l) => idsSensores.has(l.id_sensor)));
        this.loadingDetalle.set(false);
      },
      error: () => this.loadingDetalle.set(false),
    });
  }

  openCreatePiscina(): void {
    this.piscinaEnEdicion.set(null);
    this.piscinaFormOpen.set(true);
  }

  openEditPiscina(piscina: Piscina, event: Event): void {
    event.stopPropagation();
    this.piscinaEnEdicion.set(piscina);
    this.piscinaFormOpen.set(true);
  }

  savePiscina(payload: PiscinaCreate | PiscinaUpdate): void {
    this.savingPiscina.set(true);
    const editing = this.piscinaEnEdicion();
    const request = editing
      ? this.piscinaService.update(editing.id, payload)
      : this.piscinaService.create(payload as PiscinaCreate);

    request.subscribe({
      next: (piscina) => {
        this.savingPiscina.set(false);
        this.piscinaFormOpen.set(false);
        this.notifications.success(editing ? 'Piscina actualizada correctamente.' : 'Piscina creada correctamente.');
        this.cargarPiscinas(piscina.id);
      },
      error: () => this.savingPiscina.set(false),
    });
  }

  confirmDeletePiscina(piscina: Piscina, event: Event): void {
    event.stopPropagation();
    this.piscinaAEliminar.set(piscina);
  }

  deletePiscina(): void {
    const piscina = this.piscinaAEliminar();
    if (!piscina) return;
    this.piscinaService.delete(piscina.id).subscribe({
      next: () => {
        this.notifications.success('Piscina eliminada.');
        this.piscinaAEliminar.set(null);
        this.cargarPiscinas();
      },
      error: () => this.piscinaAEliminar.set(null),
    });
  }

  openCreateSensor(): void {
    this.sensorEnEdicion.set(null);
    this.sensorFormOpen.set(true);
  }

  openEditSensor(sensor: Sensor): void {
    this.sensorEnEdicion.set(sensor);
    this.sensorFormOpen.set(true);
  }

  saveSensor(payload: SensorCreate | SensorUpdate): void {
    this.savingSensor.set(true);
    const editing = this.sensorEnEdicion();
    const request = editing ? this.sensorService.update(editing.id, payload) : this.sensorService.create(payload as SensorCreate);

    request.subscribe({
      next: () => {
        this.savingSensor.set(false);
        this.sensorFormOpen.set(false);
        this.notifications.success(editing ? 'Sensor actualizado.' : 'Sensor creado.');
        const id = this.selectedId();
        if (id) this.select(id);
      },
      error: () => this.savingSensor.set(false),
    });
  }

  confirmDeleteSensor(sensor: Sensor): void {
    this.sensorAEliminar.set(sensor);
  }

  deleteSensor(): void {
    const sensor = this.sensorAEliminar();
    if (!sensor) return;
    this.sensorService.delete(sensor.id).subscribe({
      next: () => {
        this.notifications.success('Sensor eliminado.');
        this.sensorAEliminar.set(null);
        const id = this.selectedId();
        if (id) this.select(id);
      },
      error: () => this.sensorAEliminar.set(null),
    });
  }
}
