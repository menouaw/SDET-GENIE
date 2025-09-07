"""
Browser execution logic for SDET-GENIE application.
Handles the async browser test execution and data collection.
"""

import os
import re
import streamlit as st
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import datetime

from browser_use import Agent as BrowserAgent
from browser_use.browser.events import ClickElementEvent, TypeTextEvent
from langchain_google_genai import ChatGoogleGenerativeAI

from src.logic.element_tracker import element_tracker
from src.Prompts.browser_prompts import generate_browser_task
from src.logic.model_factory import get_llm_instance
from src.config import SESSION_KEYS, APP_CONFIG, BROWSER_CONFIG

# Import the TrackingBrowserAgent
from src.logic.tracking_browser_agent import TrackingBrowserAgent


async def execute_test(steps: str) -> None:
    """
    Execute Gherkin test scenarios in a browser environment.
    
    Args:
        steps: Gherkin scenarios to execute
        
    Raises:
        Exception: If test execution fails
    """
    try:
        # Parse the Gherkin content to extract scenarios
        scenarios = _parse_gherkin_scenarios(steps)

        # Execute all scenarios in a single browser session to maintain context
        all_results = []
        all_actions = []
        all_extracted_content = []
        element_xpath_map = {}
        history = None  # Initialize history variable
        execution_context = {
            "visited_urls": [],
            "session_data": {}
        }

        # Get the selected provider and model from session state
        provider = st.session_state.get('selected_provider', 'Google')
        model = st.session_state.get('selected_model', 'gemini-2.0-flash')
        
        # Create the browser_use model instance
        browser_use_llm = get_llm_instance(provider, model, for_agno=False)
        
        if not browser_use_llm:
            st.error("Failed to initialize the BrowserAgent model. Please check your API keys and environment setup.")
            return

        # Define lifecycle hooks to maintain context
        async def on_step_end(agent):
            """Hook to capture context after each step"""
            try:
                # Capture current URL
                current_url = await agent.browser_session.get_current_page_url()
                if current_url and current_url not in execution_context["visited_urls"]:
                    execution_context["visited_urls"].append(current_url)
                
                # Capture session data if needed
                # This could include cookies, localStorage, etc.
            except Exception as e:
                # Silently handle errors in hooks
                pass

        # Execute each scenario in its own browser session
        for i, scenario in enumerate(scenarios):
            try:
                # Create browser agent with proper recording configuration for each scenario
                # Add timestamp and scenario index for unique scenario identification
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                scenario_id = f"execution_{timestamp}_scenario_{i+1}"
                
                # Create timestamped directories for this execution
                scenario_video_dir = f"./recordings/videos/{scenario_id}"
                scenario_traces_dir = f"./recordings/debug.traces/{scenario_id}"
                scenario_har_path = f"./recordings/network.traces/{scenario_id}.har"
                
                # Ensure directories exist
                Path(scenario_video_dir).mkdir(parents=True, exist_ok=True)
                Path(scenario_traces_dir).mkdir(parents=True, exist_ok=True)
                Path("./recordings/network.traces").mkdir(parents=True, exist_ok=True)
                
                # Generate the enhanced browser task prompt using our designed prompt
                enhanced_task = generate_browser_task(scenario, execution_context)
                
                # Create the browser agent with recording parameters for this specific scenario
                browser_agent = TrackingBrowserAgent(
                    task=enhanced_task,  # Use the enhanced task prompt instead of raw scenario
                    llm=browser_use_llm,
                    generate_gif=True,
                    record_video_dir=scenario_video_dir,
                    record_har_path=scenario_har_path,
                    traces_dir=scenario_traces_dir,
                    highlight_elements=BROWSER_CONFIG.get("highlight_elements", True),
                    use_vision=BROWSER_CONFIG.get("use_vision", True),
                    record_har_content=BROWSER_CONFIG.get("record_har_content", "embed"),
                    record_har_mode=BROWSER_CONFIG.get("record_har_mode", "full"),
                    vision_detail_level=BROWSER_CONFIG.get("vision_detail_level", "auto"),
                    max_history_items=BROWSER_CONFIG.get("max_history_items"),
                    save_conversation_path=BROWSER_CONFIG.get("save_conversation_path"),
                    headless=BROWSER_CONFIG.get("headless", False),
                    window_size=BROWSER_CONFIG.get("window_size", {"width": 1280, "height": 720})
                )

                # Debug output to verify recording parameters
                print(f"DEBUG: Recording parameters for scenario {i+1} execution {scenario_id}:")
                print(f"  task: {enhanced_task[:100]}...")  # Show first 100 chars of enhanced task
                print(f"  record_video_dir: {scenario_video_dir}")
                print(f"  record_har_path: {scenario_har_path}")
                print(f"  traces_dir: {scenario_traces_dir}")
                print(f"  generate_gif: {browser_agent.generate_gif}")
                
                # Check if browser profile has the recording settings
                if hasattr(browser_agent, 'browser_profile'):
                    bp = browser_agent.browser_profile
                    print(f"  browser_profile.record_video_dir: {getattr(bp, 'record_video_dir', None)}")
                    print(f"  browser_profile.record_har_path: {getattr(bp, 'record_har_path', None)}")
                    print(f"  browser_profile.traces_dir: {getattr(bp, 'traces_dir', None)}")
                
                # Set the on_step_end callback using our custom method
                browser_agent.set_on_step_end_callback(on_step_end)

                # Update the current URL in execution context after agent is created
                if history and hasattr(history, 'urls') and history.urls():
                    try:
                        current_url = await browser_agent.browser_session.get_current_page_url()
                        execution_context["current_url"] = current_url
                    except:
                        # Fallback to last URL in history
                        execution_context["current_url"] = history.urls()[-1] if history.urls() else ""
                
                # Execute and collect results
                scenario_history = await browser_agent.run(max_steps=50)
                
                # For the first scenario, save the history object
                if i == 0:
                    history = scenario_history
                else:
                    # For subsequent scenarios, merge the history
                    _merge_history(history, scenario_history)
                
                result = scenario_history.final_result()
                
                if isinstance(result, str):
                    # Convert string result to JSON format
                    result = {"status": result, "details": "Execution completed"}
                all_results.append(result)

                # Enhanced element tracking: Extract interactions from browser-use events
                # Get element interactions directly from the browser agent
                tracked_interactions = browser_agent.get_tracked_interactions()
                
                # Process model actions to extract additional element details
                action_details = _process_model_actions(scenario_history, element_xpath_map)
                all_actions.extend(action_details)

                # Extract content
                for content in scenario_history.extracted_content():
                    all_extracted_content.append(content)
                    _extract_xpath_from_content(content, element_xpath_map)
                    
            except Exception as e:
                st.markdown(
                    f'<div class="status-error">Error executing scenario {i+1}: {str(e)}</div>', 
                    unsafe_allow_html=True
                )
                # Continue with the next scenario instead of stopping completely
                continue

        # After all scenarios, display the element tracking information
        tracked_interactions = element_tracker.get_interactions_summary()
        print(f"Tracked interactions: {tracked_interactions}")  # Debug print
        if tracked_interactions["total_interactions"] > 0:
            st.write("🎯 **Element Interactions Captured:**")
            st.write(f"- Total interactions: {tracked_interactions['total_interactions']}")
            st.write(f"- Action types: {', '.join(tracked_interactions['action_types'])}")
            st.write(f"- Unique elements: {tracked_interactions['unique_elements']}")
            
            # Show key element details
            st.write("\n📋 **Key Element Details:**")
            for element_key, element_data in tracked_interactions["automation_data"]["element_library"].items():
                st.write(f"- {element_key}: {element_data['tag_name']} with id='{element_data['attributes'].get('id', 'N/A')}'")
            
            # Show framework-specific exports
            st.write("\n🔧 **Framework Exports Available:**")
            st.write("- Selenium")
            st.write("- Playwright")
            st.write("- Cypress")
            
            # Show selector coverage
            selector_types = list(tracked_interactions["automation_data"]["framework_selectors"].keys())
            st.write(f"\n🧩 **Selector Coverage:** {len(selector_types)} different selector types captured")
        else:
            st.write("ℹ️ No element interactions were tracked in this execution.")
            print("No element interactions were tracked")  # Debug print

        # Save combined history to session state with comprehensive element tracking
        if history:  # Only save if we have valid history
            # Get comprehensive element tracking data
            element_tracking_data = element_tracker.get_interactions_summary()
            automation_data = element_tracker.get_automation_script_data()
            
            print(f"Saving element tracking data: {element_tracking_data}")  # Debug print
            
            _save_execution_history(
                history, all_actions, element_xpath_map, 
                all_extracted_content, all_results,
                element_tracking_data, automation_data
            )

        # Display execution results
        _display_execution_results(all_results)

    except Exception as e:
        st.markdown(
            f'<div class="status-error">An error occurred during test execution: {str(e)}</div>', 
            unsafe_allow_html=True
        )
        raise


