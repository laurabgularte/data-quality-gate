from __future__ import annotations

import pandas as pd

from .models import ValidationIssue, ValidationReport


def run_quality_gate(df: pd.DataFrame, schema: dict) -> ValidationReport:
    issues: list[ValidationIssue] = []
    bad_indices: set[int] = set()

    required_cols = schema.get("required_columns", [])
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing_cols)}")

    total_rows = len(df)
    if total_rows == 0:
        return ValidationReport(
            total_rows=0,
            valid_rows_count=0,
            rejected_rows_count=0,
            issues=[],
            valid_df=df.copy(),
            rejected_df=df.copy(),
        )

    # 1. Campos obrigatórios não nulos / não vazios
    for col in schema.get("not_null_columns", []):
        for idx, val in df[col].items():
            if val == "" or val.lower() in {"nan", "none", "null", "nat"}:
                issues.append(
                    ValidationIssue(
                        row_number=int(idx) + 2,
                        column=col,
                        rule="not_null",
                        message="Campo obrigatório vazio ou nulo.",
                        value=val,
                    )
                )
                bad_indices.add(int(idx))

    # 2. Duplicidade em colunas únicas
    unique_cols = schema.get("unique_columns", [])
    if unique_cols:
        seen_keys: dict[tuple, int] = {}
        for idx, row in df.iterrows():
            key = tuple(row[c] for c in unique_cols)
            if any(k == "" for k in key):
                continue
            if key in seen_keys:
                first_row = seen_keys[key] + 2
                issues.append(
                    ValidationIssue(
                        row_number=int(idx) + 2,
                        column=" + ".join(unique_cols),
                        rule="unique",
                        message=f"Chave duplicada (já apareceu na linha {first_row}).",
                        value=" | ".join(key),
                    )
                )
                bad_indices.add(int(idx))
            else:
                seen_keys[key] = int(idx)

    # 3. Colunas de data
    for col in schema.get("date_columns", []):
        for idx, val in df[col].items():
            if val == "":
                continue
            parsed = pd.to_datetime(val, errors="coerce")
            if pd.isna(parsed):
                issues.append(
                    ValidationIssue(
                        row_number=int(idx) + 2,
                        column=col,
                        rule="valid_date",
                        message="Data inválida ou fora de formato reconhecível.",
                        value=val,
                    )
                )
                bad_indices.add(int(idx))

    # 4. Colunas numéricas e intervalos (min/max)
    numeric_rules: dict = schema.get("numeric_columns", {})
    for col, bounds in numeric_rules.items():
        min_val = bounds.get("min")
        max_val = bounds.get("max")
        for idx, val in df[col].items():
            if val == "":
                continue
            normalized = val.replace(",", ".")
            try:
                num = float(normalized)
                if pd.isna(num):
                    raise ValueError("NaN")
            except ValueError:
                issues.append(
                    ValidationIssue(
                        row_number=int(idx) + 2,
                        column=col,
                        rule="numeric_type",
                        message="Valor não numérico.",
                        value=val,
                    )
                )
                bad_indices.add(int(idx))
                continue

            if min_val is not None and num < float(min_val):
                issues.append(
                    ValidationIssue(
                        row_number=int(idx) + 2,
                        column=col,
                        rule="min_value",
                        message=f"Valor menor que o mínimo permitido ({min_val}).",
                        value=val,
                    )
                )
                bad_indices.add(int(idx))

            if max_val is not None and num > float(max_val):
                issues.append(
                    ValidationIssue(
                        row_number=int(idx) + 2,
                        column=col,
                        rule="max_value",
                        message=f"Valor maior que o máximo permitido ({max_val}).",
                        value=val,
                    )
                )
                bad_indices.add(int(idx))

    # 5. Domínio de valores permitidos
    allowed_rules: dict = schema.get("allowed_values", {})
    for col, allowed in allowed_rules.items():
        allowed_set = {str(x).strip() for x in allowed}
        for idx, val in df[col].items():
            if val == "":
                continue
            if val not in allowed_set:
                issues.append(
                    ValidationIssue(
                        row_number=int(idx) + 2,
                        column=col,
                        rule="allowed_values",
                        message=f"Valor fora da lista permitida ({sorted(allowed_set)}).",
                        value=val,
                    )
                )
                bad_indices.add(int(idx))

    rejected_df = df.loc[sorted(bad_indices)].copy()
    valid_df = df.drop(index=sorted(bad_indices)).copy()

    return ValidationReport(
        total_rows=total_rows,
        valid_rows_count=len(valid_df),
        rejected_rows_count=len(rejected_df),
        issues=issues,
        valid_df=valid_df,
        rejected_df=rejected_df,
    )
