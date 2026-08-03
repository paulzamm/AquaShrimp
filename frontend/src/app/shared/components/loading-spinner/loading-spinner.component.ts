import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-loading-spinner',
  standalone: true,
  template: `
    <div class="flex items-center justify-center gap-3 py-10 text-on-surface-variant">
      <span class="material-symbols-outlined animate-spin text-primary">progress_activity</span>
      <span class="font-body-md text-body-md">{{ label }}</span>
    </div>
  `,
})
export class LoadingSpinnerComponent {
  @Input() label = 'Cargando...';
}
