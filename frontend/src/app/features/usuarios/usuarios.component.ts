import { DatePipe } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';

import { Rol, RolCreate, RolUpdate, Usuario, UsuarioCreate, UsuarioUpdate } from '../../core/models';
import { NotificationService } from '../../core/services/notification.service';
import { RolService } from '../../core/services/rol.service';
import { UsuarioService } from '../../core/services/usuario.service';
import { ConfirmDialogComponent } from '../../shared/components/confirm-dialog/confirm-dialog.component';
import { EmptyStateComponent } from '../../shared/components/empty-state/empty-state.component';
import { LoadingSpinnerComponent } from '../../shared/components/loading-spinner/loading-spinner.component';
import { StatusBadgeComponent } from '../../shared/components/status-badge/status-badge.component';
import { RolFormComponent } from './rol-form/rol-form.component';
import { UsuarioFormComponent } from './usuario-form/usuario-form.component';

type Tab = 'usuarios' | 'roles';

@Component({
  selector: 'app-usuarios',
  standalone: true,
  imports: [
    DatePipe,
    LoadingSpinnerComponent,
    EmptyStateComponent,
    StatusBadgeComponent,
    UsuarioFormComponent,
    RolFormComponent,
    ConfirmDialogComponent,
  ],
  templateUrl: './usuarios.component.html',
})
export class UsuariosComponent implements OnInit {
  private readonly usuarioService = inject(UsuarioService);
  private readonly rolService = inject(RolService);
  private readonly notifications = inject(NotificationService);

  readonly loading = signal(true);
  readonly tab = signal<Tab>('usuarios');
  readonly usuarios = signal<Usuario[]>([]);
  readonly roles = signal<Rol[]>([]);

  readonly usuarioFormOpen = signal(false);
  readonly usuarioEnEdicion = signal<Usuario | null>(null);
  readonly savingUsuario = signal(false);
  readonly usuarioAEliminar = signal<Usuario | null>(null);

  readonly rolFormOpen = signal(false);
  readonly rolEnEdicion = signal<Rol | null>(null);
  readonly savingRol = signal(false);
  readonly rolAEliminar = signal<Rol | null>(null);

  private readonly rolPorId = computed(() => new Map(this.roles().map((r) => [r.id, r])));

  ngOnInit(): void {
    this.cargar();
  }

  cargar(): void {
    this.loading.set(true);
    forkJoin({
      usuarios: this.usuarioService.list({ limit: 300 }),
      roles: this.rolService.list({ limit: 300 }),
    }).subscribe({
      next: ({ usuarios, roles }) => {
        this.usuarios.set(usuarios);
        this.roles.set(roles);
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  nombreRol(idRol: number): string {
    return this.rolPorId().get(idRol)?.nombre_rol ?? `#${idRol}`;
  }

  setTab(tab: Tab): void {
    this.tab.set(tab);
  }

  abrirCrearUsuario(): void {
    this.usuarioEnEdicion.set(null);
    this.usuarioFormOpen.set(true);
  }

  abrirEditarUsuario(usuario: Usuario): void {
    this.usuarioEnEdicion.set(usuario);
    this.usuarioFormOpen.set(true);
  }

  guardarUsuario(payload: UsuarioCreate | UsuarioUpdate): void {
    this.savingUsuario.set(true);
    const editing = this.usuarioEnEdicion();
    const request = editing
      ? this.usuarioService.update(editing.id, payload)
      : this.usuarioService.create(payload as UsuarioCreate);

    request.subscribe({
      next: () => {
        this.savingUsuario.set(false);
        this.usuarioFormOpen.set(false);
        this.notifications.success(editing ? 'Usuario actualizado.' : 'Usuario creado.');
        this.cargar();
      },
      error: () => this.savingUsuario.set(false),
    });
  }

  confirmarEliminarUsuario(usuario: Usuario): void {
    this.usuarioAEliminar.set(usuario);
  }

  eliminarUsuario(): void {
    const usuario = this.usuarioAEliminar();
    if (!usuario) return;
    this.usuarioService.delete(usuario.id).subscribe({
      next: () => {
        this.notifications.success('Usuario eliminado.');
        this.usuarioAEliminar.set(null);
        this.cargar();
      },
      error: () => this.usuarioAEliminar.set(null),
    });
  }

  abrirCrearRol(): void {
    this.rolEnEdicion.set(null);
    this.rolFormOpen.set(true);
  }

  abrirEditarRol(rol: Rol): void {
    this.rolEnEdicion.set(rol);
    this.rolFormOpen.set(true);
  }

  guardarRol(payload: RolCreate | RolUpdate): void {
    this.savingRol.set(true);
    const editing = this.rolEnEdicion();
    const request = editing ? this.rolService.update(editing.id, payload) : this.rolService.create(payload as RolCreate);

    request.subscribe({
      next: () => {
        this.savingRol.set(false);
        this.rolFormOpen.set(false);
        this.notifications.success(editing ? 'Rol actualizado.' : 'Rol creado.');
        this.cargar();
      },
      error: () => this.savingRol.set(false),
    });
  }

  confirmarEliminarRol(rol: Rol): void {
    this.rolAEliminar.set(rol);
  }

  eliminarRol(): void {
    const rol = this.rolAEliminar();
    if (!rol) return;
    this.rolService.delete(rol.id).subscribe({
      next: () => {
        this.notifications.success('Rol eliminado.');
        this.rolAEliminar.set(null);
        this.cargar();
      },
      error: () => this.rolAEliminar.set(null),
    });
  }
}
