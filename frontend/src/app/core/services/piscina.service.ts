import { Injectable } from '@angular/core';

import { Piscina, PiscinaCreate, PiscinaUpdate } from '../models';
import { CrudService } from './crud.service';

@Injectable({ providedIn: 'root' })
export class PiscinaService extends CrudService<Piscina, PiscinaCreate, PiscinaUpdate> {
  constructor() {
    super('piscinas');
  }
}
