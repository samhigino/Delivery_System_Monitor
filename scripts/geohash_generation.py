import pandas as pd
from pathlib import Path

ROOT = Path.cwd().parent if Path.cwd().name == "scripts" else Path.cwd()
RAW_DIR = ROOT / "data" / "raw"
PRC_DIR = ROOT / "data" / "processed"

# Função para obter o geohash de uma coordenada
def geohash_encode(lat, lon, prefix="", level=1, maxlevel=8):
    return

# Função para obter as coordenadas a partir de um geohash
def geohash_decode(hash, levels=8):
    return

