import { Injectable } from '@angular/core';

import {
  RecomendacionAlimentacion,
  RecomendacionAlimentacionCreate,
  RecomendacionAlimentacionUpdate,
} from '../models';
import { CrudService } from './crud.service';

@Injectable({ providedIn: 'root' })
export class RecomendacionAlimentacionService extends CrudService<
  RecomendacionAlimentacion,
  RecomendacionAlimentacionCreate,
  RecomendacionAlimentacionUpdate
> {
  constructor() {
    super('recomendaciones-alimentacion');
  }
}
