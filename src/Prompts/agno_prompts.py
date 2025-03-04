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

def generate_selenium_pytest_bdd(gherkin_steps: str, history_data: Dict[str, Any]) -> str:
    """Generate a single Python file with Selenium PyTest BDD automation code"""
    
    # Extract feature name from Gherkin
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    if feature_match:
        feature_name = feature_match.group(1).strip().replace(" ", "_")
    
    # Extract selectors and actions
    selectors = extract_selectors_from_history(history_data)
    actions = analyze_actions(history_data)
    
    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"
    
    # Create prompt for Selenium PyTest BDD code
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
    
    Requirements:
    1. The file should include ALL necessary imports for Selenium and PyTest BDD
    2. Include the Gherkin feature as a docstring at the top of the file
    3. Create step definitions for each step in the Gherkin scenarios
    4. Use Selenium WebDriver for browser automation
    5. Include proper wait strategies and error handling
    6. Add helper functions for common operations
    7. Include a main function to run the tests
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

