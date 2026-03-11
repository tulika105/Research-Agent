# 🔍 Research Agent

A ReAct (Reasoning + Action) agent that autonomously searches the web and synthesizes findings into a structured research report — all from the CLI.

You type a topic. The agent thinks, searches, observes, and repeats — streaming each search query live to the terminal as it reasons. Once done, it hands off to a second LLM that formats everything into a clean report.

---

## Demo

```
Enter a research topic: LangChain

📡 Researching: 'LangChain'
(ReAct agent is thinking... watch the steps below)

🔎 Search 1: LangChain overview
🔎 Search 2: LangChain recent developments 2026
🔎 Search 3: LangChain technical architecture how it works
🔎 Search 4: LangChain real world applications use cases
🔎 Search 5: LangChain limitations and challenges
🧠 Agent: done researching, compiling results...

📝 Formatting structured report...

============================================================
  RESEARCH REPORT
  Topic  : LangChain
  Generated: 2026-03-11 18:06
============================================================

## Overview
LangChain is an open-source framework that simplifies the creation of
applications using large language models (LLMs)...

## Key Findings
- LangChain provides a standard interface for LLM calls, prompt templates,
  chains, agents, and tool-integration
- ...

💾 Save report to file? (y/n): y
✅ Saved to: examples/langchain_report.txt
```

---

## How It Works

The agent follows the **ReAct loop** — Reasoning and Action in alternating steps:

```
User Input: "Vector Databases"
        │
        ▼
🧠 THINK → "Start with a broad overview"
⚡ ACT   → duckduckgo_search("Vector Databases overview")
👁️ OBSERVE → 5 results returned

🧠 THINK → "Got overview, missing recent developments"
⚡ ACT   → duckduckgo_search("Vector Databases recent developments 2024")
👁️ OBSERVE → 5 results returned

🧠 THINK → "Need technical depth — how does HNSW indexing work?"
⚡ ACT   → duckduckgo_search("Vector Databases HNSW indexing technical")
👁️ OBSERVE → 5 results returned

... continues until all angles are covered ...

🧠 THINK → "I have enough coverage. Stopping."
        │
        ▼
  report.py formats raw research
        │
        ▼
  Structured report printed to CLI
```

Each THINK step asks *"what am I still missing?"* — the agent searches the topic in depth from different angles (overview → recent news → technical details → use cases → limitations).

---

## Architecture

```
research-agent/
├── main.py       # CLI entry point + streaming loop
├── agent.py      # ReAct agent (LangGraph + Groq)
├── tools.py      # DuckDuckGo search tool (@tool decorator)
├── report.py     # Report formatter 
├── examples/     # Sample reports saved here in txt
├── requirements.txt  # Python dependencies
```

### Two-Model Design

| Component | Model | Role |
|---|---|---|
| `agent.py` | `gpt-oss-20b` | Reasoning — decides what to search, detects gaps |
| `report.py` | `llama-3.3-70b-versatile` | Writing — formats raw research into structured report |

The agent gathers first, the formatter writes second. Separating these two jobs produces significantly better reports than combining them in a single prompt.

### Report Structure

Every report follows the same 6-section format:

1. **Overview** — 2-3 sentence summary
2. **Key Findings** — 4-6 bullet points of top facts
3. **Background & Context** — history and depth
4. **Current Developments** — what's happening now
5. **Key Players / Sources** — notable names and references
6. **Summary** — conclusion

---

## Stack

| Tool | Purpose |
|---|---|
| `langgraph.prebuilt.create_react_agent` | ReAct agent loop |
| `langchain-groq` | LLM integration for agent |
| `groq` Python SDK | Direct API call for report formatting |
| `DuckDuckGoSearchResults` | Web search tool (no API key needed) |
| `@tool` decorator | LangChain tool definition |

---

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/tulika105/Research-Agent
cd research-report-agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your Groq API key in .env
# 5. Run the File
python main.py
```
