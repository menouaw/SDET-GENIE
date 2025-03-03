import re
from typing import Dict, Any
import json

from src.Agents.agents import (
    code_gen_agent
)

from src.Utilities.utils import (
    extract_selectors_from_history,
    analyze_actions,
)

def generate_gherkin_scenarios(user_story: str) -> str:
    """Generate Gherkin scenarios from a user story"""
    prompt = f"""
    Convert the following user story into comprehensive Gherkin test scenarios.
    Include positive and negative test cases, edge cases, and boundary conditions.
    
    User Story:
    {user_story}
    
    Requirements:
    - Use proper Gherkin syntax with Feature, Scenario, Given, When, Then
    - Add descriptive scenario titles
    - Include tags for organization
    - Create at least 3-5 scenarios covering different cases
    - Focus on functional requirements
    """
    return prompt
    
def extract_code_content(text: str) -> str:
    """Extract code from markdown code blocks if present"""
    code_block_pattern = re.compile(r"```(?:python|gherkin|javascript|java|robot)?\n(.*?)```", re.DOTALL)
    match = code_block_pattern.search(text)
    
    if match:
        return match.group(1).strip()
    return text.strip()

def extract_model_actions(model_actions: List[Dict]) -> List[Dict]:
    """
    Extract and structure model actions from browser agent debug output
    
    Args:
        model_actions: Raw model actions from browser agent debug mode
        
    Returns:
        List of structured action details
    """
    structured_actions = []
    
    for action_index, action_data in enumerate(model_actions):
        action_entry = {
            "action_index": action_index,
            "action_type": None,
            "element_xpath": None,
            "element_id": None,
            "element_selector": None,
            "input_value": None,
            "url": None
        }
        
        # Determine action type
        if "go_to_url" in action_data:
            action_entry["action_type"] = "navigation"
            action_entry["url"] = action_data["go_to_url"].get("url")
        
        elif "get_xpath_of_element" in action_data:
            action_entry["action_type"] = "locate_element"
            element_index = action_data["get_xpath_of_element"].get("index")
            action_entry["element_index"] = element_index
            
            # Extract element info from interacted_element
            if "interacted_element" in action_data and action_data["interacted_element"]:
                element_info = str(action_data["interacted_element"])
                
                # Parse XPath
                xpath_match = re.search(r"xpath='([^']+)'", element_info)
                if xpath_match:
                    action_entry["element_xpath"] = xpath_match.group(1)
                
                # Parse ID
                id_match = re.search(r"'id': '([^']+)'", element_info)
                if id_match:
                    action_entry["element_id"] = id_match.group(1)
                
                # Parse CSS selector
                css_match = re.search(r"css_selector='([^']+)'", element_info)
                if css_match:
                    action_entry["element_selector"] = css_match.group(1)
        
        elif "click_element" in action_data:
            action_entry["action_type"] = "click"
            element_index = action_data["click_element"].get("index")
            action_entry["element_index"] = element_index
            
            # Extract element info from interacted_element
            if "interacted_element" in action_data and action_data["interacted_element"]:
                element_info = str(action_data["interacted_element"])
                
                # Parse XPath
                xpath_match = re.search(r"xpath='([^']+)'", element_info)
                if xpath_match:
                    action_entry["element_xpath"] = xpath_match.group(1)
                
                # Parse ID
                id_match = re.search(r"'id': '([^']+)'", element_info)
                if id_match:
                    action_entry["element_id"] = id_match.group(1)
                
                # Parse CSS selector
                css_match = re.search(r"css_selector='([^']+)'", element_info)
                if css_match:
                    action_entry["element_selector"] = css_match.group(1)
        
        elif "input_text" in action_data:
            action_entry["action_type"] = "input"
            element_index = action_data["input_text"].get("index")
            input_value = action_data["input_text"].get("value")
            action_entry["element_index"] = element_index
            action_entry["input_value"] = input_value
            
            # Extract element info from interacted_element
            if "interacted_element" in action_data and action_data["interacted_element"]:
                element_info = str(action_data["interacted_element"])
                
                # Parse XPath
                xpath_match = re.search(r"xpath='([^']+)'", element_info)
                if xpath_match:
                    action_entry["element_xpath"] = xpath_match.group(1)
                
                # Parse ID
                id_match = re.search(r"'id': '([^']+)'", element_info)
                if id_match:
                    action_entry["element_id"] = id_match.group(1)
                
                # Parse CSS selector
                css_match = re.search(r"css_selector='([^']+)'", element_info)
                if css_match:
                    action_entry["element_selector"] = css_match.group(1)
        
        elif "perform_element_action" in action_data:
            action_params = action_data["perform_element_action"]
            action_type = action_params.get("action", "unknown")
            action_entry["action_type"] = action_type
            element_index = action_params.get("index")
            action_entry["element_index"] = element_index
            
            if action_type == "fill" and "value" in action_params:
                action_entry["input_value"] = action_params["value"]
            
            # Extract element info from interacted_element
            if "interacted_element" in action_data and action_data["interacted_element"]:
                element_info = str(action_data["interacted_element"])
                
                # Parse XPath
                xpath_match = re.search(r"xpath='([^']+)'", element_info)
                if xpath_match:
                    action_entry["element_xpath"] = xpath_match.group(1)
                
                # Parse ID
                id_match = re.search(r"'id': '([^']+)'", element_info)
                if id_match:
                    action_entry["element_id"] = id_match.group(1)
                
                # Parse CSS selector
                css_match = re.search(r"css_selector='([^']+)'", element_info)
                if css_match:
                    action_entry["element_selector"] = css_match.group(1)
        
        # Add to structured actions if we identified an action type
        if action_entry["action_type"]:
            structured_actions.append(action_entry)
    
    return structured_actions

