export interface Rol {
  id: number;
  nombre_rol: string;
  descripcion?: string | null;
  permisos?: string | null;
  estado: string;
  created_at: string;
  updated_at?: string | null;
}

export interface RolCreate {
  nombre_rol: string;
  descripcion?: string | null;
  permisos?: string | null;
  estado?: string;
}

export type RolUpdate = Partial<RolCreate>;
