"""
Cliente Modbus TCP com polling em thread separada, suporte a 4X/FP
e escrita read-modify-write para registradores de bitmask.
"""

import json
import struct
import threading
import time
from typing import Any, Callable, Dict, Optional

from pymodbus.client import ModbusTcpClient

from config.settings import (
    CONNECTION_PROFILES,
    DEFAULT_PROFILE,
    DEFAULT_SCAN_TIME,
    FLOAT_BYTE_ORDER,
    FLOAT_WORD_ORDER,
    MODBUS_TIMEOUT,
    TAGS_MAP_PATH,
)


class ModbusClientService:
    def __init__(
        self,
        on_data: Optional[Callable[[Dict[str, Any], float], None]] = None,
        on_status: Optional[Callable[[bool, str], None]] = None,
    ):
        profile = CONNECTION_PROFILES[DEFAULT_PROFILE]
        self.host: str = profile["host"]
        self.port: int = profile["port"]
        self.scan_time: float = DEFAULT_SCAN_TIME

        self.on_data = on_data
        self.on_status = on_status

        self.tags_map: Dict[str, dict] = self._load_tags_map()
        self._client: Optional[ModbusTcpClient] = None
        self._io_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.connected: bool = False

    @staticmethod
    def _load_tags_map() -> Dict[str, dict]:
        with open(TAGS_MAP_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def configure(self, host: str, port: int, scan_time: float = DEFAULT_SCAN_TIME) -> None:
        self.host = host
        self.port = int(port)
        self.scan_time = max(0.2, float(scan_time))

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3.0)
        self._disconnect()

    def _connect(self) -> bool:
        with self._io_lock:
            if self._client:
                self._client.close()
            self._client = ModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=MODBUS_TIMEOUT,
            )
            ok = self._client.connect()
            self._set_status(ok, "" if ok else f"Falha ao conectar em {self.host}:{self.port}")
            return ok

    def _disconnect(self) -> None:
        with self._io_lock:
            if self._client:
                self._client.close()
                self._client = None
        self._set_status(False, "Desconectado")

    def _set_status(self, connected: bool, message: str = "") -> None:
        if self.connected != connected or message:
            self.connected = connected
            if self.on_status:
                self.on_status(connected, message)

    @staticmethod
    def _regs_to_float(regs: list[int]) -> float:
        r0, r1 = regs[0], regs[1]
        if FLOAT_WORD_ORDER == "little":
            r0, r1 = r1, r0
        fmt_pack = ">HH" if FLOAT_BYTE_ORDER == "big" else "<HH"
        fmt_float = ">f" if FLOAT_BYTE_ORDER == "big" else "<f"
        return struct.unpack(fmt_float, struct.pack(fmt_pack, r0, r1))[0]

    @staticmethod
    def _float_to_regs(value: float) -> list[int]:
        fmt_float = ">f" if FLOAT_BYTE_ORDER == "big" else "<f"
        fmt_pack = ">HH" if FLOAT_BYTE_ORDER == "big" else "<HH"
        r0, r1 = struct.unpack(fmt_pack, struct.pack(fmt_float, float(value)))
        if FLOAT_WORD_ORDER == "little":
            r0, r1 = r1, r0
        return [r0, r1]

    def _read_all_tags(self) -> Dict[str, Any]:
        """Lê todas as tags com acesso R ou RW, evitando leituras duplicadas de bitmasks."""
        values: Dict[str, Any] = {}
        word_cache: Dict[int, int] = {}

        with self._io_lock:
            if not self._client or not self._client.connected:
                raise ConnectionError("Cliente Modbus desconectado")

            for tag_name, meta in self.tags_map.items():
                if meta["access"] not in ("R", "RW"):
                    continue

                addr = meta["address"]
                tag_type = meta["type"]
                div = meta.get("div", 1)
                bit = meta.get("bit")

                if tag_type == "FP":
                    resp = self._client.read_holding_registers(addr, count=2)
                    if resp.isError():
                        raise IOError(f"Erro lendo FP {tag_name} ({addr}): {resp}")
                    raw = self._regs_to_float(resp.registers)
                    values[tag_name] = round(raw / div, 3)

                elif tag_type == "4X":
                    if addr not in word_cache:
                        resp = self._client.read_holding_registers(addr, count=1)
                        if resp.isError():
                            raise IOError(f"Erro lendo 4X {tag_name} ({addr}): {resp}")
                        word_cache[addr] = resp.registers[0]

                    raw_word = word_cache[addr]
                    if bit is not None:
                        values[tag_name] = (raw_word >> bit) & 1
                    else:
                        values[tag_name] = round(raw_word / div, 3) if div != 1 else raw_word

        return values

    def write_tag(self, tag_name: str, value: Any) -> bool:
        """Escreve em uma tag W ou RW, usando read-modify-write para bitmasks."""
        if tag_name not in self.tags_map:
            raise ValueError(f"Tag desconhecida: {tag_name}")

        meta = self.tags_map[tag_name]
        if meta["access"] not in ("W", "RW"):
            raise PermissionError(f"Tag {tag_name} é somente leitura")

        addr = meta["address"]
        tag_type = meta["type"]
        div = meta.get("div", 1)
        bit = meta.get("bit")

        with self._io_lock:
            if not self._client or not self._client.connected:
                return False

            try:
                if tag_type == "FP":
                    regs = self._float_to_regs(float(value) * div)
                    resp = self._client.write_registers(addr, regs)
                    return not resp.isError()

                elif tag_type == "4X":
                    if bit is not None:
                        # Read-Modify-Write para não sobrescrever outros bits da palavra
                        current = self._client.read_holding_registers(addr, count=1)
                        if current.isError():
                            return False
                        word = current.registers[0]
                        if int(value):
                            word |= (1 << bit)
                        else:
                            word &= ~(1 << bit)
                        resp = self._client.write_register(addr, word)
                        return not resp.isError()
                    else:
                        raw_int = int(round(float(value) * div))
                        resp = self._client.write_register(addr, raw_int)
                        return not resp.isError()
            except Exception as exc:
                self._set_status(False, f"Erro na escrita de {tag_name}: {exc}")
                return False

        return False

    def _poll_loop(self) -> None:
        while not self._stop_event.is_set():
            cycle_start = time.monotonic()

            if not self.connected:
                self._connect()

            if self.connected:
                try:
                    data = self._read_all_tags()
                    if self.on_data:
                        self.on_data(data, time.time())
                except Exception as exc:
                    self._set_status(False, f"Perda de comunicação: {exc}")

            elapsed = time.monotonic() - cycle_start
            sleep_time = max(0.05, self.scan_time - elapsed)
            self._stop_event.wait(sleep_time)


if __name__ == "__main__":
    # Teste rápido contra o simulador local (rode simulator/run_simulator.py em outro terminal)
    def print_status(ok, msg):
        print(f"[STATUS] Conectado={ok} | {msg}")

    def print_data(data, ts):
        print(
            f"[LEITURA] Temp={data.get('ve.temperatura')} °C | "
            f"Vazão={data.get('ve.vazao')} m³/h | "
            f"Freq={data.get('ve.frequencia')} Hz | "
            f"Comp(raw)={data.get('ve.st_compressor')}"
        )

    client = ModbusClientService(on_data=print_data, on_status=print_status)
    client.start()
    try:
        time.sleep(3)
        print("Testando escrita: ve.sp_termo = 25 °C ->", client.write_tag("ve.sp_termo", 25))
        print("Testando escrita bitmask: ve.liga_aq1 = 1 ->", client.write_tag("ve.liga_aq1", 1))
        time.sleep(2)
    finally:
        client.stop()