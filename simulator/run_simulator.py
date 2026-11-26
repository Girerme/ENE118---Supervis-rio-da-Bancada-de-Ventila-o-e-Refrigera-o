"""
Inicializa o simulador Modbus TCP local para a Bancada de Ventilação e Refrigeração.
Uso: python simulator/run_simulator.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

JSON_PATH = Path(__file__).resolve().parent / "setup_ventilacao.json"


def main():
    bin_dir = Path(sys.executable).parent
    exe_name = "pymodbus.simulator.exe" if sys.platform == "win32" else "pymodbus.simulator"
    simulator_bin = bin_dir / exe_name

    if not simulator_bin.exists():
        found = shutil.which("pymodbus.simulator")
        if not found:
            raise FileNotFoundError("Executável 'pymodbus.simulator' não encontrado. Rode: pip install \"pymodbus[simulator]\"")
        simulator_bin = Path(found)

    cmd = [
        str(simulator_bin),
        "--json_file",
        str(JSON_PATH),
        "--modbus_server",
        "server",
        "--modbus_device",
        "device",
    ]
    print(f"Iniciando simulador Modbus TCP em 127.0.0.1:5020 usando {JSON_PATH.name}...")
    print("Pressione Ctrl+C para encerrar.")
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nSimulador encerrado.")


if __name__ == "__main__":
    main()