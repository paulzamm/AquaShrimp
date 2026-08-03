export type EstadoPiscina = 'activa' | 'inactiva' | 'mantenimiento';

export interface Piscina {
  id: number;
  codigo: string;
  ubicacion: string;
  area_m2: number;
  profundidad: number;
  estado: EstadoPiscina;
  fecha_inicio_ciclo?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface PiscinaCreate {
  codigo: string;
  ubicacion: string;
  area_m2: number;
  profundidad: number;
  estado?: EstadoPiscina;
  fecha_inicio_ciclo?: string | null;
}

export type PiscinaUpdate = Partial<PiscinaCreate>;
