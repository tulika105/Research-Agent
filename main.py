import os
import sys
from dotenv import load_dotenv
from agent import build_agent
from report import format_report, save_report

load_dotenv()

def check_env():
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY not found. Add it to your .env file.")
        sys.exit(1)

def run():
    check_env()

    print("\n🔍 Research Agent — powered by Groq + DuckDuckGo")
    print("="*50)

    # Get topic from argument or prompt
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("\nEnter a research topic: ").strip()

    if not topic:
        print("❌ No topic provided.")
        sys.exit(1)

    print(f"\n📡 Researching: '{topic}'")
    print("(ReAct agent is thinking... watch the steps below)\n")
    print("-"*50)

    # Step 1: Stream ReAct agent to show live reasoning loop
    agent = build_agent()
    raw_research = ""
    iteration = 1

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": f"Research this topic thoroughly and gather as much factual information as possible: {topic}"}]}
    ):
        if "agent" in chunk:
            agent_msg = chunk["agent"]["messages"][0]
            if agent_msg.tool_calls:
                # LLM decided to search — print the query before DDG runs
                query = agent_msg.tool_calls[0]["args"].get("query", "")
                print(f"\n🔎 Search {iteration}: {query}")
                iteration += 1
            else:
                # No tool calls = final answer
                raw_research = agent_msg.content
                print(f"\n🧠 Agent: done researching, compiling results...")

    # Step 2: Format into structured report
    print("\n" + "-"*50)
    print("📝 Formatting structured report...\n")
    report = format_report(topic, raw_research)

    # Step 3: Print report
    print(report)

    # Step 4: Offer to save
    save = input("\n💾 Save report to file? (y/n): ").strip().lower()
    if save == "y":
        filename = save_report(topic, report)
        print(f"✅ Saved to: {filename}")

if __name__ == "__main__":
    run()