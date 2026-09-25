"""Outils partagés : construction de trames et faux client BLE Blue Connect."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

MAC = "AA:BB:CC:DD:EE:FF"
ACCESS_CODE = "AB12CD34E"  # 9 caractères alphanumériques

# UUID des caractéristiques lues après la mesure (valeurs de coordinator.py).
UUID_RAW_SENSORS = "70ea0005-7a29-4fdf-93d2-838665e72677"
UUID_ACCELEROMETER = "70ea000a-7a29-4fdf-93d2-838665e72677"
UUID_SERIAL_NUMBER = "70ea0020-7a29-4fdf-93d2-838665e72677"
UUID_HW_VERSION = "70ea0021-7a29-4fdf-93d2-838665e72677"
UUID_SW_VERSION = "70ea0022-7a29-4fdf-93d2-838665e72677"


def build_frame(
    temp_c: float = 25.02,
    ph: float = 7.4,
    orp_mv: int = 700,
    conductivity: int | None = 1200,
    salinity: float = 3.5,
    battery_pct: int = 80,
    battery_adc: int = 4000,
    echo: bool = False,
    prefixed: bool = False,
) -> bytes:
    """Trame de 18 octets (19 avec `prefixed`, un octet d'en-tête en plus).

    Champs décodés par protocol.parse_raw_frame, tous big-endian :
    température ×100, pH ×10, ORP, conductivité (0xFFFF = sonde absente),
    salinité ×100, batterie %, batterie ADC. `echo` place le marqueur « B »
    que le mode passif reconnaît comme un écho.
    """
    cond = 0xFFFF if conductivity is None else conductivity
    body = bytearray(3)  # en-tête de 3 octets
    body += round(temp_c * 100).to_bytes(2, "big")
    body += round(ph * 10).to_bytes(2, "big")
    body += int(orp_mv).to_bytes(2, "big")
    body += int(cond).to_bytes(2, "big")
    body += round(salinity * 100).to_bytes(2, "big")
    body += bytes([battery_pct])
    body += int(battery_adc).to_bytes(2, "big")
    body += bytes([0xB0 if echo else 0x00, 0x00])  # 2 octets de fin
    assert len(body) == 18
    return (b"\xaa" + bytes(body)) if prefixed else bytes(body)


def clean_hex(frame: bytes) -> str:
    """Trame telle que stockée (sans l'octet d'en-tête des trames de 19 octets)."""
    return (frame[1:] if len(frame) == 19 else frame).hex().upper()


class FakeBlueClient:
    """Remplace BleakClient : authentification, déclenchement, notification, lectures.

    - `frames` : trames livrées par notification à chaque écriture du déclencheur ;
    - `auth_ok` : octet de statut d'authentification lu (True → 0x01, False → 0x00,
      None → la lecture échoue) ;
    - `write_errors` : exceptions levées successivement par write_gatt_char ;
    - `reads` : valeurs des lectures GATT (UUID → octets) ; absentes → erreur.
    """

    def __init__(
        self,
        frames: list[bytes] | None = None,
        auth_ok: bool | None = True,
        write_errors: list[BaseException | None] | None = None,
        reads: dict[str, bytes] | None = None,
    ) -> None:
        self.frames = list(frames or [])
        self.auth_ok = auth_ok
        self.write_errors = list(write_errors or [])
        self.reads = (
            {
                UUID_RAW_SENSORS: bytes.fromhex("0102030405"),
                UUID_ACCELEROMETER: (0).to_bytes(2, "big", signed=True)
                + (900).to_bytes(2, "big", signed=True)  # y > 700 → vertical
                + (0).to_bytes(2, "big", signed=True),
                UUID_SERIAL_NUMBER: b"SN12345\x00",
                UUID_HW_VERSION: b"WA000100\x00",
                UUID_SW_VERSION: b"CLOUD42\x00",
            }
            if reads is None
            else dict(reads)
        )
        self.is_connected = True
        self.writes: list[tuple[str, bytes]] = []
        self.notify_started = False
        self.notify_stopped = False
        self.disconnected = False
        self._handler: Callable[[Any, bytearray], None] | None = None

    async def start_notify(self, uuid: str, handler: Callable) -> None:
        self.notify_started = True
        self._handler = handler

    async def stop_notify(self, uuid: str) -> None:
        self.notify_stopped = True

    async def write_gatt_char(self, uuid: str, data, response: bool = True) -> None:
        self.writes.append((uuid, bytes(data)))
        if self.write_errors:
            error = self.write_errors.pop(0)
            if error is not None:
                raise error
        # Écriture du déclencheur (0x02) : la sonde répond par une notification.
        if bytes(data) == b"\x02" and self._handler is not None and self.frames:
            self._handler(None, bytearray(self.frames.pop(0)))

    async def read_gatt_char(self, uuid: str) -> bytearray:
        if uuid.startswith("1fb20002"):  # statut d'authentification
            if self.auth_ok is None:
                raise OSError("auth status unavailable")
            return bytearray([1 if self.auth_ok else 0])
        if uuid not in self.reads:
            raise OSError(f"cannot read {uuid}")
        return bytearray(self.reads[uuid])

    async def disconnect(self) -> None:
        self.disconnected = True
        self.is_connected = False
