from pathlib import Path

# Projecty root directory
ROOT = Path(__file__).parent

# Data directory
DATA_DIR = ROOT / "data"

# Token database
TOKENDB = DATA_DIR / "tokendb.json"

API_CONFIG = {
    "host": "localhost",
    "port": 8222
}