def _merge_history(main_history, new_history):
    """
    Merge new history into main history to maintain context.
    
    Args:
        main_history: Main AgentHistoryList object
        new_history: New AgentHistoryList object to merge
    """
    # This is a simplified merge - in practice, you might need to extend AgentHistoryList
    # to support proper merging of histories
    pass


def _extend_history_with_context(history, context):
    """
    Extend history with execution context information.
    
    Args:
        history: AgentHistoryList object
        context: Execution context dictionary
    """
    # Add context information to history for better tracking
    if not hasattr(history, 'execution_context'):
        history.execution_context = context
    else:
        # Merge context
        history.execution_context.update(context)


def _extract_element_interactions_from_history(history):
    """
    Extract element interaction details from browser-use agent history.
    
    Args:
        history: Browser agent execution history
        
    Returns:
        List of element interaction details
    """
    interactions = []
    
    try:
        # Get model actions from history
        model_actions = history.model_actions()
        action_names = history.action_names()
        
        for i, action_data in enumerate(model_actions):
            action_name = action_names[i] if i < len(action_names) else "Unknown Action"
            
            # Extract element details from different action types
            element_details = None
            action_type = "unknown"
            
            # Check for click actions
            if "click_element_by_index" in action_data:
                action_type = "click"
                click_data = action_data["click_element_by_index"]
                element_details = {
                    "element_index": click_data.get("index"),
                    "action_type": "click",
                    "button": "left",  # default
                    "ctrl_held": click_data.get("while_holding_ctrl", False)
                }
            
            # Check for input text actions
            elif "input_text" in action_data:
                action_type = "type_text"
                input_data = action_data["input_text"]
                element_details = {
                    "element_index": input_data.get("index"),
                    "action_type": "type_text",
                    "text": input_data.get("text", ""),
                    "clear_existing": input_data.get("clear_existing", True)
                }
            
            # Check for other element actions
            elif "upload_file_to_element" in action_data:
                action_type = "upload_file"
                upload_data = action_data["upload_file_to_element"]
                element_details = {
                    "element_index": upload_data.get("index"),
                    "action_type": "upload_file",
                    "file_path": upload_data.get("path", "")
                }
            
            if element_details:
                # Add common metadata
                element_details.update({
                    "action_name": action_name,
                    "sequence_number": i,
                    "timestamp": f"step_{i}"
                })
                
                interactions.append(element_details)
    
    except Exception as e:
        st.error(f"Error extracting element interactions: {str(e)}")
    
    return interactions


