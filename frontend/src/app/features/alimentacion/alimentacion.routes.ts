import { Routes } from '@angular/router';

export const ALIMENTACION_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./alimentacion.component').then((m) => m.AlimentacionComponent),
  },
];
