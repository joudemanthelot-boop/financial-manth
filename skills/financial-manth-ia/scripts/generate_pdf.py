#!/usr/bin/env python3
"""Financial Manth IA - Génération du livrable PDF d'analyse financière.

Usage:
    pip install fpdf2
    python generate_pdf.py analyse.json rapport.pdf

Schéma JSON attendu (les champs absents sont omis ; jamais de 0 pour une donnée manquante):
{
  "entreprise": {"nom": str, "secteur": str, "activite": str},
  "exercices": [
    {
      "libelle": "N",
      "periode": "01/01/2024 - 31/12/2024",
      "indicateurs": {"Chiffre d'affaires": 250000},
      "equilibre": {"FRNG": 40000, "BFR": 35000, "Trésorerie nette": 5000},
      "ratios": {"Autonomie financière (%)": 42.5}
    }
  ],
  "comparaison": [{"Indicateur": "CA", "N": 250000, "N-1": 230000, "Variation €": 20000, "Variation %": 8.7}],
  "controles": [{"type": "Équilibre du bilan", "message": "...", "gravite": "info|attention"}],
  "diagnostic": {"Points forts": [], "Points faibles": [], "Risques / points de vigilance": [], "Pistes d'action": []},
  "sources": [{"poste": str, "libelle_origine": str, "provenance": str, "valeur": str, "correction": str, "statut": str}]
}
"""
import glob
import json
import sys
from datetime import date

try:
    from fpdf import FPDF
except ImportError:
    sys.exit("Dépendance manquante : exécutez 'pip install fpdf2'.")


NA = "N/D"
FONT = "helvetica"
WARNING = ("Document généré par Financial Manth IA à titre d'aide à l'analyse et à la décision. "
           "Il ne constitue ni une certification comptable, ni un conseil professionnel, "
           "juridique ou fiscal, et ne remplace ni un expert-comptable ni un commissaire aux comptes.")


def setup_fonts(pdf):
    global FONT
    """Police Unicode si disponible (symbole € requis), sinon helvetica + cp1252."""
    regular = None
    for pattern in [
        "/usr/share/fonts/**/DejaVuSans.ttf",
        "/usr/share/fonts/**/DejaVuSansBook.ttf",
        "/usr/local/share/fonts/**/DejaVuSans.ttf",
        "/Library/Fonts/DejaVuSans.ttf",
    ]:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            regular = matches[0]
            break
    if regular:
        bold = regular.replace("DejaVuSans.ttf", "DejaVuSans-Bold.ttf")
        import os
        pdf.add_font("DejaVu", "", regular)
        pdf.add_font("DejaVu", "B", bold if os.path.exists(bold) else regular)
        FONT = "DejaVu"
        return FONT
    pdf.core_fonts_encoding = "windows-1252"
    FONT = "helvetica"
    return FONT


class RapportPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font(FONT, "I", 8)
            self.set_text_color(110)
            self.cell(0, 6, "Financial Manth IA - Rapport d'analyse financière", align="L")
            self.ln(6)
            self.set_draw_color(200)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font(FONT, "I", 8)
        self.set_text_color(110)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def section_title(pdf, title):
    pdf.ln(2)
    pdf.set_font(FONT, "B", 13)
    pdf.set_text_color(20, 60, 120)
    pdf.cell(0, 8, title, align="L")
    pdf.ln(2)
    pdf.set_draw_color(20, 60, 120)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)


def kv_table(pdf, data, w1=95, w2=95):
    for k, v in data.items():
        pdf.set_font(FONT, "", 10)
        pdf.set_fill_color(240, 244, 250)
        pdf.cell(w1, 7, str(k), border=1, fill=True)
        pdf.set_font(FONT, "B", 10)
        pdf.cell(w2, 7, NA if v is None else str(v), border=1)
        pdf.ln()


def bullets(pdf, items):
    pdf.set_font(FONT, "", 10)
    if not items:
        pdf.cell(0, 6, "Aucun élément.")
        pdf.ln()
        return
    for item in items:
        pdf.multi_cell(0, 6, f"- {item}", new_x="LMARGIN", new_y="NEXT")


def simple_table(pdf, headers, rows, widths=None):
    if widths is None:
        widths = [190 / len(headers)] * len(headers)
    pdf.set_font(FONT, "B", 9)
    pdf.set_fill_color(20, 60, 120)
    pdf.set_text_color(255)
    for h, w in zip(headers, widths):
        pdf.cell(w, 7, h, border=1, fill=True, align="C")
    pdf.ln()
    pdf.set_text_color(0)
    pdf.set_font(FONT, "", 9)
    for i, row in enumerate(rows):
        pdf.set_fill_color(240, 244, 250) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
        for v, w in zip(row, widths):
            pdf.cell(w, 6, NA if v is None else str(v), border=1, fill=True)
        pdf.ln()


