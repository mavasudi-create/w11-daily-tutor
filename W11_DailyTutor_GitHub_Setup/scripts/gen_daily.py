#!/usr/bin/env python3
"""
W11 Daily Tutor – Täglicher Generator
======================================
Läuft täglich via GitHub Actions.
Ruft die Claude API auf → erhält 2 Anleitungen als JSON →
baut sie in die Word-Vorlage ein → speichert als .docx in output/DATUM/
"""

import os, json, zipfile, re
from datetime import date, datetime
from pathlib import Path
import anthropic

# ── Pfade ────────────────────────────────────────────────────────────────────
ROOT          = Path(__file__).parent.parent
TEMPLATE_PATH = ROOT / "template" / "Vorlage_Fachschaft_Digitalitaet.dotx"
OUTPUT_ROOT   = ROOT / "output"
TOPICS_FILE   = ROOT / "scripts" / "used_topics.json"

# ── Wochenplan (Montag=0 … Sonntag=6) ────────────────────────────────────────
WEEKLY_COMBO = {
    0: ("W11",       "OneDrive"),    # Montag
    1: ("Office365", "Teams"),       # Dienstag
    2: ("W11",       "Edge"),        # Mittwoch
    3: ("Teams",     "OneDrive"),    # Donnerstag
    4: ("Office365", "W11"),         # Freitag
    5: ("Edge",      "Teams"),       # Samstag
    6: ("W11",       "OneDrive"),    # Sonntag
}

# ── System-Prompt (W11 Daily Tutor) ──────────────────────────────────────────
SYSTEM_PROMPT = """Du bist W11 Daily Tutor – Experte für Windows 11, speziell für Lehrer und Schüler.

AUFGABE: Erstelle täglich genau 2 praktische, einsteigerfreundliche Windows 11 Anleitungen.

AUSGABEFORMAT (NUR reines JSON, kein Text davor oder danach):
{
  "anleitungen": [
    {
      "nr": 1,
      "titel": "EMOJI + Titel (max 6 Wörter)",
      "warum": "1 Satz Nutzen",
      "kategorie": "W11 / OneDrive / Teams / Office365 / Edge",
      "dauer": "2 Min / 5 Min / 10 Min",
      "schritte": [
        {
          "nr": 1,
          "aktion": "Imperativ-Satz",
          "erklaerung": "Kurze Erklärung (Klammer wenn nötig)",
          "screenshot_beschreibung": "Was der Screenshot zeigen würde",
          "screenshot_dateiname": "dateiname_ohne_leerzeichen.png"
        }
      ],
      "illust_prompt": "Vollständiger englischer Bild-Prompt für Gemini/KI (flat-design cartoon, Schulstil, Farben #06F4A1 und #F0FC9C, keine Text-Elemente im Bild)",
      "quicktip": "Tastenkürzel ODER schnellster Weg",
      "w11_integration": "Wie dieses Feature mit W11 zusammenspielt",
      "faq_frage": "Typische Anfänger-Frage",
      "faq_antwort": "Kurze klare Antwort",
      "unterricht": "Schüleraufgabe oder Lehrer-Tipp (3 nummerierte Schritte)"
    },
    { "nr": 2, "...": "gleiche Struktur" }
  ]
}

REGELN:
- Kein Thema in 7 Tagen wiederholen
- Max 280 Wörter pro Anleitung
- Deutsch, verständlich für 10-Jährige
- Geduldig, ermutigend – wie ein hilfsbereiter Freund
- Antworte AUSSCHLIESSLICH mit dem JSON-Objekt"""

# ── Claude API aufrufen ───────────────────────────────────────────────────────

def call_claude(cat1: str, cat2: str, used: list[str]) -> dict:
    today = date.today()
    weekday_de = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
    client = anthropic.Anthropic()

    user_msg = (
        f"Heute ist {weekday_de[today.weekday()]}, {today.strftime('%d.%m.%Y')}.\n\n"
        f"Erstelle 2 Windows 11 Anleitungen:\n"
        f"- Anleitung 1: Kategorie \"{cat1}\"\n"
        f"- Anleitung 2: Kategorie \"{cat2}\"\n\n"
        f"Bereits verwendete Themen (letzte 7 Tage, NICHT wiederverwenden):\n"
        f"{', '.join(used) if used else 'Noch keine – freie Themenwahl!'}\n\n"
        "Antworte NUR mit dem JSON-Objekt."
    )

    resp = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=3000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}]
    )
    raw = resp.content[0].text.strip()
    # JSON-Backticks entfernen falls vorhanden
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)

