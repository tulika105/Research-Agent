from groq import Groq
import os
import tempfile
from datetime import datetime

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


import re

def save_report_web(topic: str, report: str) -> str:
    """Save report with a clean, readable filename in the system temporary directory."""
    # Create a pretty, safe filename from the topic
    clean_topic = re.sub(r'[^a-zA-Z0-9\s]', '', topic).strip().replace(" ", "_")
    if not clean_topic:
        clean_topic = "Research"
    
    filename = f"{clean_topic}_Research_Report.md"
    filepath = os.path.join(tempfile.gettempdir(), filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)
    
    return filepath
