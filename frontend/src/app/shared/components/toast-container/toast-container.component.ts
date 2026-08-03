import { Component, inject } from '@angular/core';

import { NotificationService } from '../../../core/services/notification.service';

@Component({
  selector: 'app-toast-container',
  standalone: true,
  templateUrl: './toast-container.component.html',
})
export class ToastContainerComponent {
  protected readonly notifications = inject(NotificationService);

  iconFor(type: string): string {
    switch (type) {
      case 'success':
        return 'check_circle';
      case 'error':
        return 'error';
      default:
        return 'info';
    }
  }

  colorClassFor(type: string): string {
    switch (type) {
      case 'success':
        return 'border-secondary/30 bg-secondary-container/20 text-on-secondary-container';
      case 'error':
        return 'border-error/30 bg-error-container/40 text-on-error-container';
      default:
        return 'border-outline-variant/30 bg-surface-container text-on-surface';
    }
  }
}
