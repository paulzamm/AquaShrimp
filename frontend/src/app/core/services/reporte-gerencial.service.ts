import { Injectable } from '@angular/core';

import { ReporteGerencial, ReporteGerencialCreate, ReporteGerencialUpdate } from '../models';
import { CrudService } from './crud.service';

@Injectable({ providedIn: 'root' })
export class ReporteGerencialService extends CrudService<
  ReporteGerencial,
  ReporteGerencialCreate,
  ReporteGerencialUpdate
> {
  constructor() {
    super('reportes-gerenciales');
  }
}