def _parse_gherkin_scenarios(steps: str) -> List[str]:
    """
    Parse Gherkin content to extract individual scenarios.
    
    Args:
        steps: Gherkin scenarios text
        
    Returns:
        List of individual scenario strings
    """
    scenarios = []
    lines = steps.split('\n')
    current_scenario = []
    in_scenario_outline = False
    examples_lines = []
    
    for line in lines:
        stripped_line = line.strip()
        
        # Check for Scenario or Scenario Outline
        if stripped_line.startswith('Scenario:'):
            # If we were processing a Scenario Outline, expand it now
            if in_scenario_outline and current_scenario and examples_lines:
                expanded_scenarios = _expand_scenario_outline(current_scenario, examples_lines)
                scenarios.extend(expanded_scenarios)
                current_scenario = []
                examples_lines = []
                in_scenario_outline = False
            
            # Start new regular scenario
            if current_scenario:
                scenarios.append('\n'.join(current_scenario))
            current_scenario = [line]
            
        elif stripped_line.startswith('Scenario Outline:'):
            # If we were processing another Scenario Outline, expand it first
            if in_scenario_outline and current_scenario and examples_lines:
                expanded_scenarios = _expand_scenario_outline(current_scenario, examples_lines)
                scenarios.extend(expanded_scenarios)
                examples_lines = []
            
            # Start new scenario outline
            if current_scenario:
                scenarios.append('\n'.join(current_scenario))
            current_scenario = [line]
            in_scenario_outline = True
            
        elif stripped_line.startswith('Examples:'):
            # Start of examples section for Scenario Outline
            if in_scenario_outline and current_scenario:
                examples_lines = [line]
            elif current_scenario:
                current_scenario.append(line)
                
        elif in_scenario_outline and examples_lines:
            # Collect examples lines
            examples_lines.append(line)
            
        elif current_scenario:
            # Regular scenario line
            current_scenario.append(line)
    
    # Process the last scenario
    if in_scenario_outline and current_scenario and examples_lines:
        # Expand the last Scenario Outline
        expanded_scenarios = _expand_scenario_outline(current_scenario, examples_lines)
        scenarios.extend(expanded_scenarios)
    elif current_scenario:
        # Add the last regular scenario
        scenarios.append('\n'.join(current_scenario))
    
    return scenarios


