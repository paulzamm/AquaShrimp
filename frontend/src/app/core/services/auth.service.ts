import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, catchError, of, switchMap, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { LoginResponse, Rol, Usuario } from '../models';
import { decodeJwtPayload, isJwtExpired } from '../utils/jwt.util';

const TOKEN_KEY = 'aquashrimp_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly tokenSignal = signal<string | null>(
    localStorage.getItem(TOKEN_KEY) ?? sessionStorage.getItem(TOKEN_KEY),
  );

  private readonly usuarioSignal = signal<Usuario | null>(null);
  private readonly rolSignal = signal<Rol | null>(null);

  readonly usuario = this.usuarioSignal.asReadonly();
  readonly rolNombre = computed(() => this.rolSignal()?.nombre_rol ?? null);

  readonly isAuthenticated = computed(() => {
    const token = this.tokenSignal();
    return !!token && !isJwtExpired(token);
  });

  readonly correo = computed(() => {
    const token = this.tokenSignal();
    return token ? (decodeJwtPayload(token)?.sub ?? null) : null;
  });

  /** `remember` controls whether the token survives a browser restart (localStorage) or only the current tab (sessionStorage). */
  login(correo: string, password: string, remember: boolean): Observable<LoginResponse> {
    const body = new HttpParams().set('username', correo).set('password', password);
    return this.http
      .post<LoginResponse>(`${environment.apiUrl}/auth/login`, body.toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      .pipe(
        tap((response) => {
          const storage = remember ? localStorage : sessionStorage;
          storage.setItem(TOKEN_KEY, response.access_token);
          this.tokenSignal.set(response.access_token);
        }),
      );
  }

  /** Fetches /auth/me + the matching rol, caching both in signals for role guards/UI. Safe to call repeatedly. */
  loadCurrentUser(): Observable<Usuario | null> {
    if (this.usuarioSignal()) {
      return of(this.usuarioSignal());
    }
    return this.http.get<Usuario>(`${environment.apiUrl}/auth/me`).pipe(
      tap((usuario) => this.usuarioSignal.set(usuario)),
      switchMap((usuario) =>
        this.http.get<Rol>(`${environment.apiUrl}/roles/${usuario.id_rol}`).pipe(
          tap((rol) => this.rolSignal.set(rol)),
          switchMap(() => of(usuario)),
        ),
      ),
      catchError(() => of(null)),
    );
  }

  hasAnyRole(...roles: string[]): boolean {
    const current = this.rolNombre();
    return !!current && roles.includes(current);
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(TOKEN_KEY);
    this.tokenSignal.set(null);
    this.usuarioSignal.set(null);
    this.rolSignal.set(null);
  }

  getToken(): string | null {
    return this.tokenSignal();
  }
}
