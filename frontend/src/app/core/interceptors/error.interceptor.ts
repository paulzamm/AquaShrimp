import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

import { isValidationError } from '../models';
import { AuthService } from '../services/auth.service';
import { NotificationService } from '../services/notification.service';

function extractMessage(error: HttpErrorResponse): string {
  const body: unknown = error.error;
  if (isValidationError(body)) {
    return body.detail.map((item) => item.msg).join(' — ');
  }
  if (body && typeof body === 'object' && typeof (body as { detail?: unknown }).detail === 'string') {
    return (body as { detail: string }).detail;
  }
  return 'Ocurrió un error inesperado al comunicarse con el servidor.';
}

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notifications = inject(NotificationService);
  const authService = inject(AuthService);
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: unknown) => {
      if (error instanceof HttpErrorResponse) {
        const message = extractMessage(error);
        const isLoginRequest = req.url.endsWith('/auth/login');

        if (error.status === 401 && !isLoginRequest) {
          authService.logout();
          notifications.error('Tu sesión expiró o no es válida. Inicia sesión nuevamente.');
          router.navigate(['/login'], { queryParams: { returnUrl: router.url } });
        } else if (error.status === 401 && isLoginRequest) {
          notifications.error(message);
        } else if (error.status === 403) {
          notifications.error(message || 'No tienes permisos suficientes para realizar esta acción.');
        } else if (error.status === 0) {
          notifications.error('No se pudo conectar con el servidor de AquaShrimp.');
        } else {
          notifications.error(message);
        }
      }
      return throwError(() => error);
    }),
  );
};
