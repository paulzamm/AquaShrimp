import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { ChartData } from 'chart.js';
import { forkJoin } from 'rxjs';

import { AlertaService } from '../../core/services/alerta.service';
import { LecturaService } from '../../core/services/lectura.service';
import { PiscinaService } from '../../core/services/piscina.service';
import { SensorService } from '../../core/services/sensor.service';
import { Alerta, LecturaSensor, Piscina, Sensor } from '../../core/models';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';
import { LineChartComponent } from '../../shared/components/line-chart/line-chart.component';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';

interface LatestLectura extends LecturaSensor {
  sensor?: Sensor;
  piscina?: Piscina;
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [LoadingSpinnerComponent, EmptyStateComponent, LineChartComponent, StatusBadgeComponent],
  templateUrl: './dashboard.component.html',
})
export class DashboardComponent implements OnInit {
  private readonly piscinaService = inject(PiscinaService);
  private readonly sensorService = inject(SensorService);
  private readonly lecturaService = inject(LecturaService);
  private readonly alertaService = inject(AlertaService);

  readonly loading = signal(true);
  readonly piscinas = signal<Piscina[]>([]);
  readonly sensores = signal<Sensor[]>([]);
  readonly lecturas = signal<LecturaSensor[]>([]);
  readonly alertasActivas = signal<Alerta[]>([]);
  readonly selectedPiscinaId = signal<number | null>(null);

  private readonly sensorPorId = computed(() => new Map(this.sensores().map((s) => [s.id, s])));
  private readonly piscinaPorId = computed(() => new Map(this.piscinas().map((p) => [p.id, p])));

  private readonly sensoresFiltrados = computed(() => {
    const piscinaId = this.selectedPiscinaId();
    return piscinaId ? this.sensores().filter((s) => s.id_piscina === piscinaId) : this.sensores();
  });

  private readonly lecturasFiltradas = computed(() => {
    const idsPermitidos = new Set(this.sensoresFiltrados().map((s) => s.id));
    return this.lecturas().filter((l) => idsPermitidos.has(l.id_sensor));
  });

  readonly piscinasActivas = computed(() => this.piscinas().filter((p) => p.estado === 'activa').length);
  readonly totalPiscinas = computed(() => this.piscinas().length);

  readonly alertasCriticas = computed(
    () => this.alertasActivas().filter((a) => a.severidad === 'critica').length,
  );

  private readonly latestPorSensor = computed(() => {
    const latest = new Map<number, LecturaSensor>();
    for (const lectura of this.lecturasFiltradas()) {
      const current = latest.get(lectura.id_sensor);
      const fecha = lectura.fecha_hora ?? lectura.created_at;
      const currentFecha = current ? (current.fecha_hora ?? current.created_at) : undefined;
      if (!current || (fecha && currentFecha && fecha > currentFecha)) {
        latest.set(lectura.id_sensor, lectura);
      }
    }
    return latest;
  });

  readonly promedioTemperatura = computed(() => this.promedioPorTipo('temperatura'));
  readonly promedioOxigeno = computed(() => this.promedioPorTipo('oxigeno_disuelto'));

  readonly ultimasLecturas = computed<LatestLectura[]>(() => {
    const sensores = this.sensorPorId();
    const piscinasMap = this.piscinaPorId();
    return [...this.latestPorSensor().values()]
      .map((lectura) => {
        const sensor = sensores.get(lectura.id_sensor);
        return {
          ...lectura,
          sensor,
          piscina: sensor ? piscinasMap.get(sensor.id_piscina) : undefined,
        };
      })
      .sort((a, b) => (b.fecha_hora ?? b.created_at).localeCompare(a.fecha_hora ?? a.created_at))
      .slice(0, 6);
  });

  readonly chartData = computed<ChartData<'line'>>(() => {
    const sensores = this.sensorPorId();
    const piscinasMap = this.piscinaPorId();
    const temperaturaSensores = this.sensoresFiltrados().filter((s) => s.tipo === 'temperatura');

    const porSensor = new Map<number, LecturaSensor[]>();
    for (const lectura of this.lecturasFiltradas()) {
      if (!temperaturaSensores.some((s) => s.id === lectura.id_sensor)) continue;
      const arr = porSensor.get(lectura.id_sensor) ?? [];
      arr.push(lectura);
      porSensor.set(lectura.id_sensor, arr);
    }

    const labelsSet = new Set<string>();
    for (const lecturasSensor of porSensor.values()) {
      for (const l of lecturasSensor) {
        labelsSet.add(l.fecha_hora ?? l.created_at);
      }
    }
    const labels = [...labelsSet].sort();

    const palette = ['#00696c', '#004655', '#226150', '#8bd1e8'];
    const datasets = [...porSensor.entries()].map(([idSensor, lecturasSensor], index) => {
      const porFecha = new Map(lecturasSensor.map((l) => [l.fecha_hora ?? l.created_at, l.valor]));
      const sensor = sensores.get(idSensor);
      const piscina = sensor ? piscinasMap.get(sensor.id_piscina) : undefined;
      return {
        label: piscina?.codigo ?? `Sensor ${idSensor}`,
        data: labels.map((label) => porFecha.get(label) ?? null),
        borderColor: palette[index % palette.length],
        backgroundColor: palette[index % palette.length] + '33',
        tension: 0.3,
        fill: false,
      };
    });

    return {
      labels: labels.map((l) => new Date(l).toLocaleTimeString('es-EC', { hour: '2-digit', minute: '2-digit' })),
      datasets,
    };
  });

  ngOnInit(): void {
    forkJoin({
      piscinas: this.piscinaService.list({ limit: 500 }),
      sensores: this.sensorService.list({ limit: 500 }),
      lecturas: this.lecturaService.list({ limit: 500 }),
      alertas: this.alertaService.list({ estado: 'activa', limit: 200 }),
    }).subscribe({
      next: ({ piscinas, sensores, lecturas, alertas }) => {
        this.piscinas.set(piscinas);
        this.sensores.set(sensores);
        this.lecturas.set(lecturas);
        this.alertasActivas.set(alertas);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  onFiltroChange(value: string): void {
    this.selectedPiscinaId.set(value ? Number(value) : null);
  }

  private promedioPorTipo(tipo: 'temperatura' | 'oxigeno_disuelto'): number | null {
    const sensores = this.sensorPorId();
    const valores = [...this.latestPorSensor().entries()]
      .filter(([idSensor]) => sensores.get(idSensor)?.tipo === tipo)
      .map(([, lectura]) => lectura.valor);
    if (!valores.length) return null;
    return valores.reduce((sum, v) => sum + v, 0) / valores.length;
  }
}