# ── Topic-Tracking ────────────────────────────────────────────────────────────

def load_used_topics() -> dict:
    if TOPICS_FILE.exists():
        return json.loads(TOPICS_FILE.read_text())
    return {}

def save_used_topics(topics: dict):
    TOPICS_FILE.write_text(json.dumps(topics, ensure_ascii=False, indent=2))

def get_recent_titles(topics: dict) -> list[str]:
    """Titel der letzten 7 Tage"""
    cutoff = date.today().toordinal() - 7
    result = []
    for day_str, titles in topics.items():
        if date.fromisoformat(day_str).toordinal() >= cutoff:
            result.extend(titles)
    return result

# ── Word-Dokument aus Vorlage bauen ──────────────────────────────────────────

TG  = "06F4A1"
JQ  = "F0FC9C"
TGD = "04C984"
BK  = "333333"

NS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'
      '<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
      'xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" '
      'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
      'xmlns:o="urn:schemas-microsoft-com:office:office" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
      'xmlns:v="urn:schemas-microsoft-com:vml" '
      'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
      'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
      'xmlns:w10="urn:schemas-microsoft-com:office:word" '
      'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
      'xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" '
      'xmlns:w16="http://schemas.microsoft.com/office/word/2018/wordml" '
      'xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex" '
      'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
      'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
      'mc:Ignorable="w14 w15 w16se w16 wp14">')

SECT_PR = """<w:sectPr>
  <w:headerReference w:type="even" r:id="rId11"/>
  <w:headerReference w:type="default" r:id="rId12"/>
  <w:footerReference w:type="even" r:id="rId13"/>
  <w:footerReference w:type="default" r:id="rId14"/>
  <w:headerReference w:type="first" r:id="rId15"/>
  <w:footerReference w:type="first" r:id="rId16"/>
  <w:pgSz w:w="11906" w:h="16838"/>
  <w:pgMar w:top="1719" w:right="1701" w:bottom="1015" w:left="1701" w:header="567" w:footer="567" w:gutter="0"/>
  <w:pgNumType w:start="1" w:chapStyle="1"/>
  <w:cols w:space="708"/>
  <w:titlePg/>
  <w:docGrid w:linePitch="360"/>
</w:sectPr>"""

CW = 7504  # Content-Breite in DXA

def esc(t):
    return (str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                  .replace('"',"&quot;"))

def rpr(sz=22, bold=False, color=None, italic=False):
    r = f'<w:rFonts w:ascii="Aptos" w:hAnsi="Aptos" w:cs="Aptos"/><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/>'
    if bold:   r = "<w:b/><w:bCs/>" + r
    if italic: r += "<w:i/>"
    if color:  r += f'<w:color w:val="{color}"/>'
    return f"<w:rPr>{r}</w:rPr>"

def run(text, sz=22, bold=False, color=None, italic=False):
    return f'<w:r>{rpr(sz,bold,color,italic)}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'

def para(content="", align="left", sb=0, sa=120, bb=False, ind=0, fill=None):
    ppr = []
    if sb or sa:  ppr.append(f'<w:spacing w:before="{sb}" w:after="{sa}"/>')
    if align != "left": ppr.append(f'<w:jc w:val="{align}"/>')
    if ind:       ppr.append(f'<w:ind w:left="{ind}" w:hanging="360"/>')
    if bb:        ppr.append(f'<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="1" w:color="{TG}"/></w:pBdr>')
    if fill:      ppr.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>')
    ppr_xml = ("<w:pPr>" + "".join(ppr) + "</w:pPr>") if ppr else ""
    return f"<w:p>{ppr_xml}{content}</w:p>"

def sp(n=120): return para(sa=n)
def hr():      return para(bb=True, sb=140, sa=140)

