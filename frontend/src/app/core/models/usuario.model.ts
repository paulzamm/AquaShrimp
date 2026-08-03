export interface Usuario {
  id: number;
  id_rol: number;
  nombre: string;
  correo: string;
  estado: string;
  ultimo_acceso?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface UsuarioCreate {
  id_rol: number;
  nombre: string;
  correo: string;
  contrasena: string;
  estado?: string;
}

export interface UsuarioUpdate {
  id_rol?: number;
  nombre?: string;
  correo?: string;
  contrasena?: string;
  estado?: string;
}
