"""Agrega metricas de relatorios Markdown de avaliacao.

Este script le arquivos por questao (ex.: 1.md, 2.md, ...), extrai as tabelas
de metricas e qualidade, e gera:
1) JSON consolidado para consumo por outros scripts.
2) Markdown com tabelas resumo para documentacao.

Uso recomendado:
python scripts/aggregate_evaluation_results.py \
  --input-dir resultados \
  --output-dir docs/artefatos
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


MODEL_NAME_MAP = {
    "Anthropic": "Claude (Anthropic)",
    "Ollama": "Qwen (via Ollama)",
}


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = "".join(char for char in normalized if not unicodedata.combining(char))
    return ascii_only.strip().lower()


def parse_numeric_percent(value: str) -> Optional[float]:
    raw = value.strip()
    if normalize_text(raw) in {"n/a", "na", ""}:
        return None
    raw = raw.replace("%", "").replace(",", ".").strip()
    try:
        return float(raw)
    except ValueError:
        return None


def parse_numeric_score(value: str) -> Optional[float]:
    raw = value.strip()
    if normalize_text(raw) in {"n/a", "na", ""}:
        return None
    raw = raw.replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return None


def safe_mean(values: Iterable[Optional[float]]) -> Optional[float]:
    valid_values = [item for item in values if item is not None and not math.isnan(item)]
    return sum(valid_values) / len(valid_values) if valid_values else None


def extract_question_number(file_path: Path) -> Optional[int]:
    match = re.match(r"(\d+)\.md$", file_path.name)
    return int(match.group(1)) if match else None


def parse_markdown_table(table_block: str) -> List[List[str]]:
    rows: List[List[str]] = []
    for line in table_block.splitlines():
        stripped_line = line.strip()
        if not stripped_line.startswith("|"):
            continue
        if re.match(r"^\|\s*-+\s*\|", stripped_line):
            continue
        rows.append([cell.strip() for cell in stripped_line.strip("|").split("|")])
    return rows


def extract_table_after_header(markdown_text: str, header_text: str) -> Optional[str]:
    index = markdown_text.find(header_text)
    if index < 0:
        return None

    tail = markdown_text[index + len(header_text) :]
    table_lines: List[str] = []
    table_started = False

    for line in tail.splitlines():
        if line.strip().startswith("|"):
            table_started = True
            table_lines.append(line)
            continue
        if table_started:
            break

    return "\n".join(table_lines) if table_lines else None


def resolve_default_paths() -> Tuple[Path, Path]:
    repository_root = Path(__file__).resolve().parent.parent
    default_input_dir = repository_root / "resultados"
    default_output_dir = repository_root / "docs" / "artefatos"
    return default_input_dir, default_output_dir


def parse_arguments() -> argparse.Namespace:
    default_input_dir, default_output_dir = resolve_default_paths()

    parser = argparse.ArgumentParser(
        description=(
            "Consolida metricas (TEN, TEF, TSE e qualidade) a partir de relatorios "
            "Markdown por questao."
        )
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=default_input_dir,
        help="Diretorio com os arquivos Markdown por questao (padrao: resultados/).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output_dir,
        help="Diretorio de saida dos artefatos consolidados (padrao: docs/artefatos/).",
    )
    parser.add_argument(
        "--output-json",
        default="evaluation_metrics_aggregated.json",
        help="Nome do arquivo JSON consolidado.",
    )
    parser.add_argument(
        "--output-markdown",
        default="evaluation_tables_summary.md",
        help="Nome do arquivo Markdown com tabelas consolidadas.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    report_files = sorted(
        args.input_dir.glob("*.md"),
        key=lambda path: extract_question_number(path) if extract_question_number(path) is not None else 10_000,
    )

    metric_rows: List[Dict[str, object]] = []
    quality_rows: List[Dict[str, object]] = []

    for report_path in report_files:
        question_number = extract_question_number(report_path)
        if question_number is None:
            continue

        report_text = report_path.read_text(encoding="utf-8")
        metrics_table_block = extract_table_after_header(report_text, "### Metricas de Erro")
        quality_table_block = extract_table_after_header(report_text, "### Rubrica de Qualidade")

        if metrics_table_block:
            metric_table = parse_markdown_table(metrics_table_block)
            if metric_table and normalize_text(metric_table[0][0]) == "modelo":
                for row in metric_table[1:]:
                    if len(row) < 5:
                        continue
                    model_name, evaluation_group, ten_value, tef_value, tse_value = row[:5]
                    metric_rows.append(
                        {
                            "question": question_number,
                            "model": model_name.strip(),
                            "group": evaluation_group.strip(),
                            "TEN": parse_numeric_percent(ten_value),
                            "TEF": parse_numeric_percent(tef_value),
                            "TSE": parse_numeric_percent(tse_value),
                        }
                    )

        if quality_table_block:
            quality_table = parse_markdown_table(quality_table_block)
            if quality_table and normalize_text(quality_table[0][0]) == "modelo":
                for row in quality_table[1:]:
                    if len(row) < 7:
                        continue
                    model_name, evaluation_group, average_score = row[0], row[1], row[6]
                    quality_rows.append(
                        {
                            "question": question_number,
                            "model": model_name.strip(),
                            "group": evaluation_group.strip(),
                            "quality": parse_numeric_score(average_score),
                        }
                    )

    metrics_by_scenario: Dict[Tuple[str, str], Dict[str, List[Optional[float]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for metric_row in metric_rows:
        scenario = (str(metric_row["model"]), str(metric_row["group"]))
        for metric_name in ("TEN", "TEF", "TSE"):
            metrics_by_scenario[scenario][metric_name].append(metric_row[metric_name])

    quality_by_scenario: Dict[Tuple[str, str], List[Optional[float]]] = defaultdict(list)
    for quality_row in quality_rows:
        scenario = (str(quality_row["model"]), str(quality_row["group"]))
        quality_by_scenario[scenario].append(quality_row["quality"])

    scenario_keys = sorted(metrics_by_scenario.keys(), key=lambda item: (item[1], item[0]))
    scenario_summary: List[Dict[str, object]] = []

    for scenario_key in scenario_keys:
        model_name, evaluation_group = scenario_key
        scenario_summary.append(
            {
                "model": MODEL_NAME_MAP.get(model_name, model_name),
                "group": evaluation_group,
                "TEN": safe_mean(metrics_by_scenario[scenario_key]["TEN"]),
                "TEF": safe_mean(metrics_by_scenario[scenario_key]["TEF"]),
                "TSE": safe_mean(metrics_by_scenario[scenario_key]["TSE"]),
                "quality": safe_mean(quality_by_scenario.get(scenario_key, [])),
            }
        )

    metrics_by_group: Dict[str, Dict[str, List[Optional[float]]]] = defaultdict(lambda: defaultdict(list))
    quality_by_group: Dict[str, List[Optional[float]]] = defaultdict(list)
    for scenario in scenario_summary:
        group_name = str(scenario["group"])
        metrics_by_group[group_name]["TEN"].append(scenario["TEN"])
        metrics_by_group[group_name]["TEF"].append(scenario["TEF"])
        metrics_by_group[group_name]["TSE"].append(scenario["TSE"])
        quality_by_group[group_name].append(scenario["quality"])

    group_summary: List[Dict[str, object]] = []
    for group_name in sorted(metrics_by_group.keys()):
        group_summary.append(
            {
                "group": group_name,
                "TEN": safe_mean(metrics_by_group[group_name]["TEN"]),
                "TEF": safe_mean(metrics_by_group[group_name]["TEF"]),
                "TSE": safe_mean(metrics_by_group[group_name]["TSE"]),
                "quality": safe_mean(quality_by_group[group_name]),
            }
        )

    behavior_summary = {
        "TEN_gt_0": 0,
        "TEF_gt_0": 0,
        "TSE_gt_0": 0,
        "NA": 0,
        "quality_5": 0,
        "total": 0,
    }

    quality_index = {
        (row["question"], row["model"], row["group"]): row["quality"] for row in quality_rows
    }

    for metric_row in metric_rows:
        behavior_summary["total"] += 1

        if (
            metric_row["TEN"] is None
            and metric_row["TEF"] is None
            and metric_row["TSE"] is None
        ):
            behavior_summary["NA"] += 1
            continue

        if metric_row["TEN"] is not None and metric_row["TEN"] > 0:
            behavior_summary["TEN_gt_0"] += 1
        if metric_row["TEF"] is not None and metric_row["TEF"] > 0:
            behavior_summary["TEF_gt_0"] += 1
        if metric_row["TSE"] is not None and metric_row["TSE"] > 0:
            behavior_summary["TSE_gt_0"] += 1

        quality_value = quality_index.get(
            (metric_row["question"], metric_row["model"], metric_row["group"])
        )
        if quality_value is not None and abs(float(quality_value) - 5.0) < 1e-9:
            behavior_summary["quality_5"] += 1

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_output_path = args.output_dir / args.output_json
    markdown_output_path = args.output_dir / args.output_markdown

    json_output_path.write_text(
        json.dumps(
            {
                "per_scenario": scenario_summary,
                "group_summary": group_summary,
                "behavior": behavior_summary,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    def format_percent(value: Optional[float]) -> str:
        return "N/A" if value is None else f"{value:.2f}%"

    def format_quality(value: Optional[float]) -> str:
        return "N/A" if value is None else f"{value:.2f}"

    total_count = behavior_summary["total"] or 1

    def count_to_percent(value: int) -> float:
        return 100.0 * value / total_count

    markdown_lines: List[str] = []
    markdown_lines.append("# Tabelas Consolidadas (Geradas Automaticamente)\n")
    markdown_lines.append(
        f"Fonte: agregacao de {len(report_files)} arquivos em '{args.input_dir.as_posix()}'.\n"
    )

    markdown_lines.append("\n## Tabela 1 - Desempenho medio agregado por condicao\n")
    markdown_lines.append("| Condicao | TEN | TEF | TSE | Qualidade |\n")
    markdown_lines.append("|---|---:|---:|---:|---:|\n")
    for row in group_summary:
        markdown_lines.append(
            f"| {row['group']} | {format_percent(row['TEN'])} | {format_percent(row['TEF'])} | {format_percent(row['TSE'])} | {format_quality(row['quality'])} |\n"
        )

    markdown_lines.append("\n## Tabela 2 - Desempenho medio por modelo e condicao\n")
    markdown_lines.append("| Modelo | Condicao | TEN | TEF | TSE | Qualidade |\n")
    markdown_lines.append("|---|---|---:|---:|---:|---:|\n")
    for row in scenario_summary:
        markdown_lines.append(
            f"| {row['model']} | {row['group']} | {format_percent(row['TEN'])} | {format_percent(row['TEF'])} | {format_percent(row['TSE'])} | {format_quality(row['quality'])} |\n"
        )

    markdown_lines.append("\n## Tabela 3 - Comportamento observado do agente juiz\n")
    markdown_lines.append("| Comportamento observado | Ocorrencias | Percentual |\n")
    markdown_lines.append("|---|---:|---:|\n")
    markdown_lines.append(
        f"| Respostas com TEN > 0% | {behavior_summary['TEN_gt_0']} | {count_to_percent(behavior_summary['TEN_gt_0']):.2f}% |\n"
    )
    markdown_lines.append(
        f"| Respostas com TEF > 0% | {behavior_summary['TEF_gt_0']} | {count_to_percent(behavior_summary['TEF_gt_0']):.2f}% |\n"
    )
    markdown_lines.append(
        f"| Respostas com TSE > 0% | {behavior_summary['TSE_gt_0']} | {count_to_percent(behavior_summary['TSE_gt_0']):.2f}% |\n"
    )
    markdown_lines.append(
        f"| Respostas N/A (sem resposta) | {behavior_summary['NA']} | {count_to_percent(behavior_summary['NA']):.2f}% |\n"
    )
    markdown_lines.append(
        f"| Respostas com qualidade 5.0 | {behavior_summary['quality_5']} | {count_to_percent(behavior_summary['quality_5']):.2f}% |\n"
    )
    markdown_lines.append(f"| Total de avaliacoes | {behavior_summary['total']} | 100.00% |\n")

    markdown_output_path.write_text("".join(markdown_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
