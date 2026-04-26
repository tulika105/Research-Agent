from groq import Groq
import os
import re
import tempfile
from datetime import datetime
from fpdf import FPDF

SYSTEM_PROMPT = """You are a professional research report writer.
Given raw research findings, produce a structured report with the following sections:

1. **Overview** — 2-3 sentence summary of the topic
2. **Key Findings** — 4-6 bullet points of the most important facts
3. **Background & Context** — 1-2 paragraphs of background
4. **Current Developments** — What's happening now / recent trends
5. **Key Players / Sources** — Notable names, organizations, or URLs mentioned
6. **Summary** — 2-3 sentence conclusion

Use clear headings. Be factual and concise. Do not make up information not present in the research.
"""


def format_report_web(topic: str, raw_research: str) -> str:
    """Format raw research into a clean Markdown report (no Rich formatting)."""
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0,
        stream=False,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Topic: {topic}\n\nRaw Research:\n{raw_research}"}
        ]
    )

    report_body = response.choices[0].message.content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Clean Markdown header without excessive spacing
    header = (
        f"# 📊 Research Report\n"
        f"**Topic:** {topic} &nbsp;|&nbsp; **Generated:** {timestamp}\n"
        f"---\n\n"
    )

    return header + report_body.lstrip()


# Matches a line that is ENTIRELY a bold heading, e.g. **Overview** or **Key Findings**
_BOLD_HEADING_RE = re.compile(r'^\*\*([^*:]+)\*\*$')
# Matches inline **bold** spans
_INLINE_BOLD_RE  = re.compile(r'\*\*(.*?)\*\*')


def save_report_web(topic: str, report: str) -> str:
    """Save report as a PDF in the system temporary directory."""
    clean_topic = re.sub(r'[^a-zA-Z0-9\s]', '', topic).strip().replace(" ", "_")
    if not clean_topic:
        clean_topic = "Research"

    filename = f"{clean_topic}_Research_Report.pdf"
    filepath = os.path.join(tempfile.gettempdir(), filename)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    def safe(text: str) -> str:
        """Drop non-latin-1 characters (emojis, special bullets) then encode."""
        text = re.sub(r'[^\x00-\xFF]', '', text)   # strip chars outside latin-1
        return text.encode("latin-1", errors="replace").decode("latin-1")

    def strip_bold(text: str) -> str:
        return _INLINE_BOLD_RE.sub(r'\1', text)

    # Pre-process: split "**Heading**content" onto separate lines.
    # The LLM sometimes runs the section heading straight into the first bullet
    # e.g. "**Key Findings**-  item one" → "**Key Findings**\n-  item one"
    report = re.sub(r'(\*\*[^*\n]+\*\*)([ \t]*[-*\u2022])', r'\1\n\2', report)

    for line in report.splitlines():
        stripped = line.strip()

        # H1  (# Title)
        if stripped.startswith("# ") and not stripped.startswith("## "):
            pdf.set_font("Helvetica", "B", 20)
            pdf.set_text_color(20, 20, 20)
            pdf.multi_cell(0, 10, safe(stripped[2:].strip()))
            pdf.ln(3)

        # H2  (## Section)
        elif stripped.startswith("## "):
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(40, 40, 120)
            pdf.ln(4)
            pdf.multi_cell(0, 8, safe(stripped[3:].strip()))
            pdf.ln(1)

        # H3  (### Section)
        elif stripped.startswith("### "):
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(80, 80, 80)
            pdf.ln(2)
            pdf.multi_cell(0, 7, safe(stripped[4:].strip()))

        # Horizontal rule (---)
        elif stripped.startswith("---"):
            pdf.set_draw_color(180, 180, 180)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(4)

        # Bullet point (-, *, or unicode •)
        elif stripped.startswith(("- ", "* ")) or stripped.startswith("\u2022 "):
            text = re.sub(r'^[-*\u2022]\s+', '', stripped)
            text = strip_bold(text)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(30, 30, 30)
            pdf.set_x(25)
            pdf.multi_cell(0, 6, safe("-  " + text))   # ascii dash — safe in latin-1
            pdf.ln(1)

        # Standalone bold heading from LLM: **Overview**, **Key Findings** etc.
        elif _BOLD_HEADING_RE.match(stripped):
            heading = _BOLD_HEADING_RE.match(stripped).group(1).strip()
            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(40, 40, 120)
            pdf.ln(5)
            pdf.multi_cell(0, 8, safe(heading))
            pdf.ln(1)

        # Metadata line with mixed bold: **Topic:** ... | **Generated:** ...
        elif stripped.startswith("**"):
            text = strip_bold(stripped)
            text = text.replace("&nbsp;", " ").replace("|", " | ")
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(0, 6, safe(text))
            pdf.ln(1)

        # Empty line
        elif stripped == "":
            pdf.ln(3)

        # Regular paragraph text
        else:
            text = strip_bold(stripped)
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 6, safe(text))
            pdf.ln(1)

    pdf.output(filepath)
    return filepath
