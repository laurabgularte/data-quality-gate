from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def load_schema(schema_path: str | Path) -> dict:
    path = Path(schema_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de schema não encontrado: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_tabular_file(file_path: str | Path, sheet_name: str | int | None = 0) -> pd.DataFrame:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(path, dtype=str, keep_default_na=False)
    elif suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(path, sheet_name=sheet_name, dtype=str, keep_default_na=False)
    else:
        raise ValueError(f"Formato de arquivo não suportado: '{suffix}'. Use .csv, .xlsx ou .xls.")

    # Limpa espaços extras nos nomes das colunas e nos valores textuais
    df.columns = [str(col).strip() for col in df.columns]
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()

    return df
