/** Confirmed against the applied Alembic migration, NOT the conflicted model source — see project memory on backend blockers. */
export type TipoReporte = 'rendimiento' | 'alertas' | 'alimentacion';

export interface ReporteGerencial {
  id: number;
  id_usuario: number;
  tipo_reporte: TipoReporte;
  periodo_inicio: string;
  periodo_fin: string;
  fecha_generacion?: string | null;
  ruta_archivo?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface ReporteGerencialCreate {
  id_usuario: number;
  tipo_reporte: TipoReporte;
  periodo_inicio: string;
  periodo_fin: string;
  fecha_generacion?: string | null;
  ruta_archivo?: string | null;
}

export type ReporteGerencialUpdate = Partial<ReporteGerencialCreate>;
