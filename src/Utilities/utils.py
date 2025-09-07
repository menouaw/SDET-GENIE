from browser_use import Controller, ActionResult
from src.logic.element_tracker import element_tracker

import re
import json
import time
import streamlit as st

from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# Legacy element tracking (maintained for backward compatibility)
element_interactions = []

def track_element_interaction(action_type: str, element_data: Dict[str, Any]):
    """Track element interactions for automation script generation (legacy)."""
    element_interactions.append({
        "action_type": action_type,
        "element_data": element_data,
        "timestamp": str(time.time())
    })
    
def get_tracked_interactions() -> Dict[str, Any]:
    """Get all tracked element interactions (includes both legacy and enhanced tracking)."""
    # Return both legacy tracking and enhanced tracking data
    legacy_data = element_interactions.copy()
    enhanced_data = element_tracker.get_interactions_summary()
    
    return {
        "legacy_interactions": legacy_data,
        "enhanced_interactions": enhanced_data,
        "total_count": len(legacy_data) + enhanced_data.get("total_interactions", 0),
        "automation_ready_data": element_tracker.get_automation_script_data()
    }

def clear_tracked_interactions():
    """Clear all tracked interactions (both legacy and enhanced)."""
    global element_interactions
    element_interactions = []
    element_tracker.clear_interactions()

def get_comprehensive_element_data() -> Dict[str, Any]:
    """Get comprehensive element tracking data for automation script generation."""
    return {
        "element_tracking_summary": element_tracker.get_interactions_summary(),
        "automation_script_data": element_tracker.get_automation_script_data(),
        "framework_exports": {
            "selenium": element_tracker.export_for_framework("selenium"),
            "playwright": element_tracker.export_for_framework("playwright"),
            "cypress": element_tracker.export_for_framework("cypress")
        },
        "json_export": json.dumps(element_tracker.get_interactions_summary(), indent=2)
    }

# Set up controller for browser-use (simplified for compatibility)
controller = Controller()

def load_css(file_path):
    """Load external CSS file into Streamlit application.
    
    Args:
        file_path (str): Path to the CSS file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"CSS file not found: {file_path}")
    except Exception as e:
        st.error(f"Error loading CSS file: {e}")

# Simplified controller for basic browser interactions
# Note: Custom actions removed to avoid schema validation issues with browser-use v0.7.2
# The framework provides built-in actions for standard browser interactions

# Helper functions for code generation
def extract_selectors_from_history(history_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract element selectors from agent history"""
    selectors = {}
    xpath_pattern = re.compile(r"The xpath of the element is (.*)")
    element_details_pattern = re.compile(r"Element Details: \{(.+?)\}")
    
    for content in history_data.get('extracted_content', []):
        if isinstance(content, str):
            # Extract XPath from direct XPath actions
            match = xpath_pattern.search(content)
            if match:
                xpath = match.group(1)
                name = "element_" + str(len(selectors) + 1)
                selectors[name] = xpath
                continue
                
            # Extract from detailed element information
            details_match = element_details_pattern.search(content)
            if details_match:
                try:
                    # Try to parse the JSON-like string
                    details_str = '{' + details_match.group(1) + '}'
                    # Clean up the string for proper JSON parsing
                    details_str = details_str.replace("'", "\"")
                    details = json.loads(details_str)
                    
                    # Use the best selector available
                    selector = None
                    if details.get("id"):
                        selector = details.get("css_selector")
                    elif details.get("relative_xpath"):
                        selector = details.get("relative_xpath")
                    elif details.get("absolute_xpath"):
                        selector = details.get("absolute_xpath")
                    
                    if selector:
                        name = f"element_{len(selectors) + 1}"
                        selectors[name] = selector
                except Exception as e:
                    print(f"Error parsing element details: {e}")
    
    return selectors

def analyze_actions(history_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze the actions performed by the agent to create step implementations"""
    actions = []
    element_details_pattern = re.compile(r"Element Details: (\{.+?\})")
    
    for i, action_name in enumerate(history_data.get('action_names', [])):
        action_info = {
            "name": action_name,
            "index": i,
            "type": "unknown",
            "element_details": None
        }
        
        # Determine action type
        if "navigate" in action_name.lower() or "goto" in action_name.lower():
            action_info["type"] = "navigation"
        elif "click" in action_name.lower():
            action_info["type"] = "click"
        elif "type" in action_name.lower() or "fill" in action_name.lower() or "enter" in action_name.lower():
            action_info["type"] = "input"
        elif "check" in action_name.lower() or "verify" in action_name.lower() or "assert" in action_name.lower():
            action_info["type"] = "verification"
        elif "get xpath" in action_name.lower():
            action_info["type"] = "xpath"
        elif "get detailed element information" in action_name.lower():
            action_info["type"] = "element_details"
        elif "save job details" in action_name.lower():
            action_info["type"] = "custom_save"
        
        # Extract element details if available in the content
        if i < len(history_data.get('extracted_content', [])):
            content = history_data.get('extracted_content', [])[i]
            if isinstance(content, str):
                details_match = element_details_pattern.search(content)
                if details_match:
                    try:
                        details_str = details_match.group(1)
                        # Clean up the string for proper JSON parsing
                        details_str = details_str.replace("'", "\"")
                        details = json.loads(details_str)
                        action_info["element_details"] = details
                    except Exception as e:
                        print(f"Error parsing element details in action analysis: {e}")
        
        actions.append(action_info)
    
    return actions
