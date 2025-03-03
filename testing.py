import streamlit as st
from agno.agent import Agent
from agno.models.google import Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
import sys
import asyncio
import os
import json
import re
from playwright.async_api import async_playwright
from typing import List, Dict, Optional, Any, Tuple
from pydantic import BaseModel

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from dotenv import load_dotenv
load_dotenv()
from browser_use import Browser, Agent as BrowserAgent, Controller, ActionResult

# Initialize the agents
qa_agent = Agent(
    model=Gemini(id="gemini-1.5-flash", api_key=os.environ.get("GOOGLE_API_KEY")),
    markdown=True,
)

code_gen_agent = Agent(
    model=Gemini(id="gemini-1.5-flash", api_key=os.environ.get("GOOGLE_API_KEY")),
    markdown=True,
)

# Set up custom controller actions
controller = Controller()

class JobDetails(BaseModel):
    title: str
    company: str
    job_link: str
    salary: Optional[str] = None

@controller.action(
    'Save job details which you found on page',
    param_model=JobDetails
)
async def save_job(params: JobDetails, browser: Browser):
    print(f"Saving job: {params.title} at {params.company}")
    # Access browser if needed
    page = browser.get_current_page()
    await page.goto(params.job_link)
    return ActionResult(success=True, extracted_content=f"Saved job: {params.title} at {params.company}", include_in_memory=True)

class ElementOnPage(BaseModel):
    index: int
    xpath: Optional[str] = None

@controller.action("Get XPath of element using index", param_model=ElementOnPage)
async def get_xpath_of_element(params: ElementOnPage, browser: Browser):
    session = await browser.get_session()
    state = session.cached_state
    if params.index not in state.selector_map:
        return ActionResult(error="Element not found")
    element_node = state.selector_map[params.index]
    xpath = element_node.xpath
    if xpath is None:
        return ActionResult(error="Element not found, try another index")
    return ActionResult(extracted_content="The xpath of the element is "+xpath, include_in_memory=True)

class ElementProperties(BaseModel):
    index: int
    property_name: str = "innerText"

@controller.action("Get element property", param_model=ElementProperties)
async def get_element_property(params: ElementProperties, browser: Browser):
    page = browser.get_current_page()
    session = await browser.get_session()
    state = session.cached_state
    
    if params.index not in state.selector_map:
        return ActionResult(error="Element not found")
    
    element_node = state.selector_map[params.index]
    element = await page.query_selector(element_node.selector)
    
    if element is None:
        return ActionResult(error="Element not found on page")
    
    try:
        property_value = await element.get_property(params.property_name)
        json_value = await property_value.json_value()
        return ActionResult(
            extracted_content=f"Element {params.index} {params.property_name}: {json_value}",
            include_in_memory=True
        )
    except Exception as e:
        return ActionResult(error=f"Error getting property: {str(e)}")

class ElementAction(BaseModel):
    index: int
    action: str = "click"  # click, hover, focus, etc.
    value: Optional[str] = None  # For actions like fill

@controller.action("Perform element action", param_model=ElementAction)
async def perform_element_action(params: ElementAction, browser: Browser):
    page = browser.get_current_page()
    session = await browser.get_session()
    state = session.cached_state
    
    if params.index not in state.selector_map:
        return ActionResult(error="Element not found")
    
    element_node = state.selector_map[params.index]
    element = await page.query_selector(element_node.selector)
    
    if element is None:
        return ActionResult(error="Element not found on page")
    
    try:
        if params.action == "click":
            await element.click()
            return ActionResult(
                extracted_content=f"Clicked element {params.index}",
                include_in_memory=True
            )
        elif params.action == "hover":
            await element.hover()
            return ActionResult(
                extracted_content=f"Hovered over element {params.index}",
                include_in_memory=True
            )
        elif params.action == "fill" and params.value is not None:
            await element.fill(params.value)
            return ActionResult(
                extracted_content=f"Filled element {params.index} with '{params.value}'",
                include_in_memory=True
            )
        else:
            return ActionResult(error=f"Unsupported action: {params.action}")
    except Exception as e:
        return ActionResult(error=f"Error performing action: {str(e)}")

