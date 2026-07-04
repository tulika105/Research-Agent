import os
import time
import gradio as gr
from dotenv import load_dotenv
from agent import build_agent
from report_web import format_report_web, save_report_web

load_dotenv()

# ── Theme ────────────────────────────────────────────────────────────────────
theme = gr.themes.Soft(
    primary_hue=gr.themes.colors.zinc,
    secondary_hue=gr.themes.colors.zinc,
    neutral_hue=gr.themes.colors.zinc,
    font=(gr.themes.GoogleFont("Plus Jakarta Sans"), "ui-sans-serif", "system-ui", "sans-serif"),
).set(
    body_background_fill="#e6e6fa",
    block_background_fill="#e6e6fa",
    block_border_width="0px",
    block_label_text_color="#000000",
    body_text_color="#000000",
    button_primary_background_fill="#000000",
    button_primary_background_fill_hover="#333333",
    button_primary_text_color="white",
    input_background_fill="#ffffff",
    input_border_color="#e5e7eb",
)

CSS = """
/* FINAL STARK MINIMAL UI */
body, .gradio-container { 
    background: #e6e6fa !important; 
    min-height: 100vh;
    color: #000000 !important;
}
.gradio-container { 
    max-width: 100% !important; /* Full Screen Chatbot Area */
    margin: auto; 
    padding: 2rem 5% !important; 
}

#app-header {
    text-align: center;
    margin-bottom: 2.5rem;
}
#app-header h1 { 
    font-size: 3rem; 
    font-weight: 800; 
    color: #000000;
    margin: 0; 
    letter-spacing: -0.02em;
}
#app-header p { color: #666666; font-size: 1.1rem; margin-top: 0.5rem; font-weight: 500; }

/* REFINED HORIZONTAL SEARCH BAR - NO SCROLLBAR */
#search-desk {
    background: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 100px !important;
    padding: 0.5rem 0.75rem !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05) !important;
    margin: 1rem auto 3rem auto !important;
    max-width: 1000px; 
    display: flex;
    align-items: center;
}

#topic-input textarea {
    background: transparent !important;
    border: none !important;
    color: #000000 !important;
    font-size: 1.25rem !important;
    font-weight: 500 !important;
    padding: 0.8rem 1rem !important;
    overflow: hidden !important; 
    resize: none !important;
    white-space: nowrap !important;
    height: auto !important;
}
#topic-input textarea::placeholder { color: #9ca3af !important; }

#submit-btn {
    border-radius: 100px !important;
    padding: 0.6rem 2.5rem !important;
    font-weight: 800 !important;
    font-size: 1.1rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    height: auto !important;
    margin: 0 !important;
    background: #000000 !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
}

/* FULL SCREEN CHATBOT */
#chatbot { 
    background: transparent !important; 
    border: none !important;
    padding: 1rem !important;
    box-shadow: none !important;
    height: auto !important;
    min-height: 400px;
}

.message.user {
    background: #f1f5f9 !important;
    color: #000000 !important;
    border-radius: 1.5rem 1.5rem 0.25rem 1.5rem !important;
    padding: 1.25rem 1.75rem !important;
    font-size: 1.15rem !important;
    margin-bottom: 2rem !important;
    border: 1px solid #e2e8f0 !important;
}

.message.assistant {
    background: transparent !important;
    color: #000000 !important;
    font-size: 0.95rem !important;
    padding: 0 !important;
    border: none !important;
    margin-bottom: 3rem !important;
}

/* Force markdown elements to be BLACK in light mode */
.message.assistant, .message.assistant p, .message.assistant h1, .message.assistant h2, .message.assistant h3, .message.assistant li, .message.assistant span, .message.assistant strong, .message.assistant td, .message.assistant th {
    color: #000000 !important;
}

/* PREMIUM ANIMATED REASONING UI */
.status-update {
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important; 
    margin: 1rem 0 1rem 1rem !important; 
    display: inline-flex;
    align-items: center;
    background: linear-gradient(135deg, #8b5cf6, #3b82f6) !important;
    padding: 0.6rem 1.4rem !important;
    border-radius: 9999px !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3) !important;
    letter-spacing: 0.02em;
    animation: status-pulse 2s infinite ease-in-out;
}
.status-update:before {
    content: "⚡"; 
    margin-right: 0.6rem;
    font-size: 1.1rem;
}
@keyframes status-pulse {
    0% { transform: scale(1); box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3); }
    50% { transform: scale(1.02); box-shadow: 0 4px 20px rgba(139, 92, 246, 0.5); }
    100% { transform: scale(1); box-shadow: 0 4px 15px rgba(139, 92, 246, 0.3); }
}

#download-btn {
    width: auto !important;
    max-width: 300px;
    margin: -1rem auto 2rem auto !important;
    border-radius: 100px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.6rem 1.5rem !important;
    background: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #000000 !important;
    display: flex;
    justify-content: center;
}
#download-btn:hover {
    background: #e2e8f0 !important;
}

footer { display: none !important; }
"""


