export interface Cosecha {
  id: number;
  id_piscina: number;
  fecha_cosecha: string;
  biomasa_kg: number;
  talla_promedio?: number | null;
  rendimiento?: number | null;
  observaciones?: string | null;
  estado?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface CosechaCreate {
  id_piscina: number;
  fecha_cosecha: string;
  biomasa_kg: number;
  talla_promedio?: number | null;
  rendimiento?: number | null;
  observaciones?: string | null;
  estado?: string;
}

export type CosechaUpdate = Partial<CosechaCreate>;