# Helper functions for code generation
def extract_selectors_from_history(history_data: Dict[str, Any]) -> Dict[str, str]:
    """Extract element selectors from agent history"""
    selectors = {}
    xpath_pattern = re.compile(r"The xpath of the element is (.*)")
    
    for content in history_data.get('extracted_content', []):
        if isinstance(content, str):
            match = xpath_pattern.search(content)
            if match:
                xpath = match.group(1)
                # Create a meaningful name based on surrounding context
                name = "element_" + str(len(selectors) + 1)
                selectors[name] = xpath
    
    return selectors

def analyze_actions(history_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze the actions performed by the agent to create step implementations"""
    actions = []
    
    for i, action_name in enumerate(history_data.get('action_names', [])):
        action_info = {
            "name": action_name,
            "index": i,
            "type": "unknown"
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
        elif "save job details" in action_name.lower():
            action_info["type"] = "custom_save"
        
        actions.append(action_info)
    
    return actions

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

# def generate_single_file_automation(gherkin_steps: str, history_data: Dict[str, Any]) -> str:
#     """Generate a single Python file with PyTest BDD automation code"""
    
#     # Extract feature name from Gherkin
#     feature_name = "Automated_Test"
#     feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
#     if feature_match:
#         feature_name = feature_match.group(1).strip().replace(" ", "_")
    
#     # Extract selectors and actions
#     selectors = extract_selectors_from_history(history_data)
#     actions = analyze_actions(history_data)
    
#     # Get URLs visited
#     urls = history_data.get('urls', [])
#     base_url = urls[0] if urls else "https://example.com"
    
#     # Create prompt for single file automation code
#     code_file_prompt = f"""
#     Generate a SINGLE Python file with PyTest BDD automation code based on the following Gherkin steps and browser interactions:
    
#     ```gherkin
#     {gherkin_steps}
#     ```
    
#     Agent execution details:
#     - Base URL: {base_url}
#     - Element selectors: {json.dumps(selectors, indent=2)}
#     - Actions performed: {json.dumps(actions, indent=2)}
#     - Extracted content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
    
#     Requirements:
#     1. The file should include ALL necessary imports
#     2. Include the Gherkin feature as a docstring at the top of the file
#     3. Create step definitions for each step in the Gherkin scenarios
#     4. Use Selenium WebDriver for browser automation (not Playwright)
#     5. Include proper wait strategies and error handling
#     6. Add helper functions for common operations
#     7. Include a main function to run the tests
#     8. Add clear comments throughout the code
#     9. Make it a single, self-contained file that can be run directly
    
#     The code should follow best practices for PyTest BDD and Selenium automation.
#     Return ONLY the Python code without any additional explanation.
#     """
    
#     try:
#         # Generate the single file
#         code_response = code_gen_agent.run(code_file_prompt)
#         code_content = extract_code_content(code_response.content)
        
#         return code_content
        
#     except Exception as e:
#         st.error(f"Error generating test file: {str(e)}")
#         raise

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

def extract_code_content(text: str) -> str:
    """Extract code from markdown code blocks if present"""
    code_block_pattern = re.compile(r"```(?:python|gherkin|javascript|java|robot)?\n(.*?)```", re.DOTALL)
    match = code_block_pattern.search(text)
    
    if match:
        return match.group(1).strip()
    return text.strip()

# Dictionary mapping framework names to their generation functions
FRAMEWORK_GENERATORS = {
    "Selenium + PyTest BDD (Python)": generate_selenium_pytest_bdd,
    "Playwright (Python)": generate_playwright_python,
    "Cypress (JavaScript)": generate_cypress_js,
    "Robot Framework": generate_robot_framework,
    "Selenium + Cucumber (Java)": generate_java_selenium
}

# Dictionary mapping framework names to their file extensions
FRAMEWORK_EXTENSIONS = {
    "Selenium + PyTest BDD (Python)": "py",
    "Playwright (Python)": "py",
    "Cypress (JavaScript)": "js",
    "Robot Framework": "robot",
    "Selenium + Cucumber (Java)": "java"
}

# Framework descriptions
framework_descriptions = {
    "Selenium + PyTest BDD (Python)": "Popular Python testing framework combining Selenium WebDriver with PyTest BDD for behavior-driven development. Best for Python developers who want strong test organization and reporting.",
    "Playwright (Python)": "Modern, powerful browser automation framework with built-in async support and cross-browser testing capabilities. Excellent for modern web applications and complex scenarios.",
    "Cypress (JavaScript)": "Modern, JavaScript-based end-to-end testing framework with real-time reloading and automatic waiting. Perfect for front-end developers and modern web applications.",
    "Robot Framework": "Keyword-driven testing framework that uses simple, tabular syntax. Great for teams with mixed technical expertise and for creating readable test cases.",
    "Selenium + Cucumber (Java)": "Robust combination of Selenium WebDriver with Cucumber for Java, supporting BDD. Ideal for Java teams and enterprise applications."
}

# Streamlit UI
st.set_page_config(page_title="User Story to Test Automation", layout="wide")

# Framework selection in sidebar
st.sidebar.subheader("Automation Framework")
selected_framework = st.sidebar.selectbox(
    "Select framework:", 
    list(FRAMEWORK_GENERATORS.keys()),
    index=0
)

# Show framework description in sidebar
st.sidebar.markdown(f"**Framework Details:**")
st.sidebar.info(framework_descriptions[selected_framework])

# Main UI
st.title("QA Automation: User Story to Selenium PyTest BDD")
user_story = st.text_area(
    "Enter your user story:",
    placeholder="e.g., As a user, I want to log in with valid credentials so that I can access my account."
)

col1, col2, col3 = st.columns(3)
with col1:
    generate_btn = st.button("Generate Gherkin Scenarios")
with col2:
    execute_btn = st.button("Execute Test Steps")
with col3:
    generate_code_btn = st.button("Generate Automation Code")

if generate_btn and user_story:
    with st.spinner("Generating Gherkin scenarios..."):
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
        run_response = qa_agent.run(prompt)
        generated_steps = run_response.content
        st.session_state.generated_steps = generated_steps
        st.code(generated_steps, language="gherkin")
        st.success("Gherkin scenarios generated!")

if execute_btn:
    if "generated_steps" not in st.session_state:
        st.error("Please generate Gherkin scenarios first.")
    else:
        # Modify the execute_test function to store more detailed information
        async def execute_test(steps: str):
            try:
                browser = Browser()
                
                async with await browser.new_context() as context:
                    # Parse the Gherkin content to extract scenarios
                    scenarios = []
                    current_scenario = []
                    for line in steps.split('\n'):
                        if line.strip().startswith('Scenario:'):
                            if current_scenario:
                                scenarios.append('\n'.join(current_scenario))
                            current_scenario = [line]
                        elif current_scenario:
                            current_scenario.append(line)
                    if current_scenario:
                        scenarios.append('\n'.join(current_scenario))
                    
                    # Execute each scenario separately
                    all_results = []
                    all_actions = []
                    all_extracted_content = []
                    element_xpath_map = {}
                    
                    for scenario in scenarios:
                        browser_agent = BrowserAgent(
                            task=f"""
                            Execute the following Gherkin scenario with comprehensive logging and detailed actions.
                            For each interactive element you encounter, use the "Get XPath of element using index" action 
                            to capture its XPath. Get the XPath BEFORE performing any actions on the element.
                            Capture element selectors, properties, and states during execution.
                            
                            {scenario}
                            """,
                            llm=ChatGoogleGenerativeAI(model='gemini-1.5-flash', api_key=os.environ.get("GOOGLE_API_KEY")),
                            browser=browser,
                            controller=controller,
                        )
                        
                        # Execute and collect results
                        history = await browser_agent.run()
                        history.save_to_file("agent_history.json")
                        result = history.final_result()
                        if isinstance(result, str):
                            # Convert string result to JSON format
                            result = {"status": result, "details": "Execution completed"}
                        all_results.append(result)
                        
                        # Log all model actions for debugging
                        st.write("Debug - Model Actions:", history.model_actions())
                        
                        # Process model actions to extract element details
                        for i, action_data in enumerate(history.model_actions()):
                            action_name = history.action_names()[i] if i < len(history.action_names()) else "Unknown Action"
                            
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
                                        element_xpath_map[element_index] = xpath
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
                                                    element_xpath_map[element_index] = xpath
                                                    action_detail["element_details"]["xpath"] = xpath
                                                    
                            all_actions.append(action_detail)
                        
                        # Also extract from content if available
                        for content in history.extracted_content():
                            all_extracted_content.append(content)
                            
                            # Look for XPath information in extracted content
                            if isinstance(content, str):
                                xpath_match = re.search(r"The xpath of the element is (.+)", content)
                                if xpath_match:
                                    xpath = xpath_match.group(1)
                                    # Try to match with an element index from previous actions
                                    index_match = re.search(r"element (\d+)", content)
                                    if index_match:
                                        element_index = int(index_match.group(1))
                                        element_xpath_map[element_index] = xpath
                    
                    # Save combined history to session state
                    st.session_state.history = {
                        "urls": history.urls(),
                        "action_names": history.action_names(),
                        "detailed_actions": all_actions,
                        "element_xpaths": element_xpath_map,
                        "extracted_content": all_extracted_content,
                        "errors": history.errors(),
                        "model_actions": history.model_actions(),
                        "execution_date": st.session_state.get("execution_date", "Unknown")
                    }
                    
                    # Display test execution details
                    st.success("Test execution completed!")
                    
                    # Display key information in tabs
                    tab1, tab2, tab3, tab4 = st.tabs(["Results", "Actions", "Elements", "Details"])
                    with tab1:
                        for i, result in enumerate(all_results):
                            st.write(f"### Scenario {i+1}")
                            st.json(result)
                    
                    with tab2:
                        st.write("### Actions Performed")
                        for i, action in enumerate(all_actions):
                            action_text = f"{i+1}. {action['name']}"
                            if 'element_details' in action and action['element_details']:
                                if 'xpath' in action['element_details']:
                                    action_text += f" (XPath: {action['element_details']['xpath']})"
                                elif 'index' in action['element_details']:
                                    action_text += f" (Element index: {action['element_details']['index']})"
                            st.write(action_text)
                    
                    with tab3:
                        st.write("### Element Details")
                        if element_xpath_map:
                            # Create a dataframe for better visualization
                            import pandas as pd
                            element_df = pd.DataFrame([
                                {"Element Index": index, "XPath": xpath}
                                for index, xpath in element_xpath_map.items()
                            ])
                            st.dataframe(element_df)
                        else:
                            st.info("No element XPaths were captured during test execution.")
                            
                            # Display raw DOM information for debugging
                            st.write("### Raw DOM Information")
                            for i, action_data in enumerate(history.model_actions()):
                                if "interacted_element" in action_data and action_data["interacted_element"]:
                                    st.write(f"Action {i}: {history.action_names()[i] if i < len(history.action_names()) else 'Unknown'}")
                                    st.code(str(action_data["interacted_element"]))
                            
                    with tab4:
                        st.write("### Extracted Content")
                        for content in all_extracted_content:
                            st.write(content)
                            
            except Exception as e:
                st.error(f"An error occurred during test execution: {str(e)}")
                st.error("Stack trace:", exc_info=True)
                
        st.session_state.execution_date = "February 26, 2025"
        asyncio.run(execute_test(st.session_state.generated_steps))

if generate_code_btn:
    if "generated_steps" not in st.session_state or "history" not in st.session_state:
        st.error("Please generate and execute Gherkin scenarios first.")
    else:
        with st.spinner(f"Generating {selected_framework} automation code..."):
            try:
                # Get the appropriate generator function
                generator_function = FRAMEWORK_GENERATORS[selected_framework]
                
                # Generate automation code
                automation_code = generator_function(
                    st.session_state.generated_steps,
                    st.session_state.history
                )
                
                # Store in session state
                st.session_state.automation_code = automation_code
                
                # Display code
                st.subheader(f"Generated {selected_framework} Automation Code")
                
                # Use appropriate language for syntax highlighting
                code_language = "python"
                if selected_framework == "Cypress (JavaScript)":
                    code_language = "javascript"
                elif selected_framework == "Robot Framework":
                    code_language = "robot"
                elif selected_framework == "Selenium + Cucumber (Java)":
                    code_language = "java"
                
                st.code(automation_code, language=code_language)
                
                # Extract feature name for file naming
                feature_name = "automated_test"
                feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", st.session_state.generated_steps)
                if feature_match:
                    feature_name = feature_match.group(1).strip().replace(" ", "_").lower()
                
                # Get appropriate file extension
                file_ext = FRAMEWORK_EXTENSIONS[selected_framework]
                
                # Add download button
                st.download_button(
                    label=f"📥 Download {selected_framework} Code",
                    data=automation_code,
                    file_name=f"{feature_name}_automation.{file_ext}",
                    mime="text/plain",
                )
                
                st.success(f"{selected_framework} code generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating {selected_framework} code: {str(e)}")
                st.error("Stack trace:", exc_info=True)

if __name__ == "__main__":
    # For local execution
    pass