# ── Core research function ──────────────────────────────────────────────────
def run_research(topic: str, chat_history: list):
    """Stream the ReAct agent's search steps, then format and return the report."""

    if not topic or not topic.strip():
        chat_history.append(
            gr.ChatMessage(role="assistant", content="⚠️ Please enter a research topic if you'd like me to start.")
        )
        yield chat_history, gr.update(visible=False), None
        return

    if not os.environ.get("GROQ_API_KEY"):
        chat_history.append(
            gr.ChatMessage(role="assistant", content="❌ `GROQ_API_KEY` not found. Add it to your `.env` file or set it as a Space Secret.")
        )
        yield chat_history, gr.update(visible=False), None
        return

    # Show user message
    chat_history.append(gr.ChatMessage(role="user", content=f"Could you research **{topic.strip()}** for me?"))
    yield chat_history, gr.update(visible=False), None

    # ── Stream the ReAct loop ────────────────────────────────────────────
    agent = build_agent()
    raw_research = ""

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": f"Research this topic thoroughly and gather as much factual information as possible: {topic.strip()}"}]}
    ):
        if "agent" in chunk:
            agent_msg = chunk["agent"]["messages"][0]
            if agent_msg.tool_calls:
                query = agent_msg.tool_calls[0]["args"].get("query", "")
                chat_history.append(
                    gr.ChatMessage(role="assistant", content=f'<div class="status-update">🔍 Searching: {query}...</div>')
                )
                yield chat_history, gr.update(visible=False), None
            else:
                raw_research = agent_msg.content

    chat_history.append(
        gr.ChatMessage(role="assistant", content='<div class="status-update">✨ Organizing results into a structured report...</div>')
    )
    yield chat_history, gr.update(visible=False), None

    report = format_report_web(topic.strip(), raw_research)
    filepath = save_report_web(topic.strip(), report)

    spaced_report = f'<div style="margin-top: 3rem;"></div>\n\n{report}'
    
    chat_history.append(
        gr.ChatMessage(role="assistant", content=spaced_report)
    )
    yield chat_history, gr.update(value=filepath, visible=True), filepath


# ── Build UI ─────────────────────────────────────────────────────────────────
with gr.Blocks() as demo:
    with gr.Row(elem_id="app-header"):
        with gr.Column():
            gr.HTML("""
                <h1>🤖 Autonomous Researcher</h1>
                <p>Powered by LangGraph & ReAct</p>
            """)

    with gr.Row(elem_id="search-desk"):
        topic_input = gr.Textbox(
            placeholder="Type a research topic (e.g. LangChain 2024)...",
            show_label=False,
            container=False,
            scale=10,
            lines=1,
            max_lines=1,
            elem_id="topic-input"
        )
        submit_btn = gr.Button("RESEARCH", variant="primary", scale=1, elem_id="submit-btn")

    with gr.Row():
        chatbot = gr.Chatbot(
            elem_id="chatbot",
            show_label=False,
            height="auto",
            avatar_images=(None, "https://em-content.zobj.net/source/twitter/408/robot_1f916.png"),
            render_markdown=True,
        )

    with gr.Row():
        download_btn = gr.DownloadButton("📥 Download Report", visible=False, variant="secondary", elem_id="download-btn")

    # State to hold the file path
    file_state = gr.State(None)

    # Wire events
    submit_btn.click(
        fn=run_research,
        inputs=[topic_input, chatbot],
        outputs=[chatbot, download_btn, file_state],
    ).then(lambda: "", outputs=[topic_input])

    topic_input.submit(
        fn=run_research,
        inputs=[topic_input, chatbot],
        outputs=[chatbot, download_btn, file_state],
    ).then(lambda: "", outputs=[topic_input])


if __name__ == "__main__":
    demo.launch(theme=theme, css=CSS)
