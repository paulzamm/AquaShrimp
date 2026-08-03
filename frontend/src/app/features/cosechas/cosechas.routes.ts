import { Routes } from '@angular/router';

export const COSECHAS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./cosechas.component').then((m) => m.CosechasComponent),
  },
];
