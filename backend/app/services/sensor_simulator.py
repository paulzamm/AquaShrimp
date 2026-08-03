import asyncio
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx

from app.core.database import SessionLocal
from app.models.sensor import Sensor

# (normal_low, normal_high), (critico_bajo_low, critico_bajo_high), (critico_alto_low, critico_alto_high)
# Los límites de "normal" coinciden con los umbrales que ya evalúa app/services/bpm.py.
RANGOS: dict[str, dict[str, Optional[tuple[float, float]]]] = {
    "ph": {
        "normal": (6.8, 8.0),
        "critico_bajo": (5.5, 6.4),
        "critico_alto": (8.6, 9.5),
    },
    "oxigeno_disuelto": {
        "normal": (4.5, 7.0),
        "critico_bajo": (1.5, 3.9),
        "critico_alto": None,
    },
    "temperatura": {
        "normal": (25.0, 31.0),
        "critico_bajo": (18.0, 23.9),
        "critico_alto": (32.1, 38.0),
    },
}

UNIDADES = {"ph": "pH", "oxigeno_disuelto": "mg/L", "temperatura": "°C"}

SIMULADOR_CORREO = "tecnico@aquashrimp.com"
SIMULADOR_PASSWORD = "tecnico123"


@dataclass
class SimuladorConfig:
    intervalo_segundos: float = 10.0
    prob_valor_critico: float = 0.1
    prob_perdida_comunicacion: float = 0.05
    prob_fallo_sensor: float = 0.03


@dataclass
class SimuladorEstado:
    activo: bool = False
    ciclos_ejecutados: int = 0
    ultima_ejecucion: Optional[datetime] = None
    ultimo_error: Optional[str] = None


@dataclass
class HistoricoEstado:
    en_progreso: bool = False
    enviadas: int = 0
    total: int = 0
    ultimo_error: Optional[str] = None


