from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from tools import get_search_tool
import os

SYSTEM_PROMPT = """You are a thorough research agent. When given a topic, you MUST search at least 5 times before stopping.

Follow this exact research plan:
1. Search for a broad overview of the topic
2. Search for recent developments or news related to the topic
3. Search for technical details, how it works, or key concepts
4. Search for real-world applications or use cases
5. Search for limitations, challenges, or criticisms

Do NOT stop after 1 or 2 searches. Each search must use a different, specific query."""

def build_agent():
    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        groq_api_key=os.environ["GROQ_API_KEY"]
    )

    tools = [get_search_tool()]

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT
    )

    return agent