def map_gherkin_to_actions(gherkin_steps: str, model_actions: List[Dict]) -> Dict:
    """
    Map Gherkin steps to corresponding browser actions
    
    Args:
        gherkin_steps: String containing Gherkin scenarios
        model_actions: Structured model actions
        
    Returns:
        Dictionary mapping Gherkin steps to actions
    """
    step_mapping = {}
    
    # Extract all steps from Gherkin
    step_pattern = re.compile(r'(Given|When|Then|And|But)\s+(.+?)$', re.MULTILINE)
    steps = step_pattern.findall(gherkin_steps)
    
    # Create mapping based on action types
    current_action_index = 0
    
    for step_type, step_text in steps:
        step_key = f"{step_type} {step_text}"
        
        # Skip background steps or steps that are just descriptions
        if "background" in step_type.lower() or not step_text.strip():
            continue
        
        # Determine what actions match this step
        matching_actions = []
        
        # Handle common step patterns
        if any(kw in step_text.lower() for kw in ["navigate", "go to", "visit", "open", "browse"]):
            # Find navigation actions
            for action in model_actions:
                if action["action_type"] == "navigation":
                    matching_actions.append(action)
        
        elif any(kw in step_text.lower() for kw in ["click", "press", "select", "choose"]):
            # Find click actions
            for action in model_actions:
                if action["action_type"] == "click":
                    matching_actions.append(action)
        
        elif any(kw in step_text.lower() for kw in ["type", "enter", "input", "fill"]):
            # Find input actions
            for action in model_actions:
                if action["action_type"] == "input" or (action["action_type"] == "fill" and action["input_value"]):
                    matching_actions.append(action)
        
        # Map remaining steps to actions based on order
        if not matching_actions and current_action_index < len(model_actions):
            remaining_count = min(3, len(model_actions) - current_action_index)
            matching_actions = model_actions[current_action_index:current_action_index + remaining_count]
            current_action_index += remaining_count
        
        # Add to mapping if we found matches
        if matching_actions:
            step_mapping[step_key] = matching_actions
    
    return step_mapping
    
