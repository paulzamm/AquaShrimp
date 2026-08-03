import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-empty-state',
  standalone: true,
  template: `
    <div class="flex flex-col items-center justify-center gap-3 py-16 text-center text-on-surface-variant">
      <span class="material-symbols-outlined text-[40px] text-outline">{{ icon }}</span>
      <p class="font-body-lg text-body-lg text-on-surface font-medium">{{ title }}</p>
      @if (subtitle) {
        <p class="font-body-md text-body-md max-w-sm">{{ subtitle }}</p>
      }
    </div>
  `,
})
export class EmptyStateComponent {
  @Input() icon = 'inbox';
  @Input() title = 'Sin datos por el momento';
  @Input() subtitle?: string;
}
