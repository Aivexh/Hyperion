
import json
import streamlit as st
from utils.api_client import api_client


def render_chat_view():
    st.title("💬 HyperAgent Task Execution Interface")
    st.caption(
        "Interact with the LangGraph TaskAgent using prompt and code "
        "heuristics from any evolved generation."
    )

    # Fetch available generations
    generations = api_client.get_evolution_history()

    if not generations:
        st.warning(
            "Could not connect to the backend archive or no generations "
            "were found. Operating in local mode."
        )
        gen_options = ["gen_0"]
    else:
        gen_options = [g["generation_id"] for g in generations]

    # Generation selector
    col_sel, col_info = st.columns([1, 2])

    with col_sel:
        selected_gen = st.selectbox(
            "Select Target Generation Version",
            options=gen_options,
            index=len(gen_options) - 1,
        )

    with col_info:
        if generations:
            curr_gen = next(
                (
                    g for g in generations
                    if g["generation_id"] == selected_gen
                ),
                generations[-1],
            )
            st.info(
                f"**Selected**: `{selected_gen}` | "
                f"**Score**: `{curr_gen.get('score', 0)}/100` | "
                f"**Parent**: `{curr_gen.get('parent_id', 'None')}`"
            )

    st.markdown("---")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am your self-improving HyperAgent TaskAgent. "
                    "Ask me any domain task, such as math calculation, "
                    "web research, code execution, or logic deduction."
                ),
                "generation_id": selected_gen,
            }
        ]

    # Display previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("generation_id"):
                st.caption(
                    f"Generation Version: `{msg['generation_id']}`"
                )

            st.markdown(msg["content"])

            if msg.get("thought_steps"):
                with st.expander(
                    "Trajectory & Tool Execution Steps",
                    expanded=False,
                ):
                    for step in msg["thought_steps"]:
                        st.write(step)

    # Chat input
    user_query = st.chat_input("Enter your task objective or query...")

    if user_query:
        st.session_state.messages.append(
            {"role": "user", "content": user_query}
        )

        with st.chat_message("user"):
            st.markdown(user_query)

        # Assistant response area
        with st.chat_message("assistant"):
            st.caption(f"Generation Version: `{selected_gen}`")

            message_placeholder = st.empty()
            thought_steps = []
            full_response = ""
            completed = False

            # Create a proper Streamlit status container
            with st.status(
                f"TaskAgent executing (Gen {selected_gen})...",
                expanded=True,
            ) as status_container:

                try:
                    # Consume the backend SSE stream
                    for event in api_client.stream_chat(
                        user_query,
                        generation_id=selected_gen,
                    ):
                        event_type = event.get("type")

                        if event_type == "status":
                            message = event.get("message", "")
                            status_container.write(f"ℹ️ {message}")
                            thought_steps.append(f"Status: {message}")

                        elif event_type == "thought":
                            content = event.get("content", "")
                            step = event.get("step", "")

                            thought_steps.append(
                                f"Thought Step {step}: {content}"
                            )
                            status_container.write(
                                f"💭 **Reasoning**: {content}"
                            )

                        elif event_type == "tool_start":
                            tool = event.get("tool", "Unknown tool")
                            tool_input = event.get("tool_input", "")

                            thought_steps.append(
                                f"Tool Invoked: `{tool}` "
                                f"with input: `{tool_input}`"
                            )
                            status_container.write(
                                f"🛠️ **Executing Tool**: `{tool}`..."
                            )

                        elif event_type == "observation":
                            observation = event.get("observation", "")

                            thought_steps.append(
                                f"Observation: {observation}"
                            )
                            status_container.write(
                                f"👁️ **Observation**: {observation}"
                            )

                        elif event_type == "token":
                            full_response += event.get("content", "")
                            message_placeholder.markdown(
                                full_response + " ▌"
                            )

                        elif event_type == "done":
                            completed = True
                            status_container.update(
                                label="Task Execution Complete",
                                state="complete",
                                expanded=False,
                            )

                except Exception as exc:
                    error_message = (
                        "An error occurred while communicating with "
                        f"HyperAgent: {exc}"
                    )
                    st.error(error_message)
                    thought_steps.append(error_message)

                # Handle streams that end without a done event
                if not completed:
                    status_container.update(
                        label=(
                            "Task finished"
                            if full_response
                            else "Task ended without a complete response"
                        ),
                        state="complete" if full_response else "error",
                        expanded=not bool(full_response),
                    )

            # Display final response
            if full_response:
                message_placeholder.markdown(full_response)
            elif not any(
                "An error occurred" in step for step in thought_steps
            ):
                message_placeholder.warning(
                    "HyperAgent returned no response. "
                    "Please check the backend logs and try again."
                )

            # Save assistant response
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response or (
                        "I couldn't generate a response. "
                        "Please try again or check the backend logs."
                    ),
                    "generation_id": selected_gen,
                    "thought_steps": thought_steps,
                }
            )

    # Download and export conversation
    st.markdown("---")
    col_dl1, col_dl2 = st.columns(2)

    with col_dl1:
        md_text = (
            f"# HyperAgent Conversation History "
            f"(Gen {selected_gen})\n\n"
        )

        for message in st.session_state.messages:
            md_text += (
                f"### {message['role'].upper()}\n"
                f"{message['content']}\n\n"
            )

        st.download_button(
            label="Download Chat Log (.MD)",
            data=md_text,
            file_name="hyperagent_chat_log.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col_dl2:
        json_data = json.dumps(
            st.session_state.messages,
            indent=2,
            ensure_ascii=False,
        )

        st.download_button(
            label="Download Chat Data (.JSON)",
            data=json_data,
            file_name="hyperagent_chat_log.json",
            mime="application/json",
            use_container_width=True,
        )
