import { HttpClient, HttpParams } from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

/** Base CRUD client shared by every feature service — all backend resources follow the same list/get/create/update/delete shape. */
export abstract class CrudService<TEntity, TCreate, TUpdate = Partial<TCreate>> {
  protected readonly http = inject(HttpClient);
  protected readonly baseUrl: string;

  protected constructor(resourcePath: string) {
    this.baseUrl = `${environment.apiUrl}/${resourcePath}`;
  }

  list(params: Record<string, string | number | undefined> = {}): Observable<TEntity[]> {
    let httpParams = new HttpParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null) {
        httpParams = httpParams.set(key, value);
      }
    }
    return this.http.get<TEntity[]>(this.baseUrl, { params: httpParams });
  }

  get(id: number): Observable<TEntity> {
    return this.http.get<TEntity>(`${this.baseUrl}/${id}`);
  }

  create(payload: TCreate): Observable<TEntity> {
    return this.http.post<TEntity>(this.baseUrl, payload);
  }

  update(id: number, payload: TUpdate): Observable<TEntity> {
    return this.http.put<TEntity>(`${this.baseUrl}/${id}`, payload);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }
}
