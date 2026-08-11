import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from frontend.utils.api_client import api_client
from frontend.utils.diff_utils import render_side_by_side_diff


def render_dashboard_view():
    st.title("🧬 HyperAgent Evolution & Self-Improvement Dashboard")
    st.caption(
        "Meta-HyperAgent autonomous prompt and code optimization engine metrics.")

    # 1. Fetch Evolution History
    generations = api_client.get_evolution_history()

    if not generations:
        st.error(
            "⚠️ Backend Archive unavailable. Click 'Trigger Evolution' below to run initial seed cycle.")
        generations = []

    # Calculate Header KPI Metrics
    total_gens = len(generations)
    latest_gen = generations[-1] if generations else {
        "generation_id": "gen_0", "score": 62.5, "parent_id": None}
    baseline_gen = generations[0] if generations else latest_gen

    best_score = max([g.get("score", 0)
                     for g in generations]) if generations else 62.5
    baseline_score = baseline_gen.get("score", 62.5)
    delta_score = round(best_score - baseline_score, 1)

    # 2. KPI Summary Cards
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    with col_kpi1:
        st.metric(label="Total Generations", value=total_gens)
    with col_kpi2:
        st.metric(label="Peak Rubric Score",
                  value=f"{best_score}/100", delta=f"+{delta_score} pts" if delta_score > 0 else None)
    with col_kpi3:
        st.metric(label="Baseline Score (G0)", value=f"{baseline_score}/100")
    with col_kpi4:
        st.metric(label="Avg Token Cost",
                  value=f"${latest_gen.get('token_cost', 0.0015):.5f}")

    st.markdown("---")

    # 3. Interactive Score Timeline Chart & Trigger Evolution Button
    col_chart, col_trigger = st.columns([2, 1])

    with col_chart:
        st.subheader("📈 Performance Score Progression Timeline")
        if generations:
            df = pd.DataFrame(generations)
            fig = px.line(
                df,
                x="generation_id",
                y="score",
                markers=True,
                title="Optimization Trajectory (Meta-HyperAgent Score-Proportional Selection)",
                labels={"generation_id": "Generation Version",
                        "score": "LLM Judge Score"},
                line_shape="spline"
            )
            fig.update_traces(line_color="#4F46E5", line_width=4,
                              marker_size=10, marker_color="#10B981")
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15,23,42,0.6)",
                font=dict(family="sans-serif", size=12),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

    with col_trigger:
        st.subheader("⚡ Autonomous Evolution Control")
        st.write(
            "Trigger the MetaAgent to mutate system prompts, run judge benchmarks, and archive the next generation.")

        trigger_btn = st.button(
            "🚀 Trigger Next Generation Evolution", type="primary", use_container_width=True)

        log_box = st.empty()
        progress_bar = st.progress(0)

        if trigger_btn:
            log_messages = []
            progress_val = 0

            with st.spinner("MetaAgent executing parent selection & prompt mutation..."):
                for event in api_client.stream_evolution_trigger():
                    event_type = event.get("type")
                    if event_type == "log":
                        msg = event.get("message", "")
                        log_messages.append(msg)
                        progress_val = min(90, progress_val + 25)
                        progress_bar.progress(progress_val)
                        log_box.code("\n".join(log_messages), language="text")
                    elif event_type == "generation_created":
                        progress_bar.progress(100)
                        gen_info = event.get("generation", {})
                        st.success(
                            f"🎉 Created Generation `{gen_info.get('generation_id')}`! Score: `{gen_info.get('score')}` (+{event.get('score_delta')} pts)")
                        st.rerun()

    st.markdown("---")

    # 4. Generation Comparison Table & Side-by-Side Prompt Diff Viewer
    st.subheader("🔍 Side-by-Side Generation Prompt Diff Viewer")

    if len(generations) >= 1:
        gen_list = [g["generation_id"] for g in generations]
        col_da, col_db = st.columns(2)

        with col_da:
            gen_a_id = st.selectbox(
                "Select Base Parent Generation (Left)", options=gen_list, index=0)
        with col_db:
            gen_b_id = st.selectbox(
                "Select Target Mutated Generation (Right)", options=gen_list, index=len(gen_list)-1)

        diff_data = api_client.get_generation_diff(gen_a_id, gen_b_id)

        if diff_data and "prompt_a" in diff_data:
            st.markdown(
                f"**Score Comparison**: `{gen_a_id}` ({diff_data['score_a']}) ➡️ `{gen_b_id}` ({diff_data['score_b']}) | "
                f"**Delta**: `+{diff_data['score_delta']} pts`"
            )
            html_diff = render_side_by_side_diff(
                diff_data["prompt_a"],
                diff_data["prompt_b"],
                label_a=f"Generation {gen_a_id} (Score: {diff_data['score_a']})",
                label_b=f"Generation {gen_b_id} (Score: {diff_data['score_b']})"
            )
            st.components.v1.html(html_diff, height=450, scrolling=True)

    st.markdown("---")

    # 5. Full Archive Data Table
    st.subheader("📊 Generations Archive Summary Table")
    if generations:
        table_data = []
        for g in generations:
            table_data.append({
                "Generation ID": g.get("generation_id"),
                "Parent ID": g.get("parent_id", "Seed G0"),
                "Rubric Score": g.get("score"),
                "Correctness": g.get("rubric_scores", {}).get("correctness", 0),
                "Tool Efficiency": g.get("rubric_scores", {}).get("tool_efficiency", 0),
                "Reasoning": g.get("rubric_scores", {}).get("reasoning_clarity", 0),
                "Estimated Cost ($)": g.get("token_cost", 0.0015),
                "Status": g.get("status", "active")
            })
        st.dataframe(pd.DataFrame(table_data), use_container_width=True)
