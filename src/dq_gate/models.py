from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ValidationIssue:
    row_number: int  # considerando cabeçalho na linha 1, dados começam na 2
    column: str
    rule: str
    message: str
    value: str


@dataclass
class ValidationReport:
    total_rows: int
    valid_rows_count: int
    rejected_rows_count: int
    issues: list[ValidationIssue] = field(default_factory=list)
    valid_df: pd.DataFrame = field(default_factory=pd.DataFrame)
    rejected_df: pd.DataFrame = field(default_factory=pd.DataFrame)

    @property
    def passed(self) -> bool:
        return self.rejected_rows_count == 0 and len(self.issues) == 0

    def to_summary_dict(self) -> dict:
        by_rule: dict[str, int] = {}
        for issue in self.issues:
            by_rule[issue.rule] = by_rule.get(issue.rule, 0) + 1

        return {
            "passed": self.passed,
            "total_rows": self.total_rows,
            "valid_rows": self.valid_rows_count,
            "rejected_rows": self.rejected_rows_count,
            "total_issues": len(self.issues),
            "issues_by_rule": by_rule,
        }
