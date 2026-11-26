from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TAGS_MAP_PATH = BASE_DIR / "config" / "tags_map.json"
DB_PATH = BASE_DIR / "database" / "historico.db"

# Perfis de conexão disponíveis na tela de configuração
CONNECTION_PROFILES = {
    "CLP_LAB": {
        "label": "CLP LABORATÓRIO",
        "host": "10.15.30.183",
        "port": 502,
        "unit_id": 1,
    },
    "SIMULADOR": {
        "label": "SIMULADOR LOCAL",
        "host": "127.0.0.1",
        "port": 5020,
        "unit_id": 1,
    },
}

# Perfil ativo ao iniciar o aplicativo
DEFAULT_PROFILE = "SIMULADOR"

# Parâmetros de comunicação e aquisição
DEFAULT_SCAN_TIME = 1.0          # segundos entre ciclos de leitura
MODBUS_TIMEOUT = 2.0             # timeout de resposta do socket (s)
STALE_DATA_THRESHOLD = 3.0       # tempo sem atualização para marcar dado como desatualizado (s)

# Ordem de bytes/palavras para registradores FP (32-bit float)
# Ajustar no laboratório se os floats vierem invertidos ("big" ou "little")
FLOAT_BYTE_ORDER = "big"
FLOAT_WORD_ORDER = "big"