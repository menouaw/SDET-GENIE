"""
Business logic handlers for SDET-GENIE application.
Contains all the handler functions for button clicks and agent calls.
"""

import asyncio
import pandas as pd
import streamlit as st
import os
from typing import Dict, Any

from src.Prompts.agno_prompts import (
    enhance_user_story,
    generate_manual_test_cases,
    generate_gherkin_scenarios
)
from src.logic.browser_executor import execute_test
from src.logic.model_factory import get_llm_instance
from src.config import (
    SESSION_KEYS, 
    STATUS_MESSAGES, 
    FRAMEWORK_GENERATORS,
    APP_CONFIG
)
from src.ui.main_view import display_status_message, show_execution_preview
from src.Agents.agents import user_story_enhancement_agent


def handle_enhance_story(user_story: str) -> None:
    """
    Handle user story enhancement.
    
    Args:
        user_story: The raw user story to enhance
    """
    if not user_story:
        display_status_message("error", "Please enter a user story first.")
        return
    
    with st.spinner("Enhancing user story..."):
        try:
            # Get the selected provider and model from session state
            provider = st.session_state.get('selected_provider', 'Google')
            model = st.session_state.get('selected_model', 'gemini-2.0-flash')
            
            # Create the agno model instance
            agno_llm = get_llm_instance(provider, model, for_agno=True)
            
            if agno_llm:
                # Configure Jira tools with credentials from session state
                jira_server_url = st.session_state.get("jira_server_url", "")
                jira_username = st.session_state.get("jira_username", "")
                jira_token = st.session_state.get("jira_token", "")
                
                # Initialize Jira tools for the agent
                _initialize_jira_tools(user_story_enhancement_agent, jira_server_url, jira_username, jira_token)
                
                # Call the user story enhancement agent
                enhanced_user_story = enhance_user_story(user_story, agno_llm)
                st.session_state[SESSION_KEYS["enhanced_user_story"]] = enhanced_user_story
                display_status_message("success", STATUS_MESSAGES["story_enhanced"])
            else:
                display_status_message("error", "Failed to initialize the model. Please check your API keys.")
        except Exception as e:
            display_status_message("error", f"Error enhancing user story: {str(e)}")


def handle_generate_manual_tests() -> None:
    """Handle manual test case generation."""
    if SESSION_KEYS["enhanced_user_story"] not in st.session_state:
        display_status_message("error", STATUS_MESSAGES["enhance_first"])
        return
    
    with st.spinner("Generating manual test cases..."):
        try:
            # Get the selected provider and model from session state
            provider = st.session_state.get('selected_provider', 'Google')
            model = st.session_state.get('selected_model', 'gemini-2.0-flash')
            
            # Create the agno model instance
            agno_llm = get_llm_instance(provider, model, for_agno=True)
            
            if agno_llm:
                # Call the manual test case generation function with the enhanced user story
                manual_test_cases_markdown = generate_manual_test_cases(
                    st.session_state[SESSION_KEYS["enhanced_user_story"]],
                    agno_llm
                )

                # Parse the markdown table into a pandas DataFrame
                manual_test_cases_data = _parse_manual_test_cases(manual_test_cases_markdown)
                
                if manual_test_cases_data:
                    st.session_state[SESSION_KEYS["manual_test_cases"]] = manual_test_cases_data
                    st.session_state[SESSION_KEYS["edited_manual_test_cases"]] = manual_test_cases_data
                    display_status_message("success", STATUS_MESSAGES["manual_generated"])
                else:
                    display_status_message("error", STATUS_MESSAGES["parse_error"])
                    st.write("Agent Output:", manual_test_cases_markdown)  # Display for debugging
            else:
                display_status_message("error", "Failed to initialize the model. Please check your API keys.")
                
        except Exception as e:
            display_status_message("error", f"Error generating manual test cases: {str(e)}")


def handle_generate_gherkin() -> None:
    """Handle Gherkin scenario generation."""
    if SESSION_KEYS["edited_manual_test_cases"] not in st.session_state:
        display_status_message("error", STATUS_MESSAGES["generate_manual_first"])
        return
    
    with st.spinner("Generating Gherkin scenarios from manual test cases..."):
        try:
            # Get the selected provider and model from session state
            provider = st.session_state.get('selected_provider', 'Google')
            model = st.session_state.get('selected_model', 'gemini-2.0-flash')
            
            # Create the agno model instance
            agno_llm = get_llm_instance(provider, model, for_agno=True)
            
            if agno_llm:
                # Convert the list of dicts back to a readable format for the agent
                manual_test_cases_text = ""
                if st.session_state[SESSION_KEYS["edited_manual_test_cases"]]:
                    manual_test_cases_text = pd.DataFrame(
                        st.session_state[SESSION_KEYS["edited_manual_test_cases"]]
                    ).to_markdown(index=False)

                generated_steps = generate_gherkin_scenarios(manual_test_cases_text or "", agno_llm)

                # Initialize both generated_steps and edited_steps in session state
                st.session_state[SESSION_KEYS["generated_steps"]] = generated_steps
                st.session_state[SESSION_KEYS["edited_steps"]] = generated_steps

                display_status_message("success", STATUS_MESSAGES["gherkin_generated"])
            else:
                display_status_message("error", "Failed to initialize the model. Please check your API keys.")
            
        except Exception as e:
            display_status_message("error", f"Error generating Gherkin scenarios: {str(e)}")