def tbl(paras, fill, left_bar=False, dashed=False, outline=False):
    bdr_xml = {
        "none":  f'<w:tcBorders></w:tcBorders>',
        "left":  f'<w:tcBorders><w:left w:val="thick" w:sz="24" w:space="0" w:color="{TG}"/></w:tcBorders>',
        "dash":  f'<w:tcBorders><w:top w:val="dashSmallGap" w:sz="8" w:space="0" w:color="AAAAAA"/><w:left w:val="dashSmallGap" w:sz="8" w:space="0" w:color="AAAAAA"/><w:bottom w:val="dashSmallGap" w:sz="8" w:space="0" w:color="AAAAAA"/><w:right w:val="dashSmallGap" w:sz="8" w:space="0" w:color="AAAAAA"/></w:tcBorders>',
        "outline":f'<w:tcBorders><w:top w:val="single" w:sz="10" w:space="0" w:color="{TG}"/><w:left w:val="single" w:sz="10" w:space="0" w:color="{TG}"/><w:bottom w:val="single" w:sz="10" w:space="0" w:color="{TG}"/><w:right w:val="single" w:sz="10" w:space="0" w:color="{TG}"/></w:tcBorders>',
    }
    bk = "left" if left_bar else "dash" if dashed else "outline" if outline else "none"
    tcPr = (f'<w:tcPr><w:tcW w:w="{CW}" w:type="dxa"/>{bdr_xml[bk]}'
            f'<w:shd w:val="clear" w:color="auto" w:fill="{fill}"/>'
            f'<w:tcMar><w:top w:w="100" w:type="dxa"/><w:left w:w="180" w:type="dxa"/>'
            f'<w:bottom w:w="100" w:type="dxa"/><w:right w:w="180" w:type="dxa"/></w:tcMar></w:tcPr>')
    tblPr = f'<w:tblPr><w:tblW w:w="{CW}" w:type="dxa"/></w:tblPr>'
    grid  = f'<w:tblGrid><w:gridCol w:w="{CW}"/></w:tblGrid>'
    cell  = f'<w:tc>{tcPr}{"".join(paras)}</w:tc>'
    return f'<w:tbl>{tblPr}{grid}<w:tr>{cell}</w:tr></w:tbl>'

def banner(nr, titel, subtitle):
    return tbl([
        para(run(f"ANLEITUNG {nr}", 18, bold=True, color=TGD), sb=60, sa=40),
        para(run(titel, 40, bold=True, color=TG), sa=60),
        para(run(subtitle, 20, color="888888", italic=True), sa=60),
    ], fill="FFFFFF", left_bar=True)

def why_box(text):
    return tbl([para(run("💡 Warum wichtig?   ", 22, bold=True, color=BK) +
                     run(text, 22, color="444444"))],
               fill=JQ, left_bar=True)

def step_head(text):
    return para(run(text, 28, bold=True, color=TG), sb=200, sa=80)

def illust_box(prompt):
    return tbl([
        para(run("🎨  Illustration — ", 22, bold=True, color=TGD) +
             run("Prompt für Gemini / Bild-KI:", 20, bold=True, color="444444"), sa=80),
        para(run(prompt, 20, color="1A1A1A"), sa=0)
    ], fill="EDFFF8", outline=True)

def ss_box(desc, filename):
    return tbl([
        para(run("📷  PLATZHALTER: Echter Screenshot", 22, bold=True, color=BK),
             align="center", sa=80),
        para(run("Beschreibung: ", 20, bold=True, color="555555") +
             run(desc, 20, color="555555"), sa=40),
        para(run("Dateiname: ", 18, bold=True, color="888888") +
             run(filename, 18, italic=True, color="888888"), sa=0),
    ], fill=JQ, dashed=True)

def info_box(label, lines):
    return tbl(
        [para(run(label, 23, bold=True, color="222222"), sa=80)] +
        [para(run(l, 21, color="444444"), sa=60) for l in lines],
        fill=JQ, left_bar=True)

def num_list(items):
    return [para(run(f"{i+1}.  ", 22, bold=True, color=TGD) + run(t, 22, color=BK),
                 ind=360, sa=60)
            for i, t in enumerate(items)]

def footer_bar(tag):
    return tbl([para(run("🪟 W11 Daily Tutor  |  ", 18, color="888888") +
                     run(tag, 18, bold=True, color=TGD) +
                     run("  |  Für Schüler & Lehrer", 18, color="888888"),
                     align="center")],
               fill="F8F8F8")

# ── Anleitung → XML-Parts ─────────────────────────────────────────────────────