class SensorSimulator:
    """Módulo interno de simulación de sensores IoT (Fase 4).

    Genera lecturas sintéticas de pH, oxígeno disuelto y temperatura y las envía
    mediante HTTP POST real a /api/lecturas — el mismo endpoint y contrato JSON
    que usaría un sensor físico — para que el resto del sistema (BPM, alertas,
    recomendaciones, dashboard) nunca distinga el origen de los datos.
    """

    def __init__(self) -> None:
        self.config = SimuladorConfig()
        self.estado = SimuladorEstado()
        self.historico = HistoricoEstado()
        self._task: Optional[asyncio.Task] = None
        self._historico_task: Optional[asyncio.Task] = None
        self._token: Optional[str] = None
        self._base_url = "http://localhost:8000"
        self._trend: dict[int, float] = {}

    def is_running(self) -> bool:
        return self.estado.activo

    async def start(self, config: SimuladorConfig) -> None:
        if self.estado.activo:
            return
        self.config = config
        self.estado = SimuladorEstado(activo=True)
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        self.estado.activo = False
        if self._task:
            self._task.cancel()
            self._task = None

    async def _login(self, client: httpx.AsyncClient) -> Optional[str]:
        try:
            resp = await client.post(
                f"{self._base_url}/api/auth/login",
                data={"username": SIMULADOR_CORREO, "password": SIMULADOR_PASSWORD},
            )
            if resp.status_code == 200:
                return resp.json()["access_token"]
        except httpx.HTTPError as exc:
            self.estado.ultimo_error = f"Error de autenticación: {exc}"
        return None

    async def _ensure_token(self, client: httpx.AsyncClient) -> Optional[str]:
        if not self._token:
            self._token = await self._login(client)
        return self._token

    def _generar_valor(self, tipo: str, id_sensor: int, forzar_critico: bool) -> float:
        rangos = RANGOS.get(tipo)
        if not rangos:
            return 0.0

        if forzar_critico:
            opciones = [r for r in (rangos["critico_bajo"], rangos["critico_alto"]) if r]
            lo, hi = random.choice(opciones)
            return round(random.uniform(lo, hi), 2)

        lo, hi = rangos["normal"]
        ancho = hi - lo
        # Tendencia: pequeña deriva acumulada por sensor para simular subidas/bajadas graduales.
        drift = self._trend.get(id_sensor, 0.0)
        drift += random.uniform(-0.05, 0.05) * ancho
        drift = max(-ancho * 0.3, min(ancho * 0.3, drift))
        self._trend[id_sensor] = drift

        centro = (lo + hi) / 2 + drift
        ruido = random.gauss(0, ancho * 0.08)
        valor = centro + ruido
        return round(valor, 2)

    async def _procesar_sensor(self, client: httpx.AsyncClient, headers: dict, sensor: Sensor) -> None:
        if random.random() < self.config.prob_perdida_comunicacion:
            return  # Pérdida de comunicación simulada: este ciclo no envía nada.

        fallo = random.random() < self.config.prob_fallo_sensor
        if fallo:
            valor = random.choice([-999.0, 999.0])
            observacion = "Lectura anómala: posible fallo de sensor (simulado)"
        else:
            forzar_critico = random.random() < self.config.prob_valor_critico
            valor = self._generar_valor(sensor.tipo, sensor.id, forzar_critico)
            observacion = None

        payload = {
            "id_sensor": sensor.id,
            "valor": valor,
            "unidad": UNIDADES.get(sensor.tipo, ""),
            "observacion": observacion,
        }
        try:
            resp = await client.post(f"{self._base_url}/api/lecturas", json=payload, headers=headers)
            if resp.status_code == 401:
                self._token = None
            elif resp.status_code >= 400:
                self.estado.ultimo_error = f"Sensor {sensor.id}: HTTP {resp.status_code} - {resp.text[:200]}"
        except httpx.HTTPError as exc:
            self.estado.ultimo_error = f"Sensor {sensor.id}: {exc}"

    async def _ciclo(self, client: httpx.AsyncClient) -> None:
        token = await self._ensure_token(client)
        if not token:
            self.estado.ultimo_error = "No se pudo autenticar el simulador"
            return
        headers = {"Authorization": f"Bearer {token}"}

        db = SessionLocal()
        try:
            sensores = db.query(Sensor).filter(Sensor.estado == "activo").all()
        finally:
            db.close()

        for sensor in sensores:
            await self._procesar_sensor(client, headers, sensor)

    async def _loop(self) -> None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            while self.estado.activo:
                try:
                    await self._ciclo(client)
                    self.estado.ciclos_ejecutados += 1
                    self.estado.ultima_ejecucion = datetime.now(timezone.utc)
                except asyncio.CancelledError:
                    raise
                except Exception as exc:  # noqa: BLE001 - el simulador no debe morir por un ciclo fallido
                    self.estado.ultimo_error = str(exc)
                await asyncio.sleep(self.config.intervalo_segundos)

    async def generar_historico(self, dias: int, lecturas_por_dia: int) -> None:
        if self.historico.en_progreso:
            return

        db = SessionLocal()
        try:
            sensores = db.query(Sensor).filter(Sensor.estado == "activo").all()
        finally:
            db.close()

        total = dias * lecturas_por_dia * max(len(sensores), 1)
        self.historico = HistoricoEstado(en_progreso=True, total=total)
        self._historico_task = asyncio.create_task(self._run_historico(sensores, dias, lecturas_por_dia))

    async def _run_historico(self, sensores: list[Sensor], dias: int, lecturas_por_dia: int) -> None:
        ahora = datetime.now(timezone.utc)
        paso = timedelta(days=dias) / max(dias * lecturas_por_dia, 1)

        async with httpx.AsyncClient(timeout=10.0) as client:
            token = await self._ensure_token(client)
            if not token:
                self.historico.ultimo_error = "No se pudo autenticar el simulador"
                self.historico.en_progreso = False
                return
            headers = {"Authorization": f"Bearer {token}"}

            momento = ahora - timedelta(days=dias)
            for _ in range(dias * lecturas_por_dia):
                for sensor in sensores:
                    forzar_critico = random.random() < self.config.prob_valor_critico
                    valor = self._generar_valor(sensor.tipo, sensor.id, forzar_critico)
                    payload = {
                        "id_sensor": sensor.id,
                        "valor": valor,
                        "unidad": UNIDADES.get(sensor.tipo, ""),
                        "fecha_hora": momento.isoformat(),
                    }
                    try:
                        resp = await client.post(f"{self._base_url}/api/lecturas", json=payload, headers=headers)
                        if resp.status_code == 401:
                            self._token = None
                            token = await self._ensure_token(client)
                            headers = {"Authorization": f"Bearer {token}"} if token else headers
                    except httpx.HTTPError as exc:
                        self.historico.ultimo_error = str(exc)
                    self.historico.enviadas += 1
                momento += paso

        self.historico.en_progreso = False


simulador = SensorSimulator()
