#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert the two import-filing supporting documents to PDF."""

from pathlib import Path
from fontTools.ttLib import TTCollection
from fpdf import FPDF

# Extract STHeiti Medium from TTC to a usable TTF
FONT_SRC = Path("/System/Library/Fonts/STHeiti Medium.ttc")
FONT_DIR = Path("/Users/johnzhuang/以鲜国际/.fonts")
FONT_DIR.mkdir(parents=True, exist_ok=True)
FONT_TTF = FONT_DIR / "STHeitiMedium.ttf"

if not FONT_TTF.exists():
    ttc = TTCollection(str(FONT_SRC))
    ttc[0].save(str(FONT_TTF))


class PDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("STHeiti", "", 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"第 {self.page_no()} 页", align="C")


def render_table(pdf, rows):
    if not rows:
        return
    # Filter out separator rows
    data = []
    for row in rows:
        cells = [c.strip() for c in row.strip("|").split("|")]
        if cells and not all(set(c) <= set("-| ") for c in cells):
            data.append(cells)
    if not data:
        return

    cols = len(data[0])
    page_width = pdf.w - 2 * pdf.l_margin
    col_width = page_width / cols

    pdf.set_font("STHeiti", "", 9)
    for cells in data:
        y = pdf.get_y()
        x = pdf.l_margin
        heights = []
        for i, cell in enumerate(cells):
            pdf.set_xy(x + i * col_width, y)
            pdf.multi_cell(col_width, 6, cell, border=1, align="L")
            heights.append(pdf.get_y() - y)
        pdf.set_y(y + max(heights))
    pdf.ln(3)


def md_to_pdf(md_path: Path, pdf_path: Path):
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    pdf = PDF()
    pdf.add_font("STHeiti", "", str(FONT_TTF))
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    table_buffer = []

    for line in lines:
        stripped = line.strip()

        # Title (H1)
        if stripped.startswith("# "):
            if table_buffer:
                render_table(pdf, table_buffer)
                table_buffer = []
            pdf.set_font("STHeiti", "", 18)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 14, stripped[2:], align="C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            continue

        # Section headings (H2)
        if stripped.startswith("## "):
            if table_buffer:
                render_table(pdf, table_buffer)
                table_buffer = []
            pdf.set_font("STHeiti", "", 13)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 10, stripped[3:], new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
            continue

        # Table rows
        if stripped.startswith("|"):
            table_buffer.append(stripped)
            continue
        elif table_buffer:
            render_table(pdf, table_buffer)
            table_buffer = []

        # Horizontal rule / signature block
        if stripped.startswith("---"):
            pdf.ln(2)
            continue

        # Bold emphasis
        if stripped.startswith("**") and stripped.endswith("**"):
            pdf.set_font("STHeiti", "", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 8, stripped.strip("*"))
            continue

        # Regular paragraph
        if stripped:
            pdf.set_font("STHeiti", "", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 8, stripped)
        else:
            pdf.ln(2)

    if table_buffer:
        render_table(pdf, table_buffer)

    pdf.output(str(pdf_path))


if __name__ == "__main__":
    base = Path("/Users/johnzhuang/以鲜国际")
    documents = [
        ("以鲜国际_拟经营食品种类及存放地点说明.md", "以鲜国际_拟经营食品种类及存放地点说明.pdf"),
        ("以鲜国际_无食品进口经历声明.md", "以鲜国际_无食品进口经历声明.pdf"),
    ]
    for md_name, pdf_name in documents:
        md_path = base / md_name
        pdf_path = base / pdf_name
        md_to_pdf(md_path, pdf_path)
        print(f"Generated: {pdf_path}")
