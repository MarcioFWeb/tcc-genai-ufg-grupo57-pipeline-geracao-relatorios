"""Gera matriz TEN em CSV e heatmap em SVG a partir dos relatorios por questao.

Uso recomendado:
python scripts/build_figure4_ten_heatmap.py \
  --input-dir resultados \
  --output-dir docs/artefatos
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


SCENARIOS: List[Tuple[str, str, str]] = [
    ("Gemini", "Sem RAG", "Gemini"),
    ("Anthropic", "Sem RAG", "Claude (Anthropic)"),
    ("Ollama", "Sem RAG", "Qwen"),
    ("Gemini", "Com RAG", "Gemini"),
    ("Anthropic", "Com RAG", "Claude (Anthropic)"),
    ("Ollama", "Com RAG", "Qwen"),
]


def extract_question_number(file_path: Path) -> Optional[int]:
    match = re.search(r"(\d+)\.md$", file_path.name)
    return int(match.group(1)) if match else None


def extract_ten_table(markdown_text: str) -> Dict[Tuple[str, str], float]:
    header_match = re.search(r"^###\s*Metricas de Erro\s*$", markdown_text, re.M | re.I)
    if not header_match:
        return {}

    tail = markdown_text[header_match.end() :]
    section_end = re.search(r"^###\s*Rubrica de Qualidade", tail, re.M | re.I)
    section = tail[: section_end.start()] if section_end else tail

    rows: List[List[str]] = []
    for line in section.splitlines():
        stripped_line = line.strip()
        if not stripped_line.startswith("|"):
            continue
        if re.match(r"^\|\s*-+\s*\|", stripped_line):
            continue
        rows.append([cell.strip() for cell in stripped_line.strip("|").split("|")])

    if not rows:
        return {}

    header = [item.lower() for item in rows[0]]
    try:
        model_index = header.index("modelo")
        group_index = header.index("grupo")
        ten_index = header.index("ten")
    except ValueError:
        return {}

    values: Dict[Tuple[str, str], float] = {}
    for row in rows[1:]:
        if len(row) <= max(model_index, group_index, ten_index):
            continue

        model_name = row[model_index].strip()
        evaluation_group = row[group_index].strip()
        ten_raw = row[ten_index].strip().replace("%", "").replace(",", ".")

        if ten_raw.upper() in {"N/A", "NA", ""}:
            values[(model_name, evaluation_group)] = math.nan
            continue

        try:
            values[(model_name, evaluation_group)] = float(ten_raw)
        except ValueError:
            values[(model_name, evaluation_group)] = math.nan

    return values


def resolve_default_paths() -> tuple[Path, Path]:
    repository_root = Path(__file__).resolve().parent.parent
    default_input_dir = repository_root / "resultados"
    default_output_dir = repository_root / "docs" / "artefatos"
    return default_input_dir, default_output_dir


def parse_arguments() -> argparse.Namespace:
    default_input_dir, default_output_dir = resolve_default_paths()

    parser = argparse.ArgumentParser(
        description="Gera artefatos da Figura 4 (matriz TEN): CSV e SVG."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=default_input_dir,
        help="Diretorio com relatorios Markdown por questao.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output_dir,
        help="Diretorio de saida para os arquivos gerados.",
    )
    parser.add_argument(
        "--csv-name",
        default="figure4_ten_heatmap.csv",
        help="Nome do arquivo CSV de saida.",
    )
    parser.add_argument(
        "--svg-name",
        default="figure4_ten_heatmap.svg",
        help="Nome do arquivo SVG de saida.",
    )
    return parser.parse_args()


def hex_to_rgb(color_hex: str) -> Tuple[int, int, int]:
    color = color_hex.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def interpolate(start: float, end: float, factor: float) -> float:
    return start + (end - start) * factor


def ten_value_to_color(value: float) -> str:
    no_data_color = "#d9d9d9"
    green = hex_to_rgb("#1a9850")
    yellow = hex_to_rgb("#ffffbf")
    red = hex_to_rgb("#d73027")

    if value is None or (isinstance(value, float) and math.isnan(value)):
        return no_data_color

    clamped = max(0.0, min(100.0, float(value)))
    if clamped <= 50:
        factor = clamped / 50.0
        rgb = tuple(int(interpolate(green[i], yellow[i], factor)) for i in range(3))
        return rgb_to_hex(rgb)

    factor = (clamped - 50.0) / 50.0
    rgb = tuple(int(interpolate(yellow[i], red[i], factor)) for i in range(3))
    return rgb_to_hex(rgb)


def main() -> None:
    args = parse_arguments()

    report_files = sorted(
        args.input_dir.glob("*.md"),
        key=lambda path: extract_question_number(path) if extract_question_number(path) is not None else 10_000,
    )

    ten_matrix: List[List[float]] = []
    for report_path in report_files:
        question_number = extract_question_number(report_path)
        if question_number is None:
            continue

        report_text = report_path.read_text(encoding="utf-8")
        ten_by_scenario = extract_ten_table(report_text)
        row_values: List[float] = []

        for model_key, evaluation_group, _display_label in SCENARIOS:
            row_values.append(ten_by_scenario.get((model_key, evaluation_group), math.nan))

        ten_matrix.append(row_values)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_output_path = args.output_dir / args.csv_name
    svg_output_path = args.output_dir / args.svg_name

    csv_columns = [
        f"{display_label}_{evaluation_group}".replace(" ", "").replace("(", "").replace(")", "")
        for _model_key, evaluation_group, display_label in SCENARIOS
    ]

    csv_lines = ["Q," + ",".join(csv_columns)]
    for question_index, row_values in enumerate(ten_matrix, start=1):
        formatted_values = [
            "" if (value is None or (isinstance(value, float) and math.isnan(value))) else f"{value:.2f}"
            for value in row_values
        ]
        csv_lines.append(f"{question_index}," + ",".join(formatted_values))
    csv_output_path.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")

    cell_width = 90
    cell_height = 26
    left_padding = 110
    top_padding = 70
    title_height = 30

    width = left_padding + cell_width * len(SCENARIOS) + 40
    height = top_padding + cell_height * max(len(ten_matrix), 1) + 60

    svg_lines: List[str] = []
    svg_lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
    )
    svg_lines.append('<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>')
    svg_lines.append(
        f'<text x="{width/2:.1f}" y="{title_height}" text-anchor="middle" font-family="Arial" font-size="18" fill="#111111">Figura 4 - Matriz de TEN (%) por pergunta e cenario</text>'
    )

    for column_index, (_model_key, evaluation_group, display_label) in enumerate(SCENARIOS):
        x = left_padding + column_index * cell_width + cell_width / 2
        svg_lines.append(
            f'<text x="{x:.1f}" y="{top_padding-28}" text-anchor="middle" font-family="Arial" font-size="11" fill="#111111">{display_label}</text>'
        )
        svg_lines.append(
            f'<text x="{x:.1f}" y="{top_padding-12}" text-anchor="middle" font-family="Arial" font-size="11" fill="#111111">{evaluation_group}</text>'
        )

    for question_index in range(len(ten_matrix)):
        y = top_padding + question_index * cell_height + cell_height * 0.7
        svg_lines.append(
            f'<text x="{left_padding-10}" y="{y:.1f}" text-anchor="end" font-family="Arial" font-size="11" fill="#111111">Q{question_index+1}</text>'
        )

    for row_index, row_values in enumerate(ten_matrix):
        for column_index, value in enumerate(row_values):
            x = left_padding + column_index * cell_width
            y = top_padding + row_index * cell_height
            fill = ten_value_to_color(value)
            label = "N/A" if (value is None or (isinstance(value, float) and math.isnan(value))) else f"{value:.0f}"

            svg_lines.append(
                f'<rect x="{x}" y="{y}" width="{cell_width}" height="{cell_height}" fill="{fill}" stroke="#ffffff" stroke-width="1"/>'
            )
            svg_lines.append(
                f'<text x="{x + cell_width/2:.1f}" y="{y + cell_height*0.68:.1f}" text-anchor="middle" font-family="Arial" font-size="10" fill="#111111">{label}</text>'
            )

    legend_x = left_padding
    legend_y = top_padding + cell_height * max(len(ten_matrix), 1) + 24
    svg_lines.append(
        f'<text x="{legend_x}" y="{legend_y}" font-family="Arial" font-size="11" fill="#111111">Legenda: 0 (verde) -> 100 (vermelho), N/A (cinza)</text>'
    )
    svg_lines.append("</svg>")

    svg_output_path.write_text("\n".join(svg_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
