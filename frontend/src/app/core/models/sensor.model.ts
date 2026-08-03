export type TipoSensor = 'ph' | 'oxigeno_disuelto' | 'temperatura';
export type EstadoSensor = 'activo' | 'inactivo' | 'fallo';

export interface Sensor {
  id: number;
  id_piscina: number;
  tipo: TipoSensor;
  ubicacion?: string | null;
  estado: EstadoSensor;
  unidad_medida: string;
  fecha_instalacion?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface SensorCreate {
  id_piscina: number;
  tipo: TipoSensor;
  ubicacion?: string | null;
  estado?: EstadoSensor;
  unidad_medida: string;
  fecha_instalacion?: string | null;
}

export type SensorUpdate = Partial<SensorCreate>;
