import re
from typing import Dict, Any, Union
import json
import streamlit as st

from src.Agents.agents import (
    gherkhin_agent, # Import gherkhin_agent
    code_gen_agent,
    manual_test_case_agent,# Import the new agent
    user_story_enhancement_agent)

from src.Utilities.utils import (
    extract_selectors_from_history,
    analyze_actions)

def generate_gherkin_scenarios(manual_test_cases_markdown: str, model_instance: Union[object, Any]) -> str:
    """Generate Gherkin scenarios from manual test cases using the QA agent"""
    try:
        # Dynamically assign the model instance
        gherkhin_agent.model = model_instance
        
        # The QA agent's description, instructions, and expected_output handle the Gherkin generation logic.
        # We need to provide the manual test cases as the input to the agent's run method.
        run_response = gherkhin_agent.run(manual_test_cases_markdown)
        # Extract the content from the agent's response
        gherkin_content = extract_code_content(run_response.content)
        return gherkin_content
    except Exception as e:
        st.error(f"Error generating Gherkin scenarios: {str(e)}")
        raise

def generate_manual_test_cases(user_story: str, model_instance: Union[object, Any]) -> str:
    """Generate manual test cases from a user story using the manual test case agent"""
    try:
        # Dynamically assign the model instance
        manual_test_case_agent.model = model_instance
        
        run_response = manual_test_case_agent.run(user_story)
        # The manual test case agent is expected to return markdown
        manual_test_cases_content = extract_code_content(run_response.content)
        return manual_test_cases_content
    except Exception as e:
        st.error(f"Error generating manual test cases: {str(e)}")
        raise

def enhance_user_story(user_story: str, model_instance: Union[object, Any]) -> str:
    """Enhance a raw user story using the user story enhancement agent"""
    try:
        # Dynamically assign the model instance
        user_story_enhancement_agent.model = model_instance
        
        # Check if the input looks like a Jira ticket number (e.g., PROJECT-123)
        import re
        jira_ticket_pattern = re.compile(r"^[A-Z]+-\d+$")
        
        if jira_ticket_pattern.match(user_story.strip()):
            # It looks like a Jira ticket number, add context about Jira tools
            user_story = f"Please fetch the details for Jira ticket {user_story} and enhance it into a proper user story."
        
        run_response = user_story_enhancement_agent.run(user_story)
        # The agent is expected to return the enhanced user story text
        enhanced_story_content = run_response.content
        return enhanced_story_content
    except Exception as e:
        st.error(f"Error enhancing user story: {str(e)}")
        raise

def extract_code_content(text: str) -> str:
    """Extract code from markdown code blocks if present"""
    # Look for content between triple backticks with optional language identifier
    code_block_pattern = re.compile(r"```(?:python|gherkin|javascript|java|robot|markdown)?\n([\s\S]*?)```", re.DOTALL)
    match = code_block_pattern.search(text)

    if match:
        return match.group(1).strip()
    return text.strip()

def generate_selenium_pytest_bdd(gherkin_steps: str, history_data: Dict[str, Any], model_instance: Union[object, Any]) -> str:
    """Generate a single Python file with Selenium PyTest BDD automation code using enhanced element tracking"""

    # Extract feature name from Gherkin (optional, for context)
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    feature_name = feature_match.group(1).strip() if feature_match else "Automated Test"

    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"

    # Use enhanced element tracking data if available
    if 'element_interactions' in history_data:
        # Enhanced tracking data
        element_data = history_data['element_interactions']
        automation_data = history_data.get('automation_script_data', {})
        
        # Get framework-specific exports for Selenium
        if 'framework_exports' in history_data and 'selenium' in history_data['framework_exports']:
            selenium_export = history_data['framework_exports']['selenium']
        else:
            selenium_export = {}
        
        code_file_prompt = f"""
        Generate comprehensive Selenium PyTest BDD code using enhanced element tracking data:

        Gherkin Steps:
        ```gherkin
        {gherkin_steps}
        ```

        Enhanced Element Tracking Data:
        - Base URL: {base_url}
        - Total Elements Interacted: {element_data.get('unique_elements', 0)}
        - Action Types: {element_data.get('action_types', [])}
        - Element Library: {json.dumps(automation_data.get('element_library', {}), indent=2)}
        - Action Sequence: {json.dumps(automation_data.get('action_sequence', []), indent=2)}
        - Selenium Framework Export: {json.dumps(selenium_export, indent=2)}
        
        IMPORTANT: Use the provided element selectors and interaction details to generate robust, production-ready test code.
        Prioritize data-testid, ID, and name attributes over XPath when available.
        """
    else:
        # Fallback to legacy extraction for backward compatibility
        selectors = extract_selectors_from_history(history_data)
        actions = analyze_actions(history_data)
        
        code_file_prompt = f"""
        Generate Selenium PyTest BDD code based on the following:

        Gherkin Steps:
        ```gherkin
        {gherkin_steps}
        ```

        Agent Execution Details:
        - Base URL: {base_url}
        - Element Selectors: {json.dumps(selectors, indent=2)}
        - Actions Performed: {json.dumps(actions, indent=2)}
        - Extracted Content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
        """

    try:
        # Dynamically assign the model instance
        code_gen_agent.model = model_instance
        
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)

        return code_content

    except Exception as e:
        st.error(f"Error generating Selenium PyTest BDD code: {str(e)}")
        raise

