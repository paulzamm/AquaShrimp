export type EstadoValidacion = 'pendiente' | 'valida' | 'invalida';

export interface LecturaSensor {
  id: number;
  id_sensor: number;
  valor: number;
  unidad: string;
  fecha_hora?: string | null;
  estado_validacion: EstadoValidacion;
  observacion?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface LecturaSensorCreate {
  id_sensor: number;
  valor: number;
  unidad: string;
  fecha_hora?: string | null;
  estado_validacion?: EstadoValidacion;
  observacion?: string | null;
}
