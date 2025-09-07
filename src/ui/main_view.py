"""
Main view UI components for SDET-GENIE application.
Handles the main content area rendering and user interactions.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
import re
from typing import Tuple, Optional
from pathlib import Path

# Import the debug view
from src.ui.debug_view import render_debug_info, render_ai_vision_info
# Import the agent history view
from src.ui.agent_history_view import render_agent_history

from src.config import (
    UI_TEXT, 
    BUTTON_LABELS, 
    STATUS_MESSAGES, 
    SESSION_KEYS,
    FRAMEWORK_EXTENSIONS
)


def display_status_message(message_type: str, message: str, **kwargs) -> None:
    """
    Display a status message to the user.
    
    Args:
        message_type: Type of message ('success', 'error', 'warning', 'info')
        message: The message to display
        **kwargs: Additional arguments for message formatting
    """
    formatted_message = message.format(**kwargs) if kwargs else message
    
    if message_type == "success":
        st.markdown(
            f'<div class="status-success">{formatted_message}</div>', 
            unsafe_allow_html=True
        )
    elif message_type == "error":
        st.markdown(
            f'<div class="status-error">{formatted_message}</div>', 
            unsafe_allow_html=True
        )
    elif message_type == "warning":
        st.markdown(
            f'<div class="status-warning">{formatted_message}</div>', 
            unsafe_allow_html=True
        )
    else:  # info or default
        st.markdown(
            f'<div class="status-info">{formatted_message}</div>', 
            unsafe_allow_html=True
        )


def show_execution_preview(steps: str) -> None:
    """
    Show a preview of the steps that will be executed.
    
    Args:
        steps: The steps to preview
    """
    st.markdown("### 🔍 Execution Preview")
    st.markdown("**The following Gherkin scenarios will be executed:**")
    with st.expander("Click to view scenarios", expanded=False):
        st.code(steps, language="gherkin")
    st.markdown("---")


def render_header():
    """Render the application header and title."""
    # Custom Header
    st.markdown(
        f'<div class="header fade-in"><span class="header-item">{UI_TEXT["header_text"]}</span></div>', 
        unsafe_allow_html=True
    )

    # Main Title with custom styling
    st.markdown(
        f'<h1 class="main-title fade-in">{UI_TEXT["main_title"]}</h1>', 
        unsafe_allow_html=True
    )
    st.markdown(
        f'<p class="subtitle fade-in">{UI_TEXT["subtitle"]}</p>', 
        unsafe_allow_html=True
    )


def render_user_story_input() -> str:
    """
    Render the user story input section.
    
    Returns:
        str: User input story
    """
    st.markdown('<div class="card fade-in">', unsafe_allow_html=True)
    st.markdown('<h3 class="glow-text">Enter User Story or Jira Ticket</h3>', unsafe_allow_html=True)
    
    # Check if Jira is configured
    jira_configured = (
        st.session_state.get("jira_server_url") and 
        st.session_state.get("jira_username") and 
        st.session_state.get("jira_token")
    )
    
    if jira_configured:
        st.markdown(
            '<p style="color: #4CAF50; font-size: 0.9em;">✅ Jira integration is configured. You can enter a Jira ticket number (e.g., PROJECT-123)</p>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<p style="color: #FF9800; font-size: 0.9em;">⚠️ Configure Jira credentials in the sidebar to enable Jira ticket integration</p>', 
            unsafe_allow_html=True
        )
    
    user_story = st.text_area(
        "Enter User Story or Jira Ticket",
        placeholder=UI_TEXT["user_story_placeholder"],
        label_visibility="hidden"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    return user_story


def render_action_buttons() -> Tuple[bool, bool, bool, bool, bool, bool]:
    """
    Render the main action buttons.
    
    Returns:
        Tuple of button states: (enhance, manual, gherkin, execute, generate, self_heal)
    """
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        enhance_story_btn = st.button(BUTTON_LABELS["enhance_story"])
    with col2:
        generate_manual_btn = st.button(BUTTON_LABELS["generate_manual"])
    with col3:
        generate_gherkin_btn = st.button(BUTTON_LABELS["generate_gherkin"])
    with col4:
        execute_btn = st.button(BUTTON_LABELS["execute_steps"])
    with col5:
        generate_code_btn = st.button(BUTTON_LABELS["generate_code"])
    with col6:
        self_healing_btn = st.button(BUTTON_LABELS["self_healing"])
    
    return (enhance_story_btn, generate_manual_btn, generate_gherkin_btn, 
            execute_btn, generate_code_btn, self_healing_btn)


def render_enhanced_story():
    """Render the enhanced user story section if available."""
    if (SESSION_KEYS["enhanced_user_story"] in st.session_state and 
        st.session_state[SESSION_KEYS["enhanced_user_story"]]):
        st.markdown('<div class="card code-container fade-in">', unsafe_allow_html=True)
        st.markdown('<h3 class="glow-text">Enhanced User Story</h3>', unsafe_allow_html=True)
        st.text_area(
            "Review and edit the enhanced user story:",
            value=st.session_state[SESSION_KEYS["enhanced_user_story"]],
            height=300,
            key="enhanced_user_story_editor"
        )
        st.markdown('</div>', unsafe_allow_html=True)


def render_manual_test_cases():
    """Render the manual test cases editor if available."""
    if (SESSION_KEYS["manual_test_cases"] in st.session_state and 
        st.session_state[SESSION_KEYS["manual_test_cases"]]):
        st.markdown('<div class="card code-container fade-in">', unsafe_allow_html=True)
        st.markdown('<h3 class="glow-text">Your Manual Test Cases</h3>', unsafe_allow_html=True)

        # Display editable dataframe
        edited_df = st.data_editor(
            pd.DataFrame(st.session_state[SESSION_KEYS["edited_manual_test_cases"]]),
            key="manual_test_case_editor",
            num_rows="dynamic"
        )

        # Save button for manual test cases
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button(BUTTON_LABELS["save_manual_changes"], key="save_manual_changes_btn"):
                st.session_state[SESSION_KEYS["edited_manual_test_cases"]] = edited_df.to_dict('records')
                st.session_state[SESSION_KEYS["manual_changes_saved"]] = True
                st.rerun()

        # Display save status for manual test cases
        with col2:
            if (SESSION_KEYS["manual_changes_saved"] in st.session_state and 
                st.session_state[SESSION_KEYS["manual_changes_saved"]]):
                st.markdown(
                    f'<div class="status-success" style="margin: 0;">{STATUS_MESSAGES["manual_changes_saved"]}</div>', 
                    unsafe_allow_html=True
                )
                st.session_state[SESSION_KEYS["manual_changes_saved"]] = False  # Reset the flag

        st.markdown('</div>', unsafe_allow_html=True)


def render_gherkin_scenarios():
    """Render the Gherkin scenarios editor if available."""
    if (SESSION_KEYS["edited_steps"] in st.session_state and 
        st.session_state[SESSION_KEYS["edited_steps"]]):
        st.markdown('<div class="card code-container fade-in">', unsafe_allow_html=True)
        st.markdown('<h3 class="glow-text">Your Gherkin Scenarios</h3>', unsafe_allow_html=True)

        # Display editable text area with the current edited steps
        edited_steps = st.text_area(
            "Edit scenarios if needed:",
            value=st.session_state[SESSION_KEYS["edited_steps"]],
            height=300,
            key="scenario_editor"
        )

        # Save button and status
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button(BUTTON_LABELS["save_changes"], key="save_changes_btn"):
                st.session_state[SESSION_KEYS["edited_steps"]] = edited_steps
                st.session_state[SESSION_KEYS["changes_saved"]] = True
                st.rerun()

        # Display save status
        with col2:
            if (SESSION_KEYS["changes_saved"] in st.session_state and 
                st.session_state[SESSION_KEYS["changes_saved"]]):
                st.markdown(
                    f'<div class="status-success" style="margin: 0;">{STATUS_MESSAGES["changes_saved"]}</div>', 
                    unsafe_allow_html=True
                )
                st.session_state[SESSION_KEYS["changes_saved"]] = False
            elif edited_steps != st.session_state[SESSION_KEYS["edited_steps"]]:
                st.markdown(
                    f'<div style="color: #FFA500; font-weight: bold;">{STATUS_MESSAGES["unsaved_changes"]}</div>', 
                    unsafe_allow_html=True
                )

        st.markdown('</div>', unsafe_allow_html=True)


def render_execution_results():
    """Render the test execution results if available."""
    if (SESSION_KEYS["history"] in st.session_state and 
        st.session_state[SESSION_KEYS["history"]]):
        history = st.session_state[SESSION_KEYS["history"]]
        
        # Display key information in tabs with more descriptive labels
        st.markdown('<div class="tab-container fade-in">', unsafe_allow_html=True)
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📊 Summary", 
            "⚡ Actions", 
            "🔍 Elements", 
            "📋 Details",
            "🔬 Debug",
            "👁️ AI Vision",
            "📜 Agent History"
        ])
        
        with tab1:
            _render_results_tab(history)
        
        with tab2:
            _render_actions_tab(history)
        
        with tab3:
            _render_elements_tab(history)
        
        with tab4:
            _render_details_tab(history)
            
        with tab5:
            render_debug_info(history)
            
        with tab6:
            render_ai_vision_info(history)
            
        with tab7:
            render_agent_history(history)
        
        st.markdown('</div>', unsafe_allow_html=True)


def _render_results_tab(history):
    """Render the Results tab content with enhanced information."""
    st.markdown('<h4 class="glow-text">📊 Execution Summary</h4>', unsafe_allow_html=True)
    
    # Execution status - filter out non-critical errors
    errors = history.get('errors', [])
    critical_errors = []
    warnings = []
    
    # Filter errors - treat empty or informational messages as warnings
    if errors:
        for error in errors:
            error_str = str(error).lower()
            # Check if it's a critical error or just informational
            if any(keyword in error_str for keyword in ['failed', 'error', 'exception', 'timeout', 'invalid', 'not found']):
                critical_errors.append(error)
            else:
                warnings.append(error)
    
    if critical_errors:
        st.error("❌ Execution completed with errors")
        for error in critical_errors:
            st.markdown(f"<div style='background-color: #ffe6e6; padding: 10px; border-radius: 5px; margin: 5px 0;'><strong>Error:</strong> {error}</div>", unsafe_allow_html=True)
        # Show warnings separately if they exist
        if warnings:
            st.warning("⚠️ Warnings during execution")
            for warning in warnings:
                st.markdown(f"<div style='background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 5px 0;'><strong>Warning:</strong> {warning}</div>", unsafe_allow_html=True)
    else:
        st.success("✅ Test execution completed successfully!")
        # Show warnings if they exist but no critical errors
        if warnings:
            st.info("ℹ️ Execution completed with warnings")
            for warning in warnings:
                st.markdown(f"<div style='background-color: #d1ecf1; padding: 10px; border-radius: 5px; margin: 5px 0;'><strong>Info:</strong> {warning}</div>", unsafe_allow_html=True)
    
    # Key metrics with enhanced visualization
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        urls_count = len(history.get('urls', []))
        st.metric("🌐 URLs Visited", urls_count)
    with col2:
        actions_count = len(history.get('action_names', []))
        st.metric("⚡ Actions Performed", actions_count)
    with col3:
        elements_count = len(history.get('element_xpaths', {}))
        st.metric("🔍 Elements Interacted", elements_count)
    with col4:
        # Check for element interactions data
        element_interactions_count = 0
        if 'element_interactions' in history and history['element_interactions']:
            element_interactions_count = history['element_interactions'].get('total_interactions', 0)
        st.metric("🎯 Element Events", element_interactions_count)
    
    # Enhanced execution timeline
    if 'urls' in history and history['urls']:
        st.markdown('<h5 class="glow-text">🧭 Execution Timeline</h5>', unsafe_allow_html=True)
        
        # Create a timeline of events
        timeline_events = []
        
        # Add URL visits
        for i, url in enumerate(history['urls'], 1):
            timeline_events.append({
                "time": f"Step {i}",
                "event": "🌐 URL Visited",
                "details": url
            })
        
        # Add actions if available
        action_names = history.get('action_names', [])
        for i, action in enumerate(action_names, len(history['urls']) + 1):
            timeline_events.append({
                "time": f"Step {i}",
                "event": "⚡ Action Performed",
                "details": action
            })
        
        # Display timeline
        for event in timeline_events:
            st.markdown(f"""
            <div style='display: flex; align-items: center; margin: 8px 0; padding: 10px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #4CAF50;'>
                <div style='min-width: 100px; font-weight: bold; color: #666;'>{event['time']}</div>
                <div style='min-width: 150px; font-weight: bold; color: #333;'>{event['event']}</div>
                <div style='flex-grow: 1; color: #555;'>{event['details']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Enhanced metrics from browser-use features
    st.markdown('<h5 class="glow-text">📈 Execution Metrics</h5>', unsafe_allow_html=True)
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        duration = history.get('total_duration', 0)
        st.metric("⏱️ Duration (s)", f"{duration:.2f}")
    with metric_col2:
        steps = history.get('number_of_steps', 0)
        st.metric("🔢 Steps", steps)
    with metric_col3:
        # Calculate actions per second
        if duration > 0:
            actions_per_second = actions_count / duration
            st.metric("⚡ Actions/sec", f"{actions_per_second:.2f}")
        else:
            st.metric("⚡ Actions/sec", "N/A")
    with metric_col4:
        # Show execution status
        is_successful = history.get('is_successful', None)
        if is_successful is True:
            st.metric("✅ Status", "Success")
        elif is_successful is False:
            st.metric("❌ Status", "Failed")
        else:
            st.metric("⏳ Status", "Unknown")
    
    # Browser-use features summary
    st.markdown('<h5 class="glow-text">🚀 Browser-Use Features Utilized</h5>', unsafe_allow_html=True)
    
    feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4)
    
    with feature_col1:
        gif_path = history.get('gif_path')
        if gif_path and Path(gif_path).exists():
            st.markdown("<div style='background-color: #e8f5e9; padding: 10px; border-radius: 8px; text-align: center;'><h3>🎥</h3><p>GIF Generated</p></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #ffebee; padding: 10px; border-radius: 8px; text-align: center;'><h3>🎥</h3><p>GIF Not Generated</p></div>", unsafe_allow_html=True)
    
    with feature_col2:
        screenshots = history.get('screenshots', [])
        if screenshots:
            st.markdown(f"<div style='background-color: #e3f2fd; padding: 10px; border-radius: 8px; text-align: center;'><h3>📸</h3><p>{len(screenshots)} Screenshots</p></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #ffebee; padding: 10px; border-radius: 8px; text-align: center;'><h3>📸</h3><p>No Screenshots</p></div>", unsafe_allow_html=True)
    
    with feature_col3:
        use_vision = history.get('vision_details') is not None
        if use_vision:
            st.markdown("<div style='background-color: #fff3e0; padding: 10px; border-radius: 8px; text-align: center;'><h3>👁️</h3><p>AI Vision Used</p></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #ffebee; padding: 10px; border-radius: 8px; text-align: center;'><h3>👁️</h3><p>Vision Not Used</p></div>", unsafe_allow_html=True)
    
    with feature_col4:
        highlight_elements = True  # This is enabled in config
        if highlight_elements:
            st.markdown("<div style='background-color: #f3e5f5; padding: 10px; border-radius: 8px; text-align: center;'><h3>✨</h3><p>Elements Highlighted</p></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #ffebee; padding: 10px; border-radius: 8px; text-align: center;'><h3>✨</h3><p>No Highlighting</p></div>", unsafe_allow_html=True)
    
    # Visualizations
    st.markdown('<h5 class="glow-text">📊 Execution Visualization</h5>', unsafe_allow_html=True)
    
    # Create a simple bar chart of actions over time
    action_names = history.get('action_names', [])
    if action_names:
        action_counts = {}
        for action in action_names:
            action_type = action.split()[0] if action else "Unknown"
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
        
        if action_counts:
            # Convert to lists for matplotlib
            action_types = list(action_counts.keys())
            counts = list(action_counts.values())
            
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(action_types, counts, color='#4CAF50')
            ax.set_xlabel('Action Types')
            ax.set_ylabel('Count')
            ax.set_title('Action Distribution')
            plt.xticks(rotation=45)
            st.pyplot(fig)
    
    # Execution date
    if 'execution_date' in history:
        st.markdown(f"<p style='color: #666; font-size: 0.9em; text-align: right;'><strong>Executed on:</strong> {history['execution_date']}</p>", unsafe_allow_html=True)


def _render_actions_tab(history):
    """Render the Actions tab content with detailed action information."""
    st.markdown('<h4 class="glow-text">⚡ Actions Performed</h4>', unsafe_allow_html=True)
    
    detailed_actions = history.get('detailed_actions', [])
    action_names = history.get('action_names', [])
    
    if detailed_actions:
        st.markdown(f"<p style='color: #666;'><strong>Total Actions:</strong> {len(detailed_actions)}</p>", unsafe_allow_html=True)
        
        # Create a timeline of actions with enhanced visualization
        for i, action in enumerate(detailed_actions):
            action_name = action.get('name', 'Unknown Action')
            element_details = action.get('element_details', {})
            
            # Create a card for each action with enhanced styling
            st.markdown(f"""
            <div style='background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #FF9800; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <h5 style='margin: 0; color: #333;'>Step {i+1}: {action_name}</h5>
                    <span style='background-color: #2196F3; color: white; padding: 3px 8px; border-radius: 12px; font-size: 0.8em;'>
                        Action
                    </span>
                </div>
            """, unsafe_allow_html=True)
            
            # Show element details if available
            if element_details:
                # Show element identification information
                if 'element_index' in element_details:
                    st.markdown(f"<p style='margin: 5px 0; color: #2196F3;'><strong>Element Index:</strong> {element_details['element_index']}</p>", unsafe_allow_html=True)
                
                # Show element attributes
                if 'tag_name' in element_details:
                    st.markdown(f"<p style='margin: 5px 0; color: #9C27B0;'><strong>Tag:</strong> &lt;{element_details['tag_name']}&gt;</p>", unsafe_allow_html=True)
                
                # Show meaningful text
                if 'meaningful_text' in element_details and element_details['meaningful_text']:
                    st.markdown(f"<p style='margin: 5px 0; color: #4CAF50;'><strong>Text:</strong> {element_details['meaningful_text']}</p>", unsafe_allow_html=True)
                
                # Show ID if available
                if 'id' in element_details and element_details['id']:
                    st.markdown(f"<p style='margin: 5px 0; color: #FF5722;'><strong>ID:</strong> {element_details['id']}</p>", unsafe_allow_html=True)
                
                # Show action-specific metadata
                metadata = action.get('metadata', {})
                if metadata:
                    st.markdown("<p style='margin: 5px 0; color: #607D8B; font-weight: bold;'>Metadata:</p>", unsafe_allow_html=True)
                    for key, value in metadata.items():
                        st.markdown(f"<p style='margin: 2px 0 2px 20px; color: #607D8B;'><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
    elif action_names:
        st.markdown(f"<p style='color: #666;'><strong>Total Actions:</strong> {len(action_names)}</p>", unsafe_allow_html=True)
        # Create a more visually appealing list of actions
        for i, action_name in enumerate(action_names):
            st.markdown(f"""
            <div style='background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #FF9800; display: flex; align-items: center;'>
                <div style='background-color: #FF9800; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-weight: bold;'>{i+1}</div>
                <strong>{action_name}</strong>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No detailed actions were captured during test execution.")


def _render_elements_tab(history):
    """Render the Elements tab content with comprehensive element information."""
    st.markdown('<h4 class="glow-text">🔍 Element Details</h4>', unsafe_allow_html=True)
    
    # Check for comprehensive element tracking data
    if 'element_interactions' in history and history['element_interactions']:
        element_data = history['element_interactions']
        
        # Summary metrics with enhanced visualization
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🎯 Total Interactions", element_data.get('total_interactions', 0))
        with col2:
            st.metric("🧩 Unique Elements", element_data.get('unique_elements', 0))
        with col3:
            action_types = element_data.get('action_types', [])
            st.metric("⚡ Action Types", len(action_types))
        with col4:
            # Calculate selector coverage
            automation_data = element_data.get('automation_data', {})
            framework_selectors = automation_data.get('framework_selectors', {})
            st.metric("🔧 Selector Types", len(framework_selectors))
        
        # Action types visualization
        if action_types:
            st.markdown(f"<p style='color: #666; margin-top: 15px;'><strong>Action Types:</strong> {', '.join(action_types)}</p>", unsafe_allow_html=True)
        
        # Element library with enhanced visualization
        if 'automation_data' in element_data and 'element_library' in element_data['automation_data']:
            element_library = element_data['automation_data']['element_library']
            if element_library:
                st.markdown('<h5 class="glow-text">🧩 Element Library</h5>', unsafe_allow_html=True)
                
                # Create tabs for different views
                element_tab1, element_tab2, element_tab3 = st.tabs(["📋 Table View", "📊 Visualization", "🔍 Detailed View"])
                
                with element_tab1:
                    # Create a dataframe for better visualization
                    element_list = []
                    for element_key, element_info in element_library.items():
                        element_list.append({
                            "Element": element_key,
                            "Tag": element_info.get('tag_name', 'N/A'),
                            "Text": element_info.get('meaningful_text', '')[:30] + "..." if len(element_info.get('meaningful_text', '')) > 30 else element_info.get('meaningful_text', 'N/A'),
                            "Interactions": element_info.get('interactions_count', 0),
                            "ID": element_info.get('attributes', {}).get('id', 'N/A'),
                            "Class": element_info.get('attributes', {}).get('class', 'N/A')[:20] + "..." if len(element_info.get('attributes', {}).get('class', '')) > 20 else element_info.get('attributes', {}).get('class', 'N/A')
                        })
                    
                    element_df = pd.DataFrame(element_list)
                    st.dataframe(element_df, use_container_width=True, height=300)
                
                with element_tab2:
                    # Create a visualization of element interactions
                    st.markdown("### 📊 Element Interaction Overview")
                    
                    # Show interaction counts by element
                    interaction_counts = {element_key: element_info.get('interactions_count', 0) 
                                        for element_key, element_info in element_library.items()}
                    
                    if interaction_counts:
                        fig, ax = plt.subplots(figsize=(10, 5))
                        elements = list(interaction_counts.keys())
                        counts = list(interaction_counts.values())
                        ax.bar(elements, counts, color='#2196F3')
                        ax.set_xlabel('Elements')
                        ax.set_ylabel('Interaction Count')
                        ax.set_title('Element Interaction Frequency')
                        plt.xticks(rotation=45)
                        st.pyplot(fig)
                    
                    # Show selector reliability
                    st.markdown("### 🎯 Selector Reliability")
                    reliability_data = []
                    for element_key, element_info in element_library.items():
                        selectors = element_info.get('selectors', {})
                        reliability_score = len(selectors)  # Simple score based on number of selectors
                        reliability_data.append({
                            "Element": element_key,
                            "Reliability Score": reliability_score,
                            "Tag": element_info.get('tag_name', 'N/A')
                        })
                    
                    reliability_df = pd.DataFrame(reliability_data)
                    st.dataframe(reliability_df, use_container_width=True)
                
                with element_tab3:
                    # Detailed view of each element
                    st.markdown("### 📋 Detailed Element Information")
                    for element_key, element_info in element_library.items():
                        with st.expander(f"{element_key} - {element_info.get('tag_name', 'N/A')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"<p><strong>Tag Name:</strong> {element_info.get('tag_name', 'N/A')}</p>", unsafe_allow_html=True)
                                st.markdown(f"<p><strong>Text:</strong> {element_info.get('meaningful_text', 'N/A')}</p>", unsafe_allow_html=True)
                                st.markdown(f"<p><strong>Interactions:</strong> {element_info.get('interactions_count', 0)}</p>", unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown(f"<p><strong>ID:</strong> {element_info.get('attributes', {}).get('id', 'N/A')}</p>", unsafe_allow_html=True)
                                st.markdown(f"<p><strong>Name:</strong> {element_info.get('attributes', {}).get('name', 'N/A')}</p>", unsafe_allow_html=True)
                                st.markdown(f"<p><strong>Type:</strong> {element_info.get('attributes', {}).get('type', 'N/A')}</p>", unsafe_allow_html=True)
                            
                            # Show position information
                            position = element_info.get('position', {})
                            if position:
                                st.markdown(f"<p><strong>Position:</strong> X: {position.get('x', 'N/A')}, Y: {position.get('y', 'N/A')}, Width: {position.get('width', 'N/A')}, Height: {position.get('height', 'N/A')}</p>", unsafe_allow_html=True)
                            
                            # Show selectors
                            if 'selectors' in element_info and element_info['selectors']:
                                st.markdown("<h6>Selectors</h6>", unsafe_allow_html=True)
                                selectors = element_info['selectors']
                                
                                # Categorize selectors by reliability
                                st.markdown("<p><strong>🥇 High Reliability Selectors:</strong></p>", unsafe_allow_html=True)
                                high_reliability = [
                                    ('ID', selectors.get('id')),
                                    ('Data-testid', selectors.get('data_testid')),
                                    ('Name', selectors.get('name'))
                                ]
                                for selector_name, selector_value in high_reliability:
                                    if selector_value:
                                        st.markdown(f"<div style='background-color: #e8f5e9; padding: 5px; margin: 2px 0; border-radius: 3px; display: flex; justify-content: space-between;'><span><strong>{selector_name}:</strong></span> <span style='font-family: monospace; color: #2e7d32;'>{selector_value}</span></div>", unsafe_allow_html=True)
                                
                                st.markdown("<p><strong>🥈 Medium Reliability Selectors:</strong></p>", unsafe_allow_html=True)
                                medium_reliability = [
                                    ('CSS Selector', selectors.get('css_id')),
                                    ('XPath', selectors.get('xpath_id')),
                                    ('CSS Class', selectors.get('css_class'))
                                ]
                                for selector_name, selector_value in medium_reliability:
                                    if selector_value:
                                        st.markdown(f"<div style='background-color: #fff8e1; padding: 5px; margin: 2px 0; border-radius: 3px; display: flex; justify-content: space-between;'><span><strong>{selector_name}:</strong></span> <span style='font-family: monospace; color: #f57f17;'>{selector_value}</span></div>", unsafe_allow_html=True)
                                
                                st.markdown("<p><strong>🥉 Low Reliability Selectors:</strong></p>", unsafe_allow_html=True)
                                low_reliability = [
                                    ('Index-based', selectors.get('index_based')),
                                    ('Text-based', selectors.get('xpath_text'))
                                ]
                                for selector_name, selector_value in low_reliability:
                                    if selector_value:
                                        st.markdown(f"<div style='background-color: #ffebee; padding: 5px; margin: 2px 0; border-radius: 3px; display: flex; justify-content: space-between;'><span><strong>{selector_name}:</strong></span> <span style='font-family: monospace; color: #c62828;'>{selector_value}</span></div>", unsafe_allow_html=True)
            else:
                st.info("No elements were captured in the element library.")
        else:
            # Fallback to basic element information
            element_xpath_map = history.get('element_xpaths', {})
            if element_xpath_map:
                st.markdown('<h5 class="glow-text">🔗 Element XPaths</h5>', unsafe_allow_html=True)
                # Create a dataframe for better visualization
                element_df = pd.DataFrame([
                    {"Element Index": index, "XPath": xpath}
                    for index, xpath in element_xpath_map.items()
                ])
                st.dataframe(element_df, use_container_width=True)
            else:
                st.info("No element XPaths were captured during test execution.")
    else:
        # Fallback to basic element information
        element_xpath_map = history.get('element_xpaths', {})
        if element_xpath_map:
            st.markdown('<h5 class="glow-text">🔗 Element XPaths</h5>', unsafe_allow_html=True)
            # Create a dataframe for better visualization
            element_df = pd.DataFrame([
                {"Element Index": index, "XPath": xpath}
                for index, xpath in element_xpath_map.items()
            ])
            st.dataframe(element_df, use_container_width=True)
        else:
            st.info("No element information was captured during test execution.")


def _render_details_tab(history):
    """Render the Details tab content with comprehensive extracted information."""
    st.markdown('<h4 class="glow-text">📋 Extracted Content & Details</h4>', unsafe_allow_html=True)
    
    # Check for comprehensive element tracking data
    if 'element_interactions' in history and history['element_interactions']:
        element_data = history['element_interactions']
        
        # Create tabs for different types of details
        detail_tab1, detail_tab2, detail_tab3, detail_tab4 = st.tabs(["⚙️ Automation Data", "📄 Extracted Content", "🔧 Debug Info", "🚀 Framework Exports"])
        
        with detail_tab1:
            st.markdown('<h5 class="glow-text">Automation Framework Information</h5>', unsafe_allow_html=True)
            
            # Show framework exports
            if 'framework_exports' in history and history['framework_exports']:
                framework_exports = history['framework_exports']
                st.markdown('<p style="color: #666;"><strong>Available for these frameworks:</strong></p>', unsafe_allow_html=True)
                frameworks = list(framework_exports.keys())
                cols = st.columns(len(frameworks))
                for i, fw in enumerate(frameworks):
                    with cols[i]:
                        st.markdown(f"<div style='background-color: #e3f2fd; padding: 10px; border-radius: 8px; text-align: center;'><strong>{fw.capitalize()}</strong></div>", unsafe_allow_html=True)
            
            # Show selector coverage with enhanced visualization
            if 'automation_data' in element_data and 'framework_selectors' in element_data['automation_data']:
                selectors = element_data['automation_data']['framework_selectors']
                st.markdown(f"<p style='color: #666; margin-top: 15px;'><strong>Selector Coverage:</strong> {len(selectors)} different selector types captured</p>", unsafe_allow_html=True)
                
                # Show selector statistics
                selector_stats = {}
                for selector_type, elements in selectors.items():
                    selector_stats[selector_type] = len(elements)
                
                # Create a dataframe for selector statistics
                stats_df = pd.DataFrame([
                    {"Selector Type": selector_type, "Elements Covered": count}
                    for selector_type, count in selector_stats.items()
                ])
                st.dataframe(stats_df, use_container_width=True)
                
                # Show priority selectors with categorization
                st.markdown('<h6>Priority Selectors (Categorized by Reliability)</h6>', unsafe_allow_html=True)
                
                # High reliability selectors
                st.markdown("<p><strong>🥇 High Reliability Selectors:</strong></p>", unsafe_allow_html=True)
                high_reliability = ['id', 'data_testid', 'name']
                for selector_type in high_reliability:
                    if selector_type in selectors:
                        with st.expander(f"{selector_type.upper()} Selectors ({len(selectors[selector_type])} elements)"):
                            for element_key, selector_value in selectors[selector_type].items():
                                st.markdown(f"<div style='background-color: #e8f5e9; padding: 5px; margin: 2px 0; border-radius: 3px; display: flex; justify-content: space-between;'><span>{element_key}:</span> <span style='font-family: monospace; color: #2e7d32;'>{selector_value}</span></div>", unsafe_allow_html=True)
                
                # Medium reliability selectors
                st.markdown("<p><strong>🥈 Medium Reliability Selectors:</strong></p>", unsafe_allow_html=True)
                medium_reliability = ['css_id', 'xpath_id', 'css_class']
                for selector_type in medium_reliability:
                    if selector_type in selectors:
                        with st.expander(f"{selector_type.upper()} Selectors ({len(selectors[selector_type])} elements)"):
                            for element_key, selector_value in selectors[selector_type].items():
                                st.markdown(f"<div style='background-color: #fff8e1; padding: 5px; margin: 2px 0; border-radius: 3px; display: flex; justify-content: space-between;'><span>{element_key}:</span> <span style='font-family: monospace; color: #f57f17;'>{selector_value}</span></div>", unsafe_allow_html=True)
                
                # Low reliability selectors
                st.markdown("<p><strong>🥉 Low Reliability Selectors:</strong></p>", unsafe_allow_html=True)
                low_reliability = ['index_based', 'xpath_text']
                for selector_type in low_reliability:
                    if selector_type in selectors:
                        with st.expander(f"{selector_type.upper()} Selectors ({len(selectors[selector_type])} elements)"):
                            for element_key, selector_value in selectors[selector_type].items():
                                st.markdown(f"<div style='background-color: #ffebee; padding: 5px; margin: 2px 0; border-radius: 3px; display: flex; justify-content: space-between;'><span>{element_key}:</span> <span style='font-family: monospace; color: #c62828;'>{selector_value}</span></div>", unsafe_allow_html=True)
        
        with detail_tab2:
            # Extracted content
            extracted_content = history.get('extracted_content', [])
            if extracted_content:
                st.markdown('<h5 class="glow-text">📄 Extracted Content</h5>', unsafe_allow_html=True)
                for i, content in enumerate(extracted_content, 1):
                    st.markdown(f"<div style='background-color: #fff8e1; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid #FF9800;'><strong>Content {i}:</strong><br>{content}</div>", unsafe_allow_html=True)
            else:
                st.info("No content was extracted during execution.")
            
            # Show screenshots if available
            screenshots = history.get('screenshots', [])
            if screenshots:
                st.markdown('<h5 class="glow-text">📸 Execution Screenshots</h5>', unsafe_allow_html=True)
                st.info("Screenshots are captured during execution for debugging and analysis.")
                
                # Show GIF if available
                gif_path = history.get('gif_path')
                if gif_path and Path(gif_path).exists():
                    st.markdown('<h6>🎥 Execution GIF</h6>', unsafe_allow_html=True)
                    st.info("A GIF animation of the execution is available for review.")
                    # Display the GIF here
                    st.image(gif_path, caption="Execution Animation", use_container_width=True)
        
        with detail_tab3:
            # Raw model actions for debugging
            model_actions = history.get('model_actions', [])
            if model_actions:
                st.markdown('<h5 class="glow-text">🔧 Raw Model Actions</h5>', unsafe_allow_html=True)
                for i, action_data in enumerate(model_actions):
                    action_name = history.get('action_names', [])[i] if i < len(history.get('action_names', [])) else 'Unknown'
                    with st.expander(f"Action {i}: {action_name}"):
                        st.json(action_data)
            else:
                st.info("No raw model actions available.")
                
            # Show action sequence if available
            if 'automation_data' in element_data and 'action_sequence' in element_data['automation_data']:
                action_sequence = element_data['automation_data']['action_sequence']
                st.markdown('<h5 class="glow-text">🎬 Action Sequence</h5>', unsafe_allow_html=True)
                for action in action_sequence:
                    with st.expander(f"Step {action['step_number']}: {action['action_type']} on {action['element_context'].get('tag_name', 'N/A')}"):
                        st.json(action)
        
        with detail_tab4:
            # Framework exports
            st.markdown('<h5 class="glow-text">🚀 Framework Export Options</h5>', unsafe_allow_html=True)
            
            if 'framework_exports' in history and history['framework_exports']:
                framework_exports = history['framework_exports']
                
                # Create tabs for each framework
                framework_tabs = st.tabs([fw.capitalize() for fw in framework_exports.keys()])
                
                for i, (fw, export_data) in enumerate(framework_exports.items()):
                    with framework_tabs[i]:
                        st.markdown(f"<h6>{fw.capitalize()} Export</h6>", unsafe_allow_html=True)
                        
                        # Show setup data
                        if 'setup_data' in export_data and export_data['setup_data']:
                            st.markdown("<p><strong>Required Imports:</strong></p>", unsafe_allow_html=True)
                            for imp in export_data['setup_data'].get('required_imports', []):
                                st.code(imp, language='python')
                        
                        # Show test steps
                        if 'test_steps' in export_data and export_data['test_steps']:
                            st.markdown("<p><strong>Test Steps:</strong></p>", unsafe_allow_html=True)
                            for step in export_data['test_steps']:
                                st.markdown(f"<div style='background-color: #f1f8e9; padding: 8px; border-radius: 4px; margin: 5px 0; border-left: 3px solid #8bc34a;'><strong>{step.get('description', '')}</strong><br><code>{step.get('code', '')}</code></div>", unsafe_allow_html=True)
                        
                        # Show page objects
                        if 'page_objects' in export_data and export_data['page_objects']:
                            st.markdown("<p><strong>Page Objects:</strong></p>", unsafe_allow_html=True)
                            for page_name, page_data in export_data['page_objects'].items():
                                with st.expander(f"Page: {page_name}"):
                                    st.code(page_data.get('code', ''), language='python')
            else:
                st.info("Framework exports are generated after successful execution.")
    else:
        st.info("Detailed execution data is available after running test scenarios.")


def render_generated_code(selected_framework: str) -> None:
    """
    Render the generated automation code if available.
    
    Args:
        selected_framework: The selected testing framework
    """
    if (SESSION_KEYS["automation_code"] in st.session_state and 
        st.session_state[SESSION_KEYS["automation_code"]]):
        st.markdown('<div class="card code-container fade-in">', unsafe_allow_html=True)
        st.markdown('<h3 class="glow-text">Your Generated Automation Code</h3>', unsafe_allow_html=True)
        
        # Get the code and language
        code = st.session_state[SESSION_KEYS["automation_code"]]
        language = _get_code_language(selected_framework)
        
        # Display the code
        st.code(code, language=language)
        
        # Add download button
        _render_download_button(code, selected_framework)
        
        st.markdown('</div>', unsafe_allow_html=True)


def _get_code_language(framework: str) -> str:
    """
    Get the appropriate language for syntax highlighting based on framework.
    
    Args:
        framework: The selected testing framework
        
    Returns:
        str: The language identifier for syntax highlighting
    """
    language_map = {
        "Selenium + PyTest BDD (Python)": "python",
        "Playwright (Python)": "python",
        "Cypress (JavaScript)": "javascript",
        "Robot Framework": "robotframework",
        "Selenium + Cucumber (Java)": "java"
    }
    return language_map.get(framework, "python")


def _render_download_button(code: str, framework: str) -> None:
    """
    Render a download button for the generated code.
    
    Args:
        code: The code to download
        framework: The selected testing framework
    """
    # Get file extension
    extension = FRAMEWORK_EXTENSIONS.get(framework, "txt")
    
    # Create download link
    st.download_button(
        label="📥 Download Code",
        data=code,
        file_name=f"automation_test.{extension}",
        mime="text/plain"
    )


def render_footer() -> None:
    """Render the application footer."""
    st.markdown(
        f'<div class="footer">{UI_TEXT["footer_text"]}</div>', 
        unsafe_allow_html=True
    )
