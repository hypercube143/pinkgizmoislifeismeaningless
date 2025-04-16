import os
import json

TIME_ZONE = "Pacific/Auckland" # "Antarctica/McMurdo"

API_DIR = "api"
os.makedirs(API_DIR, exist_ok=True)
DATA_DIR = f"{API_DIR}/data"
os.makedirs(DATA_DIR, exist_ok=True)
COUNTS_DIR = f"{DATA_DIR}/counts"
os.makedirs(COUNTS_DIR, exist_ok=True)
ORACLE_DIR = f"{DATA_DIR}/oracle"
os.makedirs(ORACLE_DIR, exist_ok=True)
STATUS_DIR = f"{DATA_DIR}/status"


def time_elapsed(now_timestamp, start_timestmap, dt_expected):
    return (now_timestamp - start_timestmap) >= dt_expected


def get_config_value(key):
    with open(f"{DATA_DIR}/config.json", "r") as f:
        value = json.loads(f.read())[key]
    return value