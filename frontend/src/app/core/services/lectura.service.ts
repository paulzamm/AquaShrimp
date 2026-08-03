import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { LecturaSensor, LecturaSensorCreate } from '../models';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class LecturaService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiUrl}/lecturas`;

  list(params: { skip?: number; limit?: number; id_sensor?: number } = {}): Observable<LecturaSensor[]> {
    return this.http.get<LecturaSensor[]>(this.baseUrl, { params: params as Record<string, string | number> });
  }

  get(id: number): Observable<LecturaSensor> {
    return this.http.get<LecturaSensor>(`${this.baseUrl}/${id}`);
  }

  create(payload: LecturaSensorCreate): Observable<LecturaSensor> {
    return this.http.post<LecturaSensor>(this.baseUrl, payload);
  }
}
