import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text
from rich.table import Table
from agent import build_agent
from report import format_report, save_report

load_dotenv()
console = Console()

def check_env():
    if not os.environ.get("GROQ_API_KEY"):
        console.print("[bold red]❌ GROQ_API_KEY not found. Add it to your .env file.[/bold red]")
        sys.exit(1)

def run():
    check_env()

    # Impressive header
    title_text = Text("🔍 Research Agent", style="bold cyan", justify="center")
    subtitle_text = Text("Powered by Groq + DuckDuckGo", style="italic bright_black", justify="center")
    console.print(Panel(title_text, expand=False, border_style="cyan"))
    console.print(Panel(subtitle_text, expand=False, border_style="blue"))

    # Get topic from argument or prompt
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = console.input("\n[bold]Enter a research topic:[/bold] ")

    if not topic:
        console.print("[bold red]❌ No topic provided.[/bold red]")
        sys.exit(1)

    console.print(f"\n[bold blue]📡 Researching:[/bold blue] [yellow]'{topic}'[/yellow]")
    console.print("[dim](ReAct agent is thinking... watch the steps below)[/dim]\n")
    console.rule(style="blue")

    # Step 1: Stream ReAct agent to show live reasoning loop
    agent = build_agent()
    raw_research = ""
    iteration = 1
    search_table = Table(title="Search Queries", show_header=False, border_style="cyan")
    searches = []

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": f"Research this topic thoroughly and gather as much factual information as possible: {topic}"}]}
    ):
        if "agent" in chunk:
            agent_msg = chunk["agent"]["messages"][0]
            if agent_msg.tool_calls:
                # LLM decided to search — print the query before DDG runs
                query = agent_msg.tool_calls[0]["args"].get("query", "")
                search_item = f"[cyan]Search {iteration}:[/cyan] {query}"
                searches.append(search_item)
                console.print(f"\n{search_item}")
                iteration += 1
            else:
                # No tool calls = final answer
                raw_research = agent_msg.content
                console.print(f"\n[bold green]✓[/bold green] [bold]Agent: Done researching, compiling results...[/bold]")

    # Step 2: Format into structured report
    console.print("\n")
    console.rule(style="blue")
    with console.status("[bold cyan]📝 Formatting structured report...[/bold cyan]", spinner="dots"):
        report = format_report(topic, raw_research)
    console.print()

    # Step 3: Print report
    print(report)

    # Step 4: Offer to save
    save = console.input("\n[bold]💾 Save report to file?[/bold] [cyan](y/n):[/cyan] ").strip().lower()
    if save == "y":
        with console.status("[bold cyan]Saving...[/bold cyan]", spinner="dots"):
            filename = save_report(topic, report)
        console.print(f"[bold green]✅ Saved to:[/bold green] [blue]{filename}[/blue]")

if __name__ == "__main__":
    run()