def anleitung_to_xml(a: dict, datum_str: str) -> list[str]:
    parts = []
    subtitle = (f"Tag {datum_str}  |  {a['kategorie']}  "
                f"|  {a['dauer']}")
    parts.append(banner(a["nr"], a["titel"], subtitle))
    parts.append(sp(80))
    parts.append(why_box(a["warum"]))
    parts.append(sp(40))
    parts.append(hr())

    for s in a["schritte"]:
        parts.append(step_head(f"SCHRITT {s['nr']}: {s['aktion']}"))
        parts.append(para(run(s["erklaerung"], 22, color=BK), sa=80))
        parts.append(illust_box(a.get("illust_prompt", "Illustration für diesen Schritt")))
        parts.append(sp(80))
        parts.append(ss_box(s["screenshot_beschreibung"], s["screenshot_dateiname"]))
        parts.append(sp(80))

    parts.append(hr())
    parts.append(info_box("🎯 QUICK TIP:", [a["quicktip"]]))
    parts.append(sp(80))
    parts.append(info_box("💡 W11-INTEGRATION:", [a["w11_integration"]]))
    parts.append(sp(80))
    parts.append(info_box("❓ HÄUFIGE FRAGEN:", [
        f"F: {a['faq_frage']}", f"A: {a['faq_antwort']}"
    ]))
    parts.append(sp(80))
    parts.append(info_box("🎓 FÜR DEN UNTERRICHT:", [a["unterricht"]]))
    parts.append(sp(120))
    parts.append(footer_bar(f"{a['kategorie']}  |  {datum_str}"))
    return parts

# ── .docx aus Vorlage bauen ───────────────────────────────────────────────────

def build_docx(content_parts: list[str], out_path: Path):
    body_xml = "".join(content_parts)
    new_doc  = f"{NS}<w:body>{body_xml}{SECT_PR}</w:body></w:document>"
    with zipfile.ZipFile(TEMPLATE_PATH, "r") as zin:
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = new_doc.encode("utf-8") if item.filename == "word/document.xml" \
                       else zin.read(item.filename)
                zout.writestr(item, data)
    print(f"  ✅ {out_path.name}  ({out_path.stat().st_size // 1024} KB)")

# ── Hauptprogramm ─────────────────────────────────────────────────────────────

def main():
    today      = date.today()
    today_str  = today.isoformat()          # 2026-05-02
    datum_disp = today.strftime("%d.%m.%Y") # 02.05.2026
    cat1, cat2 = WEEKLY_COMBO[today.weekday()]

    print(f"\n🪟 W11 Daily Tutor – {datum_disp}")
    print(f"   Kategorien heute: {cat1} + {cat2}")

    # Themen-Tracking laden
    all_topics  = load_used_topics()
    recent      = get_recent_titles(all_topics)
    print(f"   Bereits verwendete Themen (7 Tage): {len(recent)}")

    # Claude API aufrufen
    print("   🤖 Claude API wird aufgerufen …")
    data = call_claude(cat1, cat2, recent)

    anleitungen = data["anleitungen"]
    print(f"   📝 Erhalten: {len(anleitungen)} Anleitungen")

    # Output-Ordner erstellen
    out_dir = OUTPUT_ROOT / datum_disp.replace(".", "-")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Beide .docx erstellen
    print("   📄 Dokumente werden gebaut …")
    for a in anleitungen:
        titel_safe = re.sub(r'[^\w\-]', '_', a["titel"])[:50]
        filename   = f"W11_{datum_disp}_Anleitung{a['nr']}_{titel_safe}.docx"
        out_path   = out_dir / filename
        parts      = anleitung_to_xml(a, datum_disp)
        build_docx(parts, out_path)

    # Themen speichern (für 7-Tage-Tracking)
    all_topics[today_str] = [a["titel"] for a in anleitungen]
    save_used_topics(all_topics)

    # Ältere Einträge (>14 Tage) löschen
    cutoff = today.toordinal() - 14
    pruned = {k: v for k, v in all_topics.items()
              if date.fromisoformat(k).toordinal() >= cutoff}
    save_used_topics(pruned)

    print(f"\n✅ Fertig! Dateien in: output/{out_dir.name}/")
    for f in sorted(out_dir.glob("*.docx")):
        print(f"   📄 {f.name}")

if __name__ == "__main__":
    main()
