import { Routes } from '@angular/router';

import { authGuard } from './core/guards/auth.guard';
import { loginGuard } from './core/guards/login.guard';
import { roleGuard } from './core/guards/role.guard';
import { ShellComponent } from './shared/components/shell/shell.component';

export const routes: Routes = [
  {
    path: 'login',
    canActivate: [loginGuard],
    loadComponent: () => import('./features/auth/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: '',
    component: ShellComponent,
    canActivate: [authGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
      {
        path: 'dashboard',
        loadChildren: () => import('./features/dashboard/dashboard.routes').then((m) => m.DASHBOARD_ROUTES),
      },
      {
        path: 'piscinas',
        loadChildren: () => import('./features/piscinas/piscinas.routes').then((m) => m.PISCINAS_ROUTES),
      },
      {
        path: 'alertas',
        loadChildren: () => import('./features/alertas/alertas.routes').then((m) => m.ALERTAS_ROUTES),
      },
      {
        path: 'alimentacion',
        loadChildren: () =>
          import('./features/alimentacion/alimentacion.routes').then((m) => m.ALIMENTACION_ROUTES),
      },
      {
        path: 'cosechas',
        loadChildren: () => import('./features/cosechas/cosechas.routes').then((m) => m.COSECHAS_ROUTES),
      },
      {
        path: 'reportes',
        loadChildren: () => import('./features/reportes/reportes.routes').then((m) => m.REPORTES_ROUTES),
      },
      {
        path: 'usuarios',
        canActivate: [roleGuard(['Administrador'])],
        loadChildren: () => import('./features/usuarios/usuarios.routes').then((m) => m.USUARIOS_ROUTES),
      },
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];