def build(data, out_path):
    pdf = RapportPDF(orientation="P", unit="mm", format="A4")
    setup_fonts(pdf)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=18)

    pdf.add_page()
    pdf.ln(40)
    pdf.set_font(FONT, "B", 24)
    pdf.set_text_color(20, 60, 120)
    pdf.cell(0, 12, "Financial Manth IA", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT, "", 15)
    pdf.set_text_color(0)
    pdf.cell(0, 10, "Rapport d'analyse financière", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    ent = data.get("entreprise", {})
    pdf.set_font(FONT, "B", 13)
    pdf.cell(0, 8, ent.get("nom", "Entreprise non renseignée"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font(FONT, "", 11)
    pdf.cell(0, 7, f"Secteur : {ent.get('secteur', NA)}   |   Activité : {ent.get('activite', NA)}",
             align="C", new_x="LMARGIN", new_y="NEXT")
    exos = [e.get("libelle", "?") for e in data.get("exercices", [])]
    pdf.cell(0, 7, "Exercices analysés : " + (", ".join(exos) if exos else NA),
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Rapport généré le {date.today().strftime('%d/%m/%Y')}",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(12)
    pdf.set_font(FONT, "I", 9)
    pdf.set_text_color(110)
    pdf.multi_cell(0, 5, "Avertissement : " + WARNING, new_x="LMARGIN", new_y="NEXT")

    pdf.add_page()
    section_title(pdf, "1. Données sources validées")
    src = data.get("sources", [])
    if src:
        rows = [[s.get("poste", NA), s.get("libelle_origine", NA), s.get("provenance", NA),
                 s.get("valeur", NA), s.get("correction", NA) or "-", s.get("statut", NA)] for s in src]
        simple_table(pdf, ["Poste financier", "Libellé d'origine", "Provenance", "Valeur", "Correction", "Statut"],
                     rows, widths=[38, 42, 34, 24, 26, 26])
    else:
        pdf.set_font(FONT, "", 10)
        pdf.cell(0, 6, "Aucune donnée source renseignée.")
        pdf.ln()

    for exo in data.get("exercices", []):
        pdf.add_page()
        section_title(pdf, f"Exercice {exo.get('libelle', '?')} ({exo.get('periode', 'période N/D')})")
        pdf.set_font(FONT, "B", 11)
        pdf.cell(0, 7, "Activité et performance")
        pdf.ln()
        kv_table(pdf, exo.get("indicateurs", {}))
        pdf.ln(2)
        pdf.set_font(FONT, "B", 11)
        pdf.cell(0, 7, "Équilibre financier")
        pdf.ln()
        kv_table(pdf, exo.get("equilibre", {}))
        pdf.ln(2)
        pdf.set_font(FONT, "B", 11)
        pdf.cell(0, 7, "Ratios")
        pdf.ln()
        kv_table(pdf, exo.get("ratios", {}))

    comp = data.get("comparaison", [])
    if comp:
        pdf.add_page()
        section_title(pdf, "Comparaison pluriannuelle")
        headers = list(comp[0].keys())
        rows = [[c.get(h, NA) for h in headers] for c in comp]
        simple_table(pdf, headers, rows, widths=[190 / len(headers)] * len(headers))

    pdf.add_page()
    section_title(pdf, "Diagnostic")
    diag = data.get("diagnostic", {})
    for cat in ["Points forts", "Points faibles", "Risques / points de vigilance", "Pistes d'action"]:
        pdf.set_font(FONT, "B", 11)
        pdf.cell(0, 7, cat)
        pdf.ln()
        bullets(pdf, diag.get(cat, []))
        pdf.ln(2)

    section_title(pdf, "Contrôles et anomalies")
    ctrl = data.get("controles", [])
    if ctrl:
        rows = [[c.get("type", NA), c.get("message", NA), c.get("gravite", NA)] for c in ctrl]
        simple_table(pdf, ["Contrôle", "Message", "Gravité"], rows, widths=[45, 115, 30])
    else:
        pdf.set_font(FONT, "", 10)
        pdf.cell(0, 6, "Aucune anomalie signalée.")
        pdf.ln()

    section_title(pdf, "Méthodologie et limites")
    bullets(pdf, [
        "Les indicateurs sont calculés par un moteur déterministe ; la formule et les données sources sont documentées.",
        "Les données manquantes sont marquées « N/D » et ne sont jamais assimilées à zéro.",
        "Les retraitements éventuels (bilan comptable vers bilan fonctionnel) sont documentés dans les données sources.",
        "Les périodes de durées différentes ne sont comparées qu'après retraitement explicite.",
        "Ce rapport ne tient pas lieu de certification : voir l'avertissement en page de titre.",
    ])

    pdf.output(out_path)
    print(f"PDF généré : {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage : python generate_pdf.py analyse.json rapport.pdf")
    with open(sys.argv[1], encoding="utf-8") as fh:
        build(json.load(fh), sys.argv[2])
