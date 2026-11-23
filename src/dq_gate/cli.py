from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from .loader import load_schema, load_tabular_file
from .validator import run_quality_gate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dq-gate",
        description="Validador de qualidade de dados antes de carga em banco ou BI.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_val = sub.add_parser("validate", help="Valida uma planilha CSV/XLSX contra um schema JSON.")
    p_val.add_argument("input_file", help="Caminho do arquivo .csv, .xlsx ou .xls")
    p_val.add_argument("--schema", required=True, help="Caminho do arquivo JSON com regras")
    p_val.add_argument("--out", default="saida", help="Pasta de saída dos relatórios e arquivos")
    p_val.add_argument("--sheet", default="0", help="Nome ou índice da aba (para Excel)")

    return parser


def _parse_sheet(raw: str) -> str | int:
    return int(raw) if raw.isdigit() else raw


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        schema = load_schema(args.schema)
        df = load_tabular_file(args.input_file, sheet_name=_parse_sheet(args.sheet))
        report = run_quality_gate(df, schema)

        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)

        report.valid_df.to_csv(out_dir / "validos.csv", index=False, encoding="utf-8")
        report.rejected_df.to_csv(out_dir / "erros_validacao.csv", index=False, encoding="utf-8")

        issues_df = pd.DataFrame([asdict(i) for i in report.issues])
        issues_df.to_csv(out_dir / "detalhes_problemas.csv", index=False, encoding="utf-8")

        summary = report.to_summary_dict()
        (out_dir / "relatorio_qualidade.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0 if report.passed else 1

    except (OSError, ValueError, KeyError, TypeError, pd.errors.ParserError) as exc:
        print(f"Erro na execução: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
