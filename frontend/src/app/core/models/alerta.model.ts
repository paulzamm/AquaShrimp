export type SeveridadAlerta = 'baja' | 'media' | 'alta' | 'critica';
export type EstadoAlerta = 'activa' | 'atendida' | 'cerrada';

export interface Alerta {
  id: number;
  id_lectura?: number | null;
  id_sensor?: number | null;
  id_usuario?: number | null;
  tipo_alerta: string;
  severidad: SeveridadAlerta;
  descripcion: string;
  fecha_generacion?: string | null;
  estado: EstadoAlerta;
  valor_medido?: number | null;
  fecha_hora?: string | null;
  resuelta_en?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface AlertaCreate {
  id_lectura?: number | null;
  id_sensor?: number | null;
  id_usuario?: number | null;
  tipo_alerta: string;
  severidad?: SeveridadAlerta;
  descripcion: string;
  fecha_generacion?: string | null;
  estado?: EstadoAlerta;
  valor_medido?: number | null;
  fecha_hora?: string | null;
  resuelta_en?: string | null;
}

export type AlertaUpdate = Partial<AlertaCreate>;

export interface AlertaFiltros {
  skip?: number;
  limit?: number;
  estado?: EstadoAlerta;
  severidad?: SeveridadAlerta;
  id_sensor?: number;
}
