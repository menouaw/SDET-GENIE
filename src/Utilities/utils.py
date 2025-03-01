from browser_use import Browser, Agent as BrowserAgent, Controller, ActionResult

import re

from pydantic import BaseModel
from typing import Dict, Any, Optional, List

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
