import streamlit as st

st.set_page_config(
    page_title="HyperAgent Self-Improving System",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

from views.chat_view import render_chat_view
from views.dashboard_view import render_dashboard_view
from utils.api_client import api_client

def main():
    # Sidebar Navigation & System Info
    st.sidebar.image("https://img.icons8.com/isometric-folders/100/brain.png", width=64)
    st.sidebar.title("HyperAgent Architecture")
    st.sidebar.caption("Inspired by Meta's HyperAgents Research")
    st.sidebar.markdown("---")

    # Backend Connection Status Check
    is_online = api_client.check_health()
    if is_online:
        st.sidebar.success("🟢 Backend Status: Online (FastAPI)")
    else:
        st.sidebar.warning("🔴 Backend Status: Local Standalone / Connecting")

    # View Mode Radio Selection
    view_mode = st.sidebar.radio(
        "Navigation Menu",
        options=["💬 TaskAgent Chat", "🧬 Evolution Dashboard"],
        index=1
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("System Highlights")
    st.sidebar.markdown(
        "- **TaskAgent**: LangGraph ReAct Loop\n"
        "- **MetaAgent**: Autonomous Prompt Mutator\n"
        "- **Selection**: Score-Proportional Softmax\n"
        "- **Evaluator**: LLM Judge Rubric Scoring\n"
        "- **Archive**: Persistent Version Control"
    )

    # Render Active View
    if view_mode == "💬 TaskAgent Chat":
        render_chat_view()
    else:
        render_dashboard_view()

if __name__ == "__main__":
    main()
