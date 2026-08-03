import { Component, OnInit, computed, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { AuthService } from '../../../core/services/auth.service';

interface NavItem {
  path: string;
  label: string;
  icon: string;
  roles?: string[];
}

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './shell.component.html',
})
export class ShellComponent implements OnInit {
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);

  private readonly allNavItems: NavItem[] = [
    { path: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
    { path: '/piscinas', label: 'Monitoreo', icon: 'monitoring' },
    { path: '/alertas', label: 'Alertas', icon: 'notifications' },
    { path: '/alimentacion', label: 'Alimentación', icon: 'set_meal' },
    { path: '/cosechas', label: 'Cosecha', icon: 'waves' },
    { path: '/reportes', label: 'Reportes', icon: 'assessment' },
    { path: '/usuarios', label: 'Admin', icon: 'settings', roles: ['Administrador'] },
  ];

  readonly navItems = computed(() =>
    this.allNavItems.filter((item) => !item.roles || this.authService.hasAnyRole(...item.roles)),
  );

  readonly correo = computed(() => this.authService.correo() ?? '');
  readonly rolNombre = computed(() => this.authService.rolNombre());

  readonly initials = computed(() => {
    const correo = this.correo();
    return correo ? correo.slice(0, 2).toUpperCase() : '?';
  });

  ngOnInit(): void {
    this.authService.loadCurrentUser().subscribe();
  }

  logout(): void {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
}
