import { Injectable } from '@angular/core';

import { Cosecha, CosechaCreate, CosechaUpdate } from '../models';
import { CrudService } from './crud.service';

@Injectable({ providedIn: 'root' })
export class CosechaService extends CrudService<Cosecha, CosechaCreate, CosechaUpdate> {
  constructor() {
    super('cosechas');
  }
}
