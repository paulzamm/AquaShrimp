export type EstadoAccionCorrectiva = 'pendiente' | 'en_progreso' | 'completada';

export interface AccionCorrectiva {
  id: number;
  id_alerta: number;
  id_usuario: number;
  descripcion: string;
  fecha_accion?: string | null;
  resultado?: string | null;
  estado: EstadoAccionCorrectiva;
  created_at: string;
  updated_at?: string | null;
}

export interface AccionCorrectivaCreate {
  id_alerta: number;
  id_usuario: number;
  descripcion: string;
  fecha_accion?: string | null;
  resultado?: string | null;
  estado?: EstadoAccionCorrectiva;
}

export type AccionCorrectivaUpdate = Partial<AccionCorrectivaCreate>;