def generate_playwright_python(gherkin_steps: str, history_data: Dict[str, Any], model_instance: Union[object, Any]) -> str:
    """Generate a single Python file with Playwright automation code using enhanced element tracking"""

    # Extract feature name from Gherkin (optional, for context)
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    feature_name = feature_match.group(1).strip() if feature_match else "Automated Test"

    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"

    # Use enhanced element tracking data if available
    if 'element_interactions' in history_data:
        # Enhanced tracking data
        element_data = history_data['element_interactions']
        automation_data = history_data.get('automation_script_data', {})
        
        # Get framework-specific exports for Playwright
        if 'framework_exports' in history_data and 'playwright' in history_data['framework_exports']:
            playwright_export = history_data['framework_exports']['playwright']
        else:
            playwright_export = {}
        
        code_file_prompt = f"""
        Generate comprehensive Playwright Python code using enhanced element tracking data:

        Gherkin Steps:
        ```gherkin
        {gherkin_steps}
        ```

        Enhanced Element Tracking Data:
        - Base URL: {base_url}
        - Total Elements Interacted: {element_data.get('unique_elements', 0)}
        - Action Types: {element_data.get('action_types', [])}
        - Element Library: {json.dumps(automation_data.get('element_library', {}), indent=2)}
        - Action Sequence: {json.dumps(automation_data.get('action_sequence', []), indent=2)}
        - Playwright Framework Export: {json.dumps(playwright_export, indent=2)}
        
        IMPORTANT: Use Playwright-specific selectors like data-testid selectors.
        Generate modern async/await Playwright code with proper wait conditions.
        """
    else:
        # Fallback to legacy extraction
        selectors = extract_selectors_from_history(history_data)
        actions = analyze_actions(history_data)
        
        code_file_prompt = f"""
        Generate Playwright Python code based on the following:

        Gherkin Steps:
        ```gherkin
        {gherkin_steps}
        ```

        Agent Execution Details:
        - Base URL: {base_url}
        - Element Selectors: {json.dumps(selectors, indent=2)}
        - Actions Performed: {json.dumps(actions, indent=2)}
        - Extracted Content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
        """

    try:
        # Dynamically assign the model instance
        code_gen_agent.model = model_instance
        
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)

        return code_content

    except Exception as e:
        st.error(f"Error generating Playwright code: {str(e)}")
        raise

def generate_cypress_js(gherkin_steps: str, history_data: Dict[str, Any], model_instance: Union[object, Any]) -> str:
    """Generate a single JavaScript file with Cypress automation code using enhanced element tracking"""

    # Extract feature name from Gherkin (optional, for context)
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    feature_name = feature_match.group(1).strip() if feature_match else "Automated Test"

    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"

    # Use enhanced element tracking data if available
    if 'element_interactions' in history_data:
        # Enhanced tracking data
        element_data = history_data['element_interactions']
        automation_data = history_data.get('automation_script_data', {})
        
        # Get framework-specific exports for Cypress
        if 'framework_exports' in history_data and 'cypress' in history_data['framework_exports']:
            cypress_export = history_data['framework_exports']['cypress']
        else:
            cypress_export = {}
        
        code_file_prompt = f"""
        Generate comprehensive Cypress JavaScript code using enhanced element tracking data:

        Gherkin Steps:
        ```gherkin
        {gherkin_steps}
        ```

        Enhanced Element Tracking Data:
        - Base URL: {base_url}
        - Total Elements Interacted: {element_data.get('unique_elements', 0)}
        - Action Types: {element_data.get('action_types', [])}
        - Element Library: {json.dumps(automation_data.get('element_library', {}), indent=2)}
        - Action Sequence: {json.dumps(automation_data.get('action_sequence', []), indent=2)}
        - Cypress Framework Export: {json.dumps(cypress_export, indent=2)}
        
        IMPORTANT: Use Cypress-specific selectors like data-cy attributes.
        Generate modern Cypress commands with proper chaining and assertions.
        """
    else:
        # Fallback to legacy extraction
        selectors = extract_selectors_from_history(history_data)
        actions = analyze_actions(history_data)
        
        code_file_prompt = f"""
        Generate Cypress JavaScript code based on the following:

        Gherkin Steps:
        ```gherkin
        {gherkin_steps}
        ```

        Agent Execution Details:
        - Base URL: {base_url}
        - Element Selectors: {json.dumps(selectors, indent=2)}
        - Actions Performed: {json.dumps(actions, indent=2)}
        - Extracted Content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
        """

    try:
        # Dynamically assign the model instance
        code_gen_agent.model = model_instance
        
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)

        return code_content

    except Exception as e:
        st.error(f"Error generating Cypress code: {str(e)}")
        raise
        # Dynamically assign the model instance
        code_gen_agent.model = model_instance
        
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)

        return code_content

    except Exception as e:
        st.error(f"Error generating Cypress code: {str(e)}")
        raise

