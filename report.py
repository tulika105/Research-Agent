from groq import Groq
import os
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
    header = f"""
{'='*60}
  RESEARCH REPORT
  Topic  : {topic}
  Generated: {timestamp}
{'='*60}
"""
    return header + "\n" + report_body + "\n" + "="*60


def save_report(topic: str, report: str):
    os.makedirs("examples", exist_ok=True)
    filename = os.path.join("examples", topic.lower().replace(" ", "_")[:40] + "_report.txt")
    with open(filename, "w") as f:
        f.write(report)
    return filename