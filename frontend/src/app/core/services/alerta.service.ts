import { Injectable } from '@angular/core';

import { Alerta, AlertaCreate, AlertaFiltros, AlertaUpdate } from '../models';
import { CrudService } from './crud.service';

@Injectable({ providedIn: 'root' })
export class AlertaService extends CrudService<Alerta, AlertaCreate, AlertaUpdate> {
  constructor() {
    super('alertas');
  }

  override list(params: AlertaFiltros = {}) {
    return super.list(params as Record<string, string | number | undefined>);
  }
}
