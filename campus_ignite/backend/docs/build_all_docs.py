import os
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

DOCS_DIR = Path("docs")

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def generate_doc(folder_path, filename_base, title, category, sections):
    folder_path.mkdir(parents=True, exist_ok=True)
    docx_path = folder_path / f"{filename_base}.docx"
    md_path = folder_path / f"{filename_base}.md"

    # --- 1. GENERATE DOCX ---
    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)

    # Title
    p_title = doc.add_paragraph()
    r_title = p_title.add_run(title)
    r_title.bold = True
    r_title.font.size = Pt(20)
    r_title.font.color.rgb = RGBColor(26, 60, 110) # Navy #1A3C6E
    p_title.paragraph_format.space_after = Pt(2)

    # Subtitle
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run(f"Campus Ignite Management System — {category}")
    r_sub.font.size = Pt(10.5)
    r_sub.font.color.rgb = RGBColor(200, 169, 81) # Gold #C8A951
    r_sub.bold = True
    p_sub.paragraph_format.space_after = Pt(12)

    # Document Control Metadata Table
    meta_table = doc.add_table(rows=4, cols=2)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Project:", "Campus Ignite (Campus Christian Institution)"),
        ("Document:", title),
        ("Author / Owner:", "Mutsawashe Mwaita (Project Lead & Administrator)"),
        ("Version & Status:", "1.0 — Production Approved & Operational"),
    ]
    for i, (k, v) in enumerate(meta_data):
        row = meta_table.rows[i]
        c0, c1 = row.cells[0], row.cells[1]
        c0.width = Inches(2.0)
        c1.width = Inches(4.5)
        c0.text = k
        c1.text = v
        c0.paragraphs[0].runs[0].bold = True
        c0.paragraphs[0].runs[0].font.size = Pt(9)
        c1.paragraphs[0].runs[0].font.size = Pt(9)
        set_cell_background(c0, "F0F4FA")
        set_cell_background(c1, "FAFCFF")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Section Content
    for sec_title, sec_paragraphs, bullet_items, table_data in sections:
        h = doc.add_heading(level=2)
        r_h = h.add_run(sec_title)
        r_h.font.color.rgb = RGBColor(26, 60, 110)
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(3)

        for p_text in sec_paragraphs:
            p = doc.add_paragraph(p_text)
            p.paragraph_format.space_after = Pt(5)
            p.runs[0].font.size = Pt(9.5)

        for item in bullet_items:
            bp = doc.add_paragraph(item, style='List Bullet')
            bp.paragraph_format.space_after = Pt(2.5)
            bp.runs[0].font.size = Pt(9.5)

        if table_data:
            t_headers, t_rows = table_data
            t = doc.add_table(rows=len(t_rows) + 1, cols=len(t_headers))
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            hdr_cells = t.rows[0].cells
            for idx, text in enumerate(t_headers):
                hdr_cells[idx].text = text
                hdr_cells[idx].paragraphs[0].runs[0].bold = True
                hdr_cells[idx].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
                hdr_cells[idx].paragraphs[0].runs[0].font.size = Pt(9)
                set_cell_background(hdr_cells[idx], "1A3C6E")
            
            for row_idx, row_values in enumerate(t_rows):
                r_cells = t.rows[row_idx + 1].cells
                bg_color = "F7F9FC" if row_idx % 2 == 0 else "FFFFFF"
                for col_idx, val in enumerate(row_values):
                    r_cells[col_idx].text = str(val)
                    r_cells[col_idx].paragraphs[0].runs[0].font.size = Pt(8.5)
                    set_cell_background(r_cells[col_idx], bg_color)
            doc.add_paragraph().paragraph_format.space_after = Pt(8)

    doc.save(str(docx_path))

    # --- 2. GENERATE MARKDOWN COMPANION ---
    md_lines = [
        f"# {title}",
        f"**Campus Ignite Management System — {category}**\n",
        "| Field | Value |",
        "|---|---|",
        "| **Project** | Campus Ignite (Campus Christian Institution) |",
        f"| **Document** | {title} |",
        "| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |",
        "| **Version & Status** | 1.0 — Production Approved & Operational |\n",
    ]

    for sec_title, sec_paragraphs, bullet_items, table_data in sections:
        md_lines.append(f"## {sec_title}\n")
        for p in sec_paragraphs:
            md_lines.append(f"{p}\n")
        if bullet_items:
            for b in bullet_items:
                md_lines.append(f"- {b}")
            md_lines.append("")
        if table_data:
            t_headers, t_rows = table_data
            md_lines.append("| " + " | ".join(t_headers) + " |")
            md_lines.append("| " + " | ".join(["---"] * len(t_headers)) + " |")
            for r in t_rows:
                md_lines.append("| " + " | ".join(str(c) for c in r) + " |")
            md_lines.append("")

    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"Generated: {docx_path.name}")

print("Doc builder helper functions ready.")
