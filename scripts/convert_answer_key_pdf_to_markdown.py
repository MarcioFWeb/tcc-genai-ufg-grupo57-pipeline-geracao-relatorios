"""Converte um PDF de gabarito para Markdown estruturado por questao.

Dependencia externa:
- pypdf

Uso recomendado:
python scripts/convert_answer_key_pdf_to_markdown.py \
  --input-pdf instrumento/gabarito.pdf \
  --output-file docs/answer_key_from_pdf.md
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Optional, Tuple

from pypdf import PdfReader


def normalize_line_breaks_and_spaces(text: str) -> str:
    normalized = text.replace("\u00a0", " ")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r" +\n", "\n", normalized)
    normalized = re.sub(r"\n +", "\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    normalized = re.sub(r" ?\u2028 ?", "\n", normalized)
    normalized = re.sub(r"(\d), (\d)", r"\1,\2", normalized)
    normalized = re.sub(r"(\d) %", r"\1%", normalized)
    normalized = normalized.replace(" - ", "-")
    normalized = re.sub(r"\s+([,.;:!?])", r"\1", normalized)
    return normalized.strip()


def collapse_whitespace(text: str) -> str:
    collapsed = text.replace("\u00a0", " ")
    collapsed = re.sub(r"\s+", " ", collapsed)
    collapsed = collapsed.replace(" - ", "-")
    collapsed = re.sub(r"(\d), (\d)", r"\1,\2", collapsed)
    collapsed = re.sub(r"(\d) %", r"\1%", collapsed)
    collapsed = re.sub(r"\s+([,.;:!?])", r"\1", collapsed)
    collapsed = re.sub(r"([A-Za-zÀ-ÿ\)])\.([A-ZÀ-Ý])", r"\1. \2", collapsed)
    collapsed = re.sub(r"(\d)\.([A-ZÀ-Ý])", r"\1. \2", collapsed)
    return collapsed.strip()


def split_question_blocks(pdf_text: str) -> List[str]:
    normalized_text = normalize_line_breaks_and_spaces(pdf_text)
    normalized_text = re.sub(r"\b(Q\d+\s+—)\s*", r"\n\n\1 ", normalized_text)
    chunks = re.split(r"\n\n(?=Q\d+\s+—)", normalized_text)

    blocks: List[str] = []
    for chunk in chunks:
        current = chunk.strip()
        if current.startswith("Q"):
            blocks.append(current)
    return blocks


def parse_question_block(block: str) -> Tuple[Optional[int], str, str, str, str]:
    header_match = re.match(r"^Q(\d+)\s+—\s+(.+?)\n", block)
    if not header_match:
        header_match = re.match(r"^Q(\d+)\s+—\s+(.+)$", block)

    question_number = int(header_match.group(1)) if header_match else None
    title = header_match.group(2).strip() if header_match else ""

    question_text = ""
    question_match = re.search(r"\*\*(.+?)\*\*", block, re.S)
    if question_match:
        question_text = collapse_whitespace(question_match.group(1))

    source_text = ""
    source_match = re.search(r"Fonte:\s*(.+)$", block, re.M)
    if source_match:
        source_text = collapse_whitespace(source_match.group(1))

    content = block
    if question_match:
        content = content[question_match.end() :]
    if source_match:
        content = content[: source_match.start()]
    content = normalize_line_breaks_and_spaces(content)
    content = re.sub(r"^Q\d+\s+—\s+.+?\n", "", content).strip()

    return question_number, title, question_text, content, source_text


def convert_content_to_bullets(content: str) -> List[str]:
    non_empty_lines = [line.strip() for line in content.split("\n") if line.strip()]

    merged_text = " ".join(non_empty_lines)
    merged_text = merged_text.replace("**", "")
    merged_text = re.sub(r"\bFonte:\s*.+$", "", merged_text).strip()
    merged_text = collapse_whitespace(merged_text)

    bullets: List[str] = []
    table_markers = [
        "Setor Saldo",
        "Grupamento Saldo",
        "Região Saldo",
        "Grupamento Salário",
        "Faixa etária Saldo",
        "Grau de instrução Saldo",
        "Mês Saldo",
        "Região / UF Valor",
        "R$ Média",
    ]

    for marker in table_markers:
        if marker in merged_text:
            before_text, after_text = merged_text.split(marker, 1)
            before_text = before_text.strip()
            after_text = after_text.strip()
            if before_text:
                merged_text = before_text
            bullets.append(f"Valores (tabela no PDF): {after_text}")
            break

    for sentence in re.split(r"(?<=[.!?])\s+", merged_text):
        current = sentence.strip()
        if current:
            bullets.append(current)

    if not bullets and merged_text:
        bullets.append(merged_text)

    return bullets


def resolve_default_output_path() -> Path:
    repository_root = Path(__file__).resolve().parent.parent
    return repository_root / "docs" / "answer_key_from_pdf.md"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Converte um PDF de gabarito para Markdown estruturado por pergunta."
    )
    parser.add_argument(
        "--input-pdf",
        type=Path,
        required=True,
        help="Arquivo PDF de entrada com o gabarito.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=resolve_default_output_path(),
        help="Arquivo Markdown de saida.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    pdf_reader = PdfReader(str(args.input_pdf))
    pages_text = [(page.extract_text() or "") for page in pdf_reader.pages]
    full_text = "\n".join(pages_text)

    question_blocks = split_question_blocks(full_text)
    parsed_items: List[Tuple[int, str, str, str, str]] = []

    for block in question_blocks:
        question_number, title, question_text, content, source_text = parse_question_block(block)
        if question_number is None:
            continue
        parsed_items.append((question_number, title, question_text, content, source_text))

    parsed_items.sort(key=lambda item: item[0])

    markdown_parts: List[str] = []
    markdown_parts.append("# Gabarito (PDF) - Versao em Markdown\n")
    markdown_parts.append(
        "Fonte: conversao automatica de PDF para formato editavel em Markdown.\n"
    )
    markdown_parts.append(
        "Observacao: valide manualmente os itens apos a conversao, especialmente em blocos tabulares.\n"
    )
    markdown_parts.append("\n---\n\n")

    for question_number, title, question_text, content, source_text in parsed_items:
        markdown_parts.append(f"## Q{question_number}\n\n")
        if title:
            markdown_parts.append(f"*{collapse_whitespace(title)}*\n\n")

        markdown_parts.append("**Pergunta:**\n\n")
        markdown_parts.append(f"{question_text}\n\n" if question_text else "(pergunta nao identificada)\n\n")

        markdown_parts.append("**Gabarito / dados-chave esperados:**\n\n")
        for bullet in convert_content_to_bullets(content):
            markdown_parts.append(f"- {bullet}\n")

        if source_text:
            markdown_parts.append(f"- Fonte: {source_text}\n")

        markdown_parts.append("\n")

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text("".join(markdown_parts), encoding="utf-8")


if __name__ == "__main__":
    main()