def _expand_scenario_outline(scenario_lines: List[str], examples_lines: List[str]) -> List[str]:
    """
    Expand a Scenario Outline with its examples into individual scenarios.
    
    Args:
        scenario_lines: Lines of the Scenario Outline
        examples_lines: Lines of the Examples section
        
    Returns:
        List of expanded individual scenarios
    """
    if not scenario_lines or not examples_lines:
        return ['\n'.join(scenario_lines)] if scenario_lines else []
    
    # Find the header line (first line with |)
    header_line = None
    data_lines = []
    in_examples_data = False
    
    for line in examples_lines:
        stripped_line = line.strip()
        if stripped_line.startswith('|') and '|' in stripped_line:
            if header_line is None:
                header_line = stripped_line
                in_examples_data = True
            elif in_examples_data:
                data_lines.append(stripped_line)
    
    if not header_line or not data_lines:
        return ['\n'.join(scenario_lines)]
    
    # Parse header
    headers = [h.strip() for h in header_line.strip('|').split('|')]
    
    # Parse data rows
    examples = []
    for data_line in data_lines:
        values = [v.strip() for v in data_line.strip('|').split('|')]
        if len(values) == len(headers):
            example = dict(zip(headers, values))
            examples.append(example)
    
    # Expand scenarios
    expanded_scenarios = []
    scenario_text = '\n'.join(scenario_lines)
    
    # Replace the "Scenario Outline:" with "Scenario:" in the first line
    if scenario_lines and scenario_lines[0].strip().startswith('Scenario Outline:'):
        scenario_header = scenario_lines[0]
        scenario_name = scenario_header.strip().replace('Scenario Outline:', '', 1).strip()
        new_header = f"Scenario: {scenario_name}"
        # Add example info to the scenario name
        scenario_lines[0] = new_header
    
    base_scenario = '\n'.join(scenario_lines)
    
    for i, example in enumerate(examples):
        # Create a copy of the scenario
        expanded_scenario = base_scenario
        
        # Replace placeholders with actual values
        for key, value in example.items():
            placeholder = f"<{key}>"
            expanded_scenario = expanded_scenario.replace(placeholder, value)
        
        # Add example info to the scenario name
        if i == 0:
            expanded_scenarios.append(expanded_scenario)
        else:
            # Modify the scenario name to indicate which example it is
            lines = expanded_scenario.split('\n')
            if lines and lines[0].strip().startswith('Scenario:'):
                scenario_name = lines[0].strip().replace('Scenario:', '', 1).strip()
                lines[0] = f"Scenario: {scenario_name} (Example {i+1})"
                expanded_scenario = '\n'.join(lines)
            expanded_scenarios.append(expanded_scenario)
    
    return expanded_scenarios


