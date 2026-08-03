import { Component, Input, computed, signal } from '@angular/core';

type BadgeTone = 'success' | 'warning' | 'danger' | 'neutral' | 'info';

const TONE_BY_VALUE: Record<string, BadgeTone> = {
  activa: 'success',
  activo: 'success',
  aplicada: 'success',
  completada: 'success',
  atendida: 'info',
  en_progreso: 'info',
  pendiente: 'warning',
  mantenimiento: 'warning',
  media: 'warning',
  baja: 'neutral',
  inactiva: 'neutral',
  inactivo: 'neutral',
  cerrada: 'neutral',
  rechazada: 'danger',
  fallo: 'danger',
  critica: 'danger',
  alta: 'danger',
  invalida: 'danger',
};

const TONE_CLASSES: Record<BadgeTone, string> = {
  success: 'bg-secondary-container/30 text-on-secondary-container',
  info: 'bg-primary-container/10 text-primary border border-primary/20',
  warning: 'bg-tertiary-fixed text-on-tertiary-fixed',
  danger: 'bg-error-container text-on-error-container',
  neutral: 'bg-surface-variant text-on-surface-variant',
};

@Component({
  selector: 'app-status-badge',
  standalone: true,
  template: `
    <span
      class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full font-caption text-caption font-bold capitalize"
      [class]="toneClass()"
    >
      <span class="w-1.5 h-1.5 rounded-full bg-current"></span>
      {{ label() }}
    </span>
  `,
})
export class StatusBadgeComponent {
  private readonly valueSignal = signal('');
  @Input() set value(v: string | null | undefined) {
    this.valueSignal.set(v ?? '');
  }

  readonly label = computed(() => this.valueSignal().replace(/_/g, ' '));
  readonly toneClass = computed(() => TONE_CLASSES[TONE_BY_VALUE[this.valueSignal()] ?? 'neutral']);
}
