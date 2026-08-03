import {
  AfterViewInit,
  Component,
  ElementRef,
  Input,
  OnChanges,
  OnDestroy,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import { Chart, ChartData, registerables } from 'chart.js';

Chart.register(...registerables);

@Component({
  selector: 'app-line-chart',
  standalone: true,
  template: `<canvas #canvas></canvas>`,
})
export class LineChartComponent implements AfterViewInit, OnChanges, OnDestroy {
  @Input() data: ChartData<'line'> = { labels: [], datasets: [] };
  @Input() height = 300;

  @ViewChild('canvas') private readonly canvasRef!: ElementRef<HTMLCanvasElement>;
  private chart?: Chart<'line'>;

  ngAfterViewInit(): void {
    this.canvasRef.nativeElement.parentElement!.style.height = `${this.height}px`;
    this.chart = new Chart<'line'>(this.canvasRef.nativeElement, {
      type: 'line',
      data: this.data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(111,121,124,0.15)' } },
        },
      },
    });
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['data'] && this.chart) {
      this.chart.data = this.data;
      this.chart.update();
    }
  }

  ngOnDestroy(): void {
    this.chart?.destroy();
  }
}
