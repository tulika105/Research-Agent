from groq import Groq
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from io import StringIO

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

def format_report(topic: str, raw_research: str) -> str:
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
    
    # Create a Rich Panel for the header and render it to string
    buffer = StringIO()
    render_console = Console(file=buffer, force_terminal=True, width=80)
    
    header_panel = Panel(
        f"[bold bright_cyan]📊 RESEARCH REPORT[/bold bright_cyan]\n[bright_black]Topic: {topic}\nGenerated: {timestamp}[/bright_black]",
        style="blue",
        expand=False,
        border_style="bold cyan"
    )
    
    render_console.print(header_panel)
    header_output = buffer.getvalue()
    
    # Combine header and report body
    return header_output + "\n" + report_body


def save_report(topic: str, report: str):
    os.makedirs("examples", exist_ok=True)
    filename = os.path.join("examples", topic.lower().replace(" ", "_")[:40] + "_report.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)
    return filename