def handle_execute_steps() -> None:
    """Handle test step execution."""
    if SESSION_KEYS["edited_steps"] not in st.session_state:
        display_status_message("error", STATUS_MESSAGES["generate_gherkin_first"])
        return
    
    # Check if there are unsaved changes and warn the user
    if (_has_unsaved_scenario_changes()):
        st.warning(STATUS_MESSAGES["unsaved_warning"])
        return
    
    with st.spinner("Executing test steps..."):
        try:
            # Display the scenarios that will be executed
            steps_to_execute = st.session_state[SESSION_KEYS["edited_steps"]]
            show_execution_preview(steps_to_execute)

            # Set execution date
            st.session_state[SESSION_KEYS["execution_date"]] = APP_CONFIG["execution_date"]
            
            # Execute the test asynchronously
            asyncio.run(execute_test(steps_to_execute))
            
        except Exception as e:
            display_status_message(
                "error", 
                STATUS_MESSAGES["execution_error"],
                error=str(e)
            )


def handle_generate_code(selected_framework: str) -> None:
    """
    Handle automation code generation.
    
    Args:
        selected_framework: The selected testing framework
    """
    if (SESSION_KEYS["edited_steps"] not in st.session_state or 
        SESSION_KEYS["history"] not in st.session_state):
        display_status_message("error", STATUS_MESSAGES["execute_first"])
        return
    
    with st.spinner(f"Generating {selected_framework} automation code..."):
        try:
            # Get the selected provider and model from session state
            provider = st.session_state.get('selected_provider', 'Google')
            model = st.session_state.get('selected_model', 'gemini-2.0-flash')
            
            # Create the agno model instance
            agno_llm = get_llm_instance(provider, model, for_agno=True)
            
            if agno_llm:
                # Get the appropriate generator function
                generator_function = FRAMEWORK_GENERATORS[selected_framework]

                # Generate automation code using the edited steps
                automation_code = generator_function(
                    st.session_state[SESSION_KEYS["edited_steps"]],
                    st.session_state[SESSION_KEYS["history"]],
                    agno_llm
                )

                # Store in session state
                st.session_state[SESSION_KEYS["automation_code"]] = automation_code

                display_status_message("success", STATUS_MESSAGES["code_generated"])
            else:
                display_status_message("error", "Failed to initialize the model. Please check your API keys.")

        except Exception as e:
            display_status_message(
                "error", 
                STATUS_MESSAGES["generation_error"],
                framework=selected_framework,
                error=str(e)
            )


def handle_self_healing() -> None:
    """Handle self-healing functionality (placeholder for future implementation)."""
    st.info("Self-healing functionality is coming soon!")


def initialize_session_state() -> None:
    """Initialize session state variables if they don't exist."""
    # Only initialize boolean flags and execution date
    # Don't initialize content keys with empty values as this triggers UI rendering
    essential_defaults = {
        SESSION_KEYS["changes_saved"]: False,
        SESSION_KEYS["manual_changes_saved"]: False,
        SESSION_KEYS["execution_date"]: APP_CONFIG["execution_date"]
    }
    
    for key, default_value in essential_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def _initialize_jira_tools(agent, jira_server_url: str, jira_username: str, jira_token: str):
    """
    Initialize Jira tools for the agent based on provided credentials or environment variables.
    
    Args:
        agent: The agent to initialize tools for
        jira_server_url: Jira server URL from UI
        jira_username: Jira username from UI
        jira_token: Jira token from UI
    """
    try:
        # Prefer UI-provided credentials over environment variables
        if jira_server_url and jira_username and jira_token:
            # Use UI-provided credentials
            from agno.tools.jira import JiraTools
            agent.tools = [JiraTools(
                server_url=jira_server_url,
                username=jira_username,
                token=jira_token
            )]
        else:
            # Check if environment variables are set for Jira
            import os
            env_jira_server_url = os.getenv("JIRA_SERVER_URL")
            env_jira_username = os.getenv("JIRA_USERNAME")
            env_jira_token = os.getenv("JIRA_TOKEN")
            
            # Use environment variables if available
            if env_jira_server_url and env_jira_username and env_jira_token:
                from agno.tools.jira import JiraTools
                agent.tools = [JiraTools()]
            else:
                # No Jira credentials available, leave tools empty
                agent.tools = []
    except Exception as e:
        # If there's any error initializing Jira tools, leave tools empty
        agent.tools = []
        # Log the error for debugging (in a real application, you might want to log this properly)
        pass


def _parse_manual_test_cases(manual_test_cases_markdown: str) -> list:
    """
    Parse manual test cases from markdown table format.
    
    Args:
        manual_test_cases_markdown: Markdown table string
        
    Returns:
        List of dictionaries representing test cases
    """
    try:
        lines = manual_test_cases_markdown.strip().split('\n')
        
        # Find the header and separator lines
        header_line = None
        separator_line = None
        
        for i, line in enumerate(lines):
            if '| Test Case ID' in line:
                header_line = i
            elif line.startswith('|---'):
                separator_line = i
                break  # Assume the first separator after header is the correct one

        if header_line is not None and separator_line is not None:
            header = [h.strip() for h in lines[header_line].strip('|').split('|')]
            data_lines = lines[separator_line + 1:]
            data = []
            
            for line in data_lines:
                if line.strip().startswith('|'):
                    # Split by '|' and strip whitespace, remove first and last empty strings
                    row_data = [cell.strip() for cell in line.strip('|').split('|')]
                    data.append(row_data)

            return pd.DataFrame(data, columns=header).to_dict('records')
        
        return []
        
    except Exception as e:
        st.error(f"Error parsing manual test cases: {e}")
        return []


def _has_unsaved_scenario_changes() -> bool:
    """
    Check if there are unsaved changes in the scenario editor.
    
    Returns:
        bool: True if there are unsaved changes
    """
    return (
        "scenario_editor" in st.session_state and 
        st.session_state.get("scenario_editor", "") != 
        st.session_state.get(SESSION_KEYS["edited_steps"], "")
    )