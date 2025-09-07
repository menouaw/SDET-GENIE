"""
Agent History view UI components for SDET-GENIE application.
Handles the display of comprehensive agent history and analysis.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any


def render_agent_history(history: Dict[str, Any]):
    """Render comprehensive agent history information."""
    st.markdown('<h4 class="glow-text">📜 Agent History & Analysis</h4>', unsafe_allow_html=True)
    
    # Create tabs for different history views
    history_tab1, history_tab2, history_tab3, history_tab4 = st.tabs([
        "📊 Execution Flow", 
        "💬 Conversation History", 
        "🧠 Decision Analysis", 
        "📈 Performance Metrics"
    ])
    
    with history_tab1:
        _render_execution_flow(history)
    
    with history_tab2:
        _render_conversation_history(history)
    
    with history_tab3:
        _render_decision_analysis(history)
        
    with history_tab4:
        _render_performance_metrics(history)


def _render_execution_flow(history: Dict[str, Any]):
    """Render the execution flow timeline."""
    st.markdown("### 🔄 Execution Flow Timeline")
    
    # Combine URLs, actions, and model outputs into a timeline
    timeline_events = []
    
    # Add URL visits
    urls = history.get('urls', [])
    for i, url in enumerate(urls):
        timeline_events.append({
            "step": i + 1,
            "type": "🌐 URL Visit",
            "content": url,
            "timestamp": f"Step {i + 1}"
        })
    
    # Add actions
    actions = history.get('action_names', [])
    for i, action in enumerate(actions):
        timeline_events.append({
            "step": len(urls) + i + 1,
            "type": "⚡ Action",
            "content": action,
            "timestamp": f"Step {len(urls) + i + 1}"
        })
    
    # Add model outputs
    model_outputs = history.get('model_outputs', [])
    for i, output in enumerate(model_outputs):
        timeline_events.append({
            "step": len(urls) + len(actions) + i + 1,
            "type": "🤖 LLM Response",
            "content": str(output)[:100] + "..." if len(str(output)) > 100 else str(output),
            "timestamp": f"Step {len(urls) + len(actions) + i + 1}"
        })
    
    # Sort by step
    timeline_events.sort(key=lambda x: x['step'])
    
    # Display timeline
    for event in timeline_events:
        if event['type'] == "🌐 URL Visit":
            st.markdown(f"""
            <div style='display: flex; align-items: center; margin: 8px 0; padding: 10px; background-color: #e3f2fd; border-radius: 8px; border-left: 4px solid #2196F3;'>
                <div style='min-width: 100px; font-weight: bold; color: #2196F3;'>{event['timestamp']}</div>
                <div style='min-width: 120px; font-weight: bold;'>{event['type']}</div>
                <div style='flex-grow: 1; color: #333; font-family: monospace;'>{event['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        elif event['type'] == "⚡ Action":
            st.markdown(f"""
            <div style='display: flex; align-items: center; margin: 8px 0; padding: 10px; background-color: #fff3e0; border-radius: 8px; border-left: 4px solid #FF9800;'>
                <div style='min-width: 100px; font-weight: bold; color: #FF9800;'>{event['timestamp']}</div>
                <div style='min-width: 120px; font-weight: bold;'>{event['type']}</div>
                <div style='flex-grow: 1; color: #333;'>{event['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        elif event['type'] == "🤖 LLM Response":
            with st.expander(f"{event['timestamp']} - {event['type']}", expanded=False):
                st.markdown(f"<div style='background-color: #f5f5f5; padding: 10px; border-radius: 5px; font-family: monospace;'>{event['content']}</div>", unsafe_allow_html=True)


def _render_conversation_history(history: Dict[str, Any]):
    """Render the conversation history between agent and LLM."""
    st.markdown("### 💬 Agent-LLM Conversation History")
    
    model_outputs = history.get('model_outputs', [])
    model_actions = history.get('model_actions', [])
    
    if model_outputs or model_actions:
        st.info(f"Total conversation turns: {len(model_outputs)}")
        
        # Display conversation in pairs
        for i, (output, action) in enumerate(zip(model_outputs, model_actions)):
            st.markdown(f"#### 🔄 Turn {i+1}")
            
            # LLM Response
            with st.expander("🤖 LLM Response", expanded=True):
                if isinstance(output, dict):
                    st.json(output)
                else:
                    st.markdown(f"<div style='background-color: #e8f5e9; padding: 10px; border-radius: 5px;'><pre>{output}</pre></div>", unsafe_allow_html=True)
            
            # Agent Action
            with st.expander("⚡ Agent Action", expanded=True):
                if isinstance(action, dict):
                    st.json(action)
                else:
                    st.markdown(f"<div style='background-color: #fff3e0; padding: 10px; border-radius: 5px;'><pre>{action}</pre></div>", unsafe_allow_html=True)
    else:
        st.info("No conversation history was captured during execution.")


def _render_decision_analysis(history: Dict[str, Any]):
    """Render decision analysis based on agent history."""
    st.markdown("### 🧠 Decision Analysis")
    
    st.markdown("""
    <div style='background-color: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3; margin-bottom: 15px;'>
        <h5>🔍 Agent Decision Patterns</h5>
        <p>Analysis of how the agent made decisions during execution:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action analysis
    actions = history.get('action_names', [])
    if actions:
        st.markdown("#### ⚡ Action Patterns")
        
        # Count action types
        action_counts = {}
        for action in actions:
            action_type = action.split()[0] if action else "Unknown"
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        # Display as dataframe
        if action_counts:
            action_df = pd.DataFrame([
                {"Action Type": action_type, "Count": count}
                for action_type, count in action_counts.items()
            ])
            st.dataframe(action_df, use_container_width=True)
        
        # Most common actions
        if action_counts:
            most_common = max(action_counts.items(), key=lambda x: x[1])
            st.markdown(f"**Most Common Action:** {most_common[0]} ({most_common[1]} times)")
    
    # Error analysis
    errors = history.get('errors', [])
    if errors:
        st.markdown("#### ❌ Error Analysis")
        
        critical_errors = []
        warnings = []
        
        for error in errors:
            error_str = str(error).lower()
            if any(keyword in error_str for keyword in ['failed', 'error', 'exception', 'timeout', 'invalid', 'not found']):
                critical_errors.append(error)
            else:
                warnings.append(error)
        
        if critical_errors:
            st.error(f"Critical Errors: {len(critical_errors)}")
            for error in critical_errors:
                st.markdown(f"<div style='background-color: #ffe6e6; padding: 8px; border-radius: 5px; margin: 5px 0;'><strong>Error:</strong> {error}</div>", unsafe_allow_html=True)
        
        if warnings:
            st.warning(f"Warnings: {len(warnings)}")
            for warning in warnings:
                st.markdown(f"<div style='background-color: #fff3cd; padding: 8px; border-radius: 5px; margin: 5px 0;'><strong>Warning:</strong> {warning}</div>", unsafe_allow_html=True)
    
    # Success analysis
    is_successful = history.get('is_successful', None)
    if is_successful is not None:
        st.markdown("#### 📈 Success Metrics")
        if is_successful:
            st.success("✅ Execution completed successfully")
            st.markdown("The agent was able to complete all tasks without critical errors.")
        else:
            st.error("❌ Execution failed")
            st.markdown("The agent encountered issues that prevented successful completion.")


def _render_performance_metrics(history: Dict[str, Any]):
    """Render performance metrics from agent history."""
    st.markdown("### 📊 Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        duration = history.get('total_duration', 0)
        st.metric("⏱️ Total Duration", f"{duration:.2f}s")
    
    with col2:
        steps = history.get('number_of_steps', 0)
        st.metric("🔢 Total Steps", steps)
    
    with col3:
        actions = len(history.get('action_names', []))
        st.metric("⚡ Actions", actions)
    
    with col4:
        errors = len([e for e in history.get('errors', []) if e])
        st.metric("❌ Errors", errors)
    
    # Calculate additional metrics
    st.markdown("#### 📈 Detailed Metrics")
    
    if duration > 0 and steps > 0:
        avg_time_per_step = duration / steps
        st.metric("⏱️ Avg Time/Step", f"{avg_time_per_step:.2f}s")
    
    if duration > 0 and actions > 0:
        actions_per_second = actions / duration
        st.metric("⚡ Actions/Second", f"{actions_per_second:.2f}")
    
    # URLs visited
    urls = history.get('urls', [])
    if urls:
        st.metric("🌐 URLs Visited", len(urls))
        with st.expander("Visited URLs"):
            for url in urls:
                st.markdown(f"- {url}")
    
    # Screenshots captured
    screenshots = history.get('screenshots', [])
    if screenshots:
        st.metric("📸 Screenshots", len(screenshots))
    
    # Elements interacted with
    elements = history.get('element_xpaths', {})
    if elements:
        st.metric("🎯 Elements Interacted", len(elements))