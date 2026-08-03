import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Sensor, SensorCreate, SensorUpdate } from '../models';
import { CrudService } from './crud.service';

@Injectable({ providedIn: 'root' })
export class SensorService extends CrudService<Sensor, SensorCreate, SensorUpdate> {
  constructor() {
    super('sensores');
  }

  listByPiscina(idPiscina: number): Observable<Sensor[]> {
    return this.list({ id_piscina: idPiscina });
  }
}