def _process_model_actions(history, element_xpath_map: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Process model actions to extract element details.
    
    Args:
        history: Browser agent execution history
        element_xpath_map: Dictionary to store element XPath mappings
        
    Returns:
        List of action detail dictionaries
    """
    all_actions = []
    
    for i, action_data in enumerate(history.model_actions()):
        action_name = (
            history.action_names()[i] 
            if i < len(history.action_names()) 
            else "Unknown Action"
        )

        # Create a detail record for each action
        action_detail = {
            "name": action_name,
            "index": i,
            "element_details": {}
        }

        # Check if this is a get_xpath_of_element action
        if "get_xpath_of_element" in action_data:
            element_index = action_data["get_xpath_of_element"].get("index")
            action_detail["element_details"]["index"] = element_index

            # Check if the interacted_element field contains XPath information
            if "interacted_element" in action_data and action_data["interacted_element"]:
                element_info = action_data["interacted_element"]

                # Extract XPath from the DOMHistoryElement string
                xpath_match = re.search(r"xpath='([^']+)'", str(element_info))
                if xpath_match:
                    xpath = xpath_match.group(1)
                    element_xpath_map[str(element_index)] = xpath
                    action_detail["element_details"]["xpath"] = xpath

        # Check if this is an action on an element
        elif any(key in action_data for key in ["input_text", "click_element", "perform_element_action"]):
            # Find the action parameters
            for key in ["input_text", "click_element", "perform_element_action"]:
                if key in action_data:
                    action_params = action_data[key]
                    if "index" in action_params:
                        element_index = action_params["index"]
                        action_detail["element_details"]["index"] = element_index

                        # If we have already captured the XPath for this element, add it
                        if element_index in element_xpath_map:
                            action_detail["element_details"]["xpath"] = element_xpath_map[element_index]

                        # Also check interacted_element
                        if "interacted_element" in action_data and action_data["interacted_element"]:
                            element_info = action_data["interacted_element"]
                            xpath_match = re.search(r"xpath='([^']+)'", str(element_info))
                            if xpath_match:
                                xpath = xpath_match.group(1)
                                element_xpath_map[str(element_index)] = xpath
                                action_detail["element_details"]["xpath"] = xpath

        all_actions.append(action_detail)
    
    return all_actions


def _extract_xpath_from_content(content, element_xpath_map: Dict[str, str]) -> None:
    """
    Extract XPath information from content strings.
    
    Args:
        content: Content string to analyze
        element_xpath_map: Dictionary to store element XPath mappings
    """
    if isinstance(content, str):
        xpath_match = re.search(r"The xpath of the element is (.+)", content)
        if xpath_match:
            xpath = xpath_match.group(1)
            # Try to match with an element index from previous actions
            index_match = re.search(r"element (\d+)", content)
            if index_match:
                element_index = int(index_match.group(1))
                element_xpath_map[str(element_index)] = xpath


def _save_execution_history(
    history, 
    all_actions: List[Dict[str, Any]], 
    element_xpath_map: Dict[str, str],
    all_extracted_content: List[Any], 
    all_results: List[Dict[str, Any]],
    element_tracking_data: Optional[Dict[str, Any]] = None,
    automation_data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Save comprehensive execution history to session state.
    
    Args:
        history: Browser agent execution history
        all_actions: List of action details
        element_xpath_map: Element XPath mappings
        all_extracted_content: Extracted content list
        all_results: Execution results
        element_tracking_data: Comprehensive element interaction data
        automation_data: Data formatted for automation script generation
    """
    session_data = {
        "urls": history.urls(),
        "action_names": history.action_names(),
        "detailed_actions": all_actions,
        "element_xpaths": element_xpath_map,
        "extracted_content": all_extracted_content,
        "errors": history.errors(),
        "model_actions": history.model_actions(),
        "execution_date": st.session_state.get(
            SESSION_KEYS["execution_date"], 
            APP_CONFIG["execution_date"]
        ),
        # Enhanced data from browser-use features
        "screenshots": history.screenshots(),
        "screenshot_paths": history.screenshot_paths(),
        "gif_path": st.session_state.history.get('gif_path') if 'history' in st.session_state else None,
        "total_duration": history.total_duration_seconds(),
        "number_of_steps": history.number_of_steps(),
        # Additional browser-use features
        "model_outputs": history.model_outputs(),  # LLM responses
        "final_result": history.final_result(),    # Final extracted content
        "is_done": history.is_done(),              # Completion status
        "is_successful": history.is_successful(),  # Success status
        "vision_details": getattr(history, 'vision_data', None) if hasattr(history, 'vision_data') else None,
        # Recording paths for UI display
        "recording_paths": {
            "videos": "./recordings/videos",
            "network_traces": "./recordings/network.traces",
            "debug_traces": "./recordings/debug.traces"
        }
    }
    
    # Add comprehensive element tracking data
    if element_tracking_data:
        session_data["element_interactions"] = element_tracking_data
        print(f"Added element interactions to session data: {element_tracking_data}")  # Debug print
        
    if automation_data:
        session_data["automation_script_data"] = automation_data
        print(f"Added automation script data to session data: {automation_data}")  # Debug print
        
    # Add framework-specific exports for immediate use
    if element_tracking_data and element_tracking_data.get("total_interactions", 0) > 0:
        session_data["framework_exports"] = {
            "selenium": element_tracker.export_for_framework("selenium"),
            "playwright": element_tracker.export_for_framework("playwright"),
            "cypress": element_tracker.export_for_framework("cypress")
        }
        print("Added framework exports to session data")  # Debug print
    
    st.session_state[SESSION_KEYS["history"]] = session_data
    print(f"Session data saved: {list(session_data.keys())}")  # Debug print


def _display_execution_results(all_results: List[Dict[str, Any]]) -> None:
    """
    Display test execution completion message.
    
    Args:
        all_results: List of execution results
    """
    st.markdown(
        '<div class="status-success fade-in">Test execution completed!</div>', 
        unsafe_allow_html=True
    )