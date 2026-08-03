export type EstadoRecomendacion = 'pendiente' | 'aplicada' | 'rechazada';

export interface RecomendacionAlimentacion {
  id: number;
  id_piscina: number;
  id_usuario?: number | null;
  cantidad_kg: number;
  frecuencia: string;
  criterio?: string | null;
  fecha_generacion?: string | null;
  estado: EstadoRecomendacion;
  created_at: string;
  updated_at?: string | null;
}

export interface RecomendacionAlimentacionCreate {
  id_piscina: number;
  id_usuario?: number | null;
  cantidad_kg: number;
  frecuencia: string;
  criterio?: string | null;
  estado?: EstadoRecomendacion;
}

export type RecomendacionAlimentacionUpdate = Partial<RecomendacionAlimentacionCreate>;
