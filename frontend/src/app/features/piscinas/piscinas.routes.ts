import { Routes } from '@angular/router';

export const PISCINAS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./piscinas.component').then((m) => m.PiscinasComponent),
  },
];