def generate_robot_framework(gherkin_steps: str, history_data: Dict[str, Any], model_instance: Union[object, Any]) -> str:
    """Generate Robot Framework test file using enhanced element tracking"""

    # Extract feature name from Gherkin (optional, for context)
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    feature_name = feature_match.group(1).strip() if feature_match else "Automated Test"

    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"

    # Use enhanced element tracking data if available
    if 'element_interactions' in history_data:
        # Enhanced tracking data
        element_data = history_data['element_interactions']
        automation_data = history_data.get('automation_script_data', {})
        
        code_file_prompt = f"""
        Generate comprehensive Robot Framework code using enhanced element tracking data:

        Gherkin Steps:
        ```gherkin
        {gherkin_steps}
        ```

        Enhanced Element Tracking Data:
        - Base URL: {base_url}
        - Total Elements Interacted: {element_data.get('unique_elements', 0)}
        - Action Types: {element_data.get('action_types', [])}
        - Element Library: {json.dumps(automation_data.get('element_library', {}), indent=2)}
        - Action Sequence: {json.dumps(automation_data.get('action_sequence', []), indent=2)}
        
        IMPORTANT: Generate Robot Framework syntax with proper keywords and variables.
        Use SeleniumLibrary keywords and create reusable custom keywords.
        """
    else:
        # Fallback to legacy extraction
        selectors = extract_selectors_from_history(history_data)
        actions = analyze_actions(history_data)
        
        code_file_prompt = f"""
        Generate Robot Framework code based on the following:

        Gherkin Steps:
        ```gherkin
        {gherkin_steps}
        ```

        Agent Execution Details:
        - Base URL: {base_url}
        - Element Selectors: {json.dumps(selectors, indent=2)}
        - Actions Performed: {json.dumps(actions, indent=2)}
        - Extracted Content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
        """

    try:
        # Dynamically assign the model instance
        code_gen_agent.model = model_instance
        
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)

        return code_content

    except Exception as e:
        st.error(f"Error generating Robot Framework code: {str(e)}")
        raise

def generate_java_selenium(gherkin_steps: str, history_data: Dict[str, Any], model_instance: Union[object, Any]) -> str:
    """Generate a Java file with Selenium and Cucumber automation code using enhanced element tracking"""

    # Extract feature name from Gherkin (optional, for context)
    feature_match = re.search(r"Feature:\s*(.+?)(?:\n|$)", gherkin_steps)
    feature_name = feature_match.group(1).strip() if feature_match else "Automated Test"

    # Get URLs visited
    urls = history_data.get('urls', [])
    base_url = urls[0] if urls else "https://example.com"

    # Use enhanced element tracking data if available
    if 'element_interactions' in history_data:
        # Enhanced tracking data
        element_data = history_data['element_interactions']
        automation_data = history_data.get('automation_script_data', {})
        
        # Get framework-specific exports for Selenium (works for Java too)
        if 'framework_exports' in history_data and 'selenium' in history_data['framework_exports']:
            selenium_export = history_data['framework_exports']['selenium']
        else:
            selenium_export = {}
        
        code_file_prompt = f"""
        Generate comprehensive Java Selenium Cucumber code using enhanced element tracking data:

        Gherkin Steps:
        ```gherkin
        {gherkin_steps}
        ```

        Enhanced Element Tracking Data:
        - Base URL: {base_url}
        - Total Elements Interacted: {element_data.get('unique_elements', 0)}
        - Action Types: {element_data.get('action_types', [])}
        - Element Library: {json.dumps(automation_data.get('element_library', {}), indent=2)}
        - Action Sequence: {json.dumps(automation_data.get('action_sequence', []), indent=2)}
        - Selenium Framework Export: {json.dumps(selenium_export, indent=2)}
        
        IMPORTANT: Generate Java code with proper Page Object Model pattern.
        Use WebDriverWait and expected conditions for robust element interactions.
        Include proper exception handling and logging.
        """
    else:
        # Fallback to legacy extraction
        selectors = extract_selectors_from_history(history_data)
        actions = analyze_actions(history_data)
        
        code_file_prompt = f"""
        Generate Java Selenium Cucumber code based on the following:

        Gherkin Steps:
        ```gherkin
        {gherkin_steps}
        ```

        Agent Execution Details:
        - Base URL: {base_url}
        - Element Selectors: {json.dumps(selectors, indent=2)}
        - Actions Performed: {json.dumps(actions, indent=2)}
        - Extracted Content: {json.dumps(history_data.get('extracted_content', []), indent=2)}
        """

    try:
        # Dynamically assign the model instance
        code_gen_agent.model = model_instance
        
        # Generate the single file
        code_response = code_gen_agent.run(code_file_prompt)
        code_content = extract_code_content(code_response.content)

        return code_content

    except Exception as e:
        st.error(f"Error generating Java Selenium Cucumber code: {str(e)}")
        raise