def generate_selenium_pytest_bdd(gherkin_steps: str, history_data: Dict[str, Any]) -> str:
    """Generate a single Python file with Selenium PyTest BDD automation code with enhanced model actions parsing"""
    
    # Extract feature name from Gherkin
    feature_name = "Automated_Test"
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    if feature_match:
        feature_name = feature_match.group(1).strip().replace(" ", "_")
    
    # Extract selectors and actions from history_data
    selectors = extract_selectors_from_history(history_data)
    actions = analyze_actions(history_data)
    
    # NEW: Extract detailed model actions from browser agent debug output
    model_actions = extract_model_actions(history_data.get('model_actions', []))
    
    # NEW: Map Gherkin steps to model actions
    step_action_mapping = map_gherkin_to_actions(gherkin_steps, model_actions)
    
    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"
    
    # Create prompt for Selenium PyTest BDD code with enhanced information
    code_file_prompt = f"""
    Generate a SINGLE Python file with Selenium PyTest BDD automation code based on the following Gherkin steps and browser interactions:
    
    ```gherkin
    {gherkin_steps}
    ```
    
    Agent execution details:
    - Base URL: {base_url}
    - Element selectors: {json.dumps(selectors, indent=2)}
    - Actions performed: {json.dumps(actions, indent=2)}
    - Extracted content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
    
    IMPORTANT - Detailed browser actions from debug mode:
    {json.dumps(model_actions, indent=2)}
    
    IMPORTANT - Mapping of Gherkin steps to browser actions:
    {json.dumps(step_action_mapping, indent=2)}
    
    Requirements:
    1. The file should include ALL necessary imports for Selenium and PyTest BDD
    2. Include the Gherkin feature as a docstring at the top of the file
    3. Create step definitions for each step in the Gherkin scenarios, using the exact element XPaths captured during testing
    4. Use Selenium WebDriver for browser automation with proper element selection strategies
    5. Include explicit wait strategies (WebDriverWait) and error handling
    6. Add helper functions for common operations
    7. Ensure that elements are identified using the exact XPaths provided in the model_actions
    8. Include a main function to run the tests
    9. Add clear comments throughout the code
    10. Make it a single, self-contained file that can be run directly
    
    Return ONLY the Python code without any additional explanation.
    """
    
    try:
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)
        
        return code_content
        
    except Exception as e:
        st.error(f"Error generating Selenium PyTest BDD code: {str(e)}")
        raise

def generate_playwright_python(gherkin_steps: str, history_data: Dict[str, Any]) -> str:
    """Generate a single Python file with Playwright automation code"""
    
    # Extract feature name from Gherkin
    feature_name = "Automated_Test"
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    if feature_match:
        feature_name = feature_match.group(1).strip().replace(" ", "_")
    
    # Extract selectors and actions
    selectors = extract_selectors_from_history(history_data)
    actions = analyze_actions(history_data)
    
    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"
    
    # Create prompt for Playwright code
    code_file_prompt = f"""
    Generate a SINGLE Python file with Playwright automation code based on the following Gherkin steps and browser interactions:
    
    ```gherkin
    {gherkin_steps}
    ```
    
    Agent execution details:
    - Base URL: {base_url}
    - Element selectors: {json.dumps(selectors, indent=2)}
    - Actions performed: {json.dumps(actions, indent=2)}
    - Extracted content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
    
    Requirements:
    1. The file should include ALL necessary imports for Playwright
    2. Include the Gherkin feature as a docstring at the top of the file
    3. Create async functions for each scenario
    4. Use Playwright's async API for browser automation
    5. Include proper wait strategies and error handling
    6. Add helper functions for common operations
    7. Include a main async function to run the tests
    8. Add clear comments throughout the code
    9. Make it a single, self-contained file that can be run directly
    
    Return ONLY the Python code without any additional explanation.
    """
    
    try:
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)
        
        return code_content
        
    except Exception as e:
        st.error(f"Error generating Playwright code: {str(e)}")
        raise

