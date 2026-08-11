import json
import streamlit as st
from frontend.utils.api_client import api_client


def render_chat_view():
    st.title("💬 HyperAgent Task Execution Interface")
    st.caption(
        "Interact with the LangGraph TaskAgent using prompt and code heuristics from any evolved generation.")

    # Fetch generations for selector
    generations = api_client.get_evolution_history()
    if not generations:
        st.warning(
            "⚠️ Could not connect to backend archive or no generations found. Operating in local mode.")
        gen_options = ["gen_0"]
    else:
        gen_options = [g["generation_id"] for g in generations]

    col_sel, col_info = st.columns([1, 2])
    with col_sel:
        selected_gen = st.selectbox(
            "Select Target Generation Version", options=gen_options, index=len(gen_options)-1)

    with col_info:
        if generations:
            curr_g = next(
                (g for g in generations if g["generation_id"] == selected_gen), generations[-1])
            st.info(
                f"**Selected**: `{selected_gen}` | **Score**: `{curr_g.get('score', 0)}/100` | **Parent**: `{curr_g.get('parent_id', 'None')}`")

    st.markdown("---")

    # Initialize chat message state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I am your self-improving HyperAgent TaskAgent. Ask me any domain task (e.g. math calculation, web research, code execution, or logic deduction).",
                "generation_id": selected_gen
            }
        ]

    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("generation_id"):
                st.caption(f"Generation Version: `{msg['generation_id']}`")
            st.markdown(msg["content"])
            if "thought_steps" in msg and msg["thought_steps"]:
                with st.expander("🔍 Trajectory & Tool Execution Steps", expanded=False):
                    for step in msg["thought_steps"]:
                        st.write(step)

    # User Input Chat Box
    if user_query := st.chat_input("Enter your task objective or query..."):
        # Add user message
        st.session_state.messages.append(
            {"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Assistant Stream Container
        with st.chat_message("assistant"):
            st.caption(f"Generation Version: `{selected_gen}`")
            message_placeholder = st.empty()
            status_container = st.empty()
            thought_steps = []
            full_response = ""

            status_container.status(
                f"⚡ TaskAgent ReAct Execution (Gen {selected_gen})...", expanded=True)

            # Consume SSE Stream from Backend
            for event in api_client.stream_chat(user_query, generation_id=selected_gen):
                event_type = event.get("type")

                if event_type == "status":
                    status_container.write(f"ℹ️ {event.get('message')}")
                    thought_steps.append(f"Status: {event.get('message')}")
                elif event_type == "thought":
                    thought_steps.append(
                        f"Thought Step {event.get('step')}: {event.get('content')}")
                    status_container.write(
                        f"💭 **Reasoning**: {event.get('content')}")
                elif event_type == "tool_start":
                    thought_steps.append(
                        f"Tool Invoked: `{event.get('tool')}` with input: `{event.get('tool_input')}`")
                    status_container.write(
                        f"🛠️ **Executing Tool**: `{event.get('tool')}`...")
                elif event_type == "observation":
                    thought_steps.append(
                        f"Observation: {event.get('observation')}")
                    status_container.write(
                        f"👁️ **Observation**: {event.get('observation')}")
                elif event_type == "token":
                    full_response += event.get("content", "")
                    message_placeholder.markdown(full_response + "▌")
                elif event_type == "done":
                    status_container.update(
                        label="✅ Task Execution Complete", state="complete", expanded=False)

            message_placeholder.markdown(full_response)

            # Save Assistant Response to Session State
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "generation_id": selected_gen,
                "thought_steps": thought_steps
            })

    # File Download & Export Section
    st.markdown("---")
    col_dl1, col_dl2 = st.columns([1, 1])

    with col_dl1:
        # Export as Markdown
        md_text = f"# HyperAgent Conversation History (Gen {selected_gen})\n\n"
        for m in st.session_state.messages:
            md_text += f"### {m['role'].upper()}\n{m['content']}\n\n"
        st.download_button(
            label="📥 Download Chat Log (.MD)",
            data=md_text,
            file_name="hyperagent_chat_log.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col_dl2:
        # Export as JSON
        json_data = json.dumps(st.session_state.messages, indent=2)
        st.download_button(
            label="📥 Download Chat Data (.JSON)",
            data=json_data,
            file_name="hyperagent_chat_log.json",
            mime="application/json",
            use_container_width=True
        )
