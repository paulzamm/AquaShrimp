import { Injectable } from '@angular/core';

import { AccionCorrectiva, AccionCorrectivaCreate, AccionCorrectivaUpdate } from '../models';
import { CrudService } from './crud.service';

@Injectable({ providedIn: 'root' })
export class AccionCorrectivaService extends CrudService<
  AccionCorrectiva,
  AccionCorrectivaCreate,
  AccionCorrectivaUpdate
> {
  constructor() {
    super('acciones-correctivas');
  }
}