def generate_cypress_js(gherkin_steps: str, history_data: Dict[str, Any]) -> str:
    """Generate a single JavaScript file with Cypress automation code"""
    
    # Extract feature name from Gherkin
    feature_name = "Automated_Test"
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    if feature_match:
        feature_name = feature_match.group(1).strip().replace(" ", "_")
    
    # Extract selectors and actions
    selectors = extract_selectors_from_history(history_data)
    actions = analyze_actions(history_data)
    
    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"
    
    # Create prompt for Cypress code
    code_file_prompt = f"""
    Generate a SINGLE JavaScript file with Cypress test automation code based on the following Gherkin steps and browser interactions:
    
    ```gherkin
    {gherkin_steps}
    ```
    
    Agent execution details:
    - Base URL: {base_url}
    - Element selectors: {json.dumps(selectors, indent=2)}
    - Actions performed: {json.dumps(actions, indent=2)}
    - Extracted content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
    
    Requirements:
    1. The file should be ready to use with Cypress
    2. Include the Gherkin feature as a comment at the top of the file
    3. Use Cypress's describe/it/cy structure for test organization
    4. Include proper wait strategies and error handling
    5. Add helper functions for common operations
    6. Add clear comments throughout the code
    7. Make it a single, self-contained .js file that can be placed in Cypress's integration folder
    
    Return ONLY the JavaScript code without any additional explanation.
    """
    
    try:
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)
        
        return code_content
        
    except Exception as e:
        st.error(f"Error generating Cypress code: {str(e)}")
        raise

def generate_robot_framework(gherkin_steps: str, history_data: Dict[str, Any]) -> str:
    """Generate Robot Framework test file"""
    
    # Extract feature name from Gherkin
    feature_name = "Automated_Test"
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    if feature_match:
        feature_name = feature_match.group(1).strip().replace(" ", "_")
    
    # Extract selectors and actions
    selectors = extract_selectors_from_history(history_data)
    actions = analyze_actions(history_data)
    
    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"
    
    # Create prompt for Robot Framework code
    code_file_prompt = f"""
    Generate a Robot Framework (.robot) test file based on the following Gherkin steps and browser interactions:
    
    ```gherkin
    {gherkin_steps}
    ```
    
    Agent execution details:
    - Base URL: {base_url}
    - Element selectors: {json.dumps(selectors, indent=2)}
    - Actions performed: {json.dumps(actions, indent=2)}
    - Extracted content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
    
    Requirements:
    1. The file should follow Robot Framework syntax and structure
    2. Include proper Settings, Variables, Keywords, and Test Cases sections
    3. Use SeleniumLibrary for browser interactions
    4. Include appropriate wait strategies
    5. Create reusable keywords for common operations
    6. Add documentation comments throughout the code
    
    Return ONLY the Robot Framework code without any additional explanation.
    """
    
    try:
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)
        
        return code_content
        
    except Exception as e:
        st.error(f"Error generating Robot Framework code: {str(e)}")
        raise

def generate_java_selenium(gherkin_steps: str, history_data: Dict[str, Any]) -> str:
    """Generate a Java file with Selenium and Cucumber automation code"""
    
    # Extract feature name from Gherkin
    feature_name = "Automated_Test"
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    if feature_match:
        feature_name = feature_match.group(1).strip().replace(" ", "_")
    
    # Extract selectors and actions
    selectors = extract_selectors_from_history(history_data)
    actions = analyze_actions(history_data)
    
    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"
    
    # Create prompt for Java Selenium Cucumber code
    code_file_prompt = f"""
    Generate a Java implementation for Selenium with Cucumber based on the following Gherkin steps and browser interactions:
    
    ```gherkin
    {gherkin_steps}
    ```
    
    Agent execution details:
    - Base URL: {base_url}
    - Element selectors: {json.dumps(selectors, indent=2)}
    - Actions performed: {json.dumps(actions, indent=2)}
    - Extracted content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
    
    Requirements:
    1. Create a complete Java implementation with proper package structure
    2. Include step definition classes for all Gherkin steps
    3. Use Selenium WebDriver for browser automation
    4. Include proper wait strategies and error handling
    5. Use Page Object Model pattern
    6. Add clear JavaDoc comments throughout the code
    7. Include a test runner class with JUnit
    
    Return ONLY the Java code without any additional explanation.
    """
    
    try:
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)
        
        return code_content
        
    except Exception as e:
        st.error(f"Error generating Java Selenium Cucumber code: {str(e)}")
        raise

