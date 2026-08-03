import { Injectable } from '@angular/core';

import { Rol, RolCreate, RolUpdate } from '../models';
import { CrudService } from './crud.service';

@Injectable({ providedIn: 'root' })
export class RolService extends CrudService<Rol, RolCreate, RolUpdate> {
  constructor() {
    super('roles');
  }
}
