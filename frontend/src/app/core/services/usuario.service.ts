import { Injectable } from '@angular/core';

import { Usuario, UsuarioCreate, UsuarioUpdate } from '../models';
import { CrudService } from './crud.service';

@Injectable({ providedIn: 'root' })
export class UsuarioService extends CrudService<Usuario, UsuarioCreate, UsuarioUpdate> {
  constructor() {
    super('usuarios');
  }
}
