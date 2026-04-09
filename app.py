import streamlit as st
import os
import sys
from dotenv import load_dotenv
from agent import build_agent
from report import format_report, save_report
import re

load_dotenv()

def check_env():
    api_key = os.environ.get("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("❌ GROQ_API_KEY not found. Add it to your .env file or Streamlit secrets.")
        st.stop()
    os.environ["GROQ_API_KEY"] = api_key

def clean_markdown(text):
    # Remove bold **text**
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove italic *text*
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # Remove headers ##
    text = re.sub(r'^##\s*', '', text, flags=re.MULTILINE)
    # Remove bullet points * to -
    text = re.sub(r'^\*\s*', '- ', text, flags=re.MULTILINE)
    return text

st.title("🔍 Research Agent — powered by Groq + DuckDuckGo")

check_env()

topic = st.text_input("Enter a research topic:", "")

if st.button("Start Research") and topic:
    with st.spinner("Researching..."):
        progress_placeholder = st.empty()
        searches = []

        # Step 1: Stream ReAct agent
        agent = build_agent()
        raw_research = ""
        iteration = 1

        for chunk in agent.stream(
            {"messages": [{"role": "user", "content": f"Research this topic thoroughly and gather as much factual information as possible: {topic}"}]}
        ):
            if "agent" in chunk:
                agent_msg = chunk["agent"]["messages"][0]
                if agent_msg.tool_calls:
                    query = agent_msg.tool_calls[0]["args"].get("query", "")
                    searches.append(f"🔎 Search {iteration}: {query}")
                    progress_placeholder.text("\n".join(searches))
                    iteration += 1
                else:
                    raw_research = agent_msg.content
                    progress_placeholder.text("\n".join(searches) + "\n🧠 Agent: done researching, compiling results...")

        # Step 2: Format report
        report = format_report(topic, raw_research)

        # Display report
        st.markdown(report)

        # Clean report for download
        clean_report = clean_markdown(report)

        # Download button
        st.download_button(
            label="Download Report as TXT",
            data=clean_report,
            file_name=f"{topic.lower().replace(' ', '_')[:40]}_report.txt",
            mime="text/plain"
        )