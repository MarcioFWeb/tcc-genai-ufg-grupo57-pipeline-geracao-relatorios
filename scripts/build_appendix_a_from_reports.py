"""Gera um apendice com perguntas e gabarito a partir dos relatorios por questao.

Uso recomendado:
python scripts/build_appendix_a_from_reports.py \
  --input-dir resultados \
  --output-file docs/appendix_a_questions_and_answer_key.md
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Optional


def extract_question_number(file_path: Path) -> Optional[int]:
    match = re.search(r"(\d+)\.md$", file_path.name)
    return int(match.group(1)) if match else None


def extract_question_text(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    for index, line in enumerate(lines):
        if re.match(r"^##\s*PERGUNTA AVALIADA\s*$", line.strip(), re.I):
            for candidate_index in range(index + 1, len(lines)):
                if lines[candidate_index].strip():
                    return lines[candidate_index].strip()
        if line.strip().startswith("##"):
            return line.strip().lstrip("#").strip()
    return ""


def extract_answer_key_bullets(markdown_text: str) -> List[str]:
    start_match = re.search(r"^###\s*Verificacao do Gabarito\s*$", markdown_text, re.M | re.I)
    if not start_match:
        return []

    tail = markdown_text[start_match.end() :]
    end_match = re.search(r"^###\s*Metricas de Erro\s*$", tail, re.M | re.I)
    section = tail[: end_match.start()] if end_match else tail

    bullets: List[str] = []
    for line in section.splitlines():
        if line.strip().startswith("-"):
            bullets.append(line.rstrip())
    return bullets


def resolve_default_paths() -> tuple[Path, Path]:
    repository_root = Path(__file__).resolve().parent.parent
    default_input_dir = repository_root / "resultados"
    default_output_file = repository_root / "docs" / "appendix_a_questions_and_answer_key.md"
    return default_input_dir, default_output_file


def parse_arguments() -> argparse.Namespace:
    default_input_dir, default_output_file = resolve_default_paths()
    parser = argparse.ArgumentParser(
        description="Consolida perguntas e blocos de gabarito em um unico arquivo Markdown."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=default_input_dir,
        help="Diretorio com relatorios por questao (padrao: resultados/).",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=default_output_file,
        help="Arquivo Markdown de saida para o apendice consolidado.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    report_files = sorted(
        args.input_dir.glob("*.md"),
        key=lambda path: extract_question_number(path) if extract_question_number(path) is not None else 10_000,
    )

    markdown_parts: List[str] = []
    markdown_parts.append("# APENDICE A - Conjunto completo de questoes e gabarito\n")
    markdown_parts.append(
        "Fonte: consolidacao automatica dos blocos 'Verificacao do Gabarito' dos relatorios por questao.\n"
    )
    markdown_parts.append(
        "Observacao: revise manualmente os itens para garantir aderencia ao instrumento original em mudancas de formato.\n"
    )
    markdown_parts.append("\n---\n\n")

    for report_path in report_files:
        question_number = extract_question_number(report_path)
        if question_number is None:
            continue

        report_text = report_path.read_text(encoding="utf-8")
        question_text = extract_question_text(report_text)
        answer_key_bullets = extract_answer_key_bullets(report_text)

        markdown_parts.append(f"## Q{question_number}\n\n")
        markdown_parts.append("**Pergunta:**\n\n")
        markdown_parts.append(f"{question_text or '(pergunta nao identificada)'}\n\n")
        markdown_parts.append("**Gabarito / dados-chave esperados:**\n\n")

        if answer_key_bullets:
            for bullet in answer_key_bullets:
                markdown_parts.append(f"{bullet}\n")
        else:
            markdown_parts.append("- (bloco de gabarito nao encontrado no arquivo de origem)\n")

        markdown_parts.append("\n")

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text("".join(markdown_parts), encoding="utf-8")


if __name__ == "__main__":
    main()

