"""
Element tracking utility for capturing browser interactions for automation script generation.
This module extends browser-use's event system to track element details during test execution.
"""

import json
import time
from typing import Dict, Any, List, Optional
from browser_use.browser.events import ClickElementEvent, TypeTextEvent
from browser_use.dom.views import EnhancedDOMTreeNode


class ElementTracker:
    """Tracks element interactions during browser automation for script generation."""
    
    def __init__(self):
        self.interactions: List[Dict[str, Any]] = []
        self.execution_context: Dict[str, Any] = {
            "visited_urls": [],
            "current_url": "",
            "session_data": {}
        }
        
    def update_context(self, context: Dict[str, Any]):
        """Update the execution context."""
        self.execution_context.update(context)
        
    def extract_element_details(self, node: EnhancedDOMTreeNode) -> Dict[str, Any]:
        """Extract comprehensive element details from EnhancedDOMTreeNode for production automation."""
        if not node:
            return {}
        
        # Base element information
        details = {
            "element_index": node.element_index,
            "node_id": node.node_id,
            "backend_node_id": node.backend_node_id,
            "tag_name": node.node_name.lower() if node.node_name else "",
            "node_type": str(node.node_type) if node.node_type else "",
            "attributes": node.attributes or {},
            "is_visible": node.is_visible,
            "is_scrollable": node.is_scrollable,
            "frame_id": node.frame_id,
            "session_id": str(node.session_id) if node.session_id else None,
            "execution_context": self.execution_context.copy()  # Add context to element details
        }
        
        # Position and bounds information
        if node.absolute_position:
            details["absolute_position"] = {
                "x": node.absolute_position.x,
                "y": node.absolute_position.y,
                "width": node.absolute_position.width,
                "height": node.absolute_position.height
            }
        
        # Enhanced snapshot data for comprehensive details
        if node.snapshot_node:
            details["snapshot_data"] = {
                "is_clickable": node.snapshot_node.is_clickable,
                "cursor_style": node.snapshot_node.cursor_style
            }
            
            # Client rectangles (viewport coordinates)
            if node.snapshot_node.clientRects:
                details["client_rect"] = {
                    "x": node.snapshot_node.clientRects.x,
                    "y": node.snapshot_node.clientRects.y,
                    "width": node.snapshot_node.clientRects.width,
                    "height": node.snapshot_node.clientRects.height
                }
            
            # Computed styles for enhanced automation
            if node.snapshot_node.computed_styles:
                details["computed_styles"] = node.snapshot_node.computed_styles
        
        # Accessibility information
        if node.ax_node:
            details["accessibility"] = {
                "role": node.ax_node.role,
                "name": node.ax_node.name,
                "description": node.ax_node.description,
                "ignored": node.ax_node.ignored
            }
            
            # Extract accessibility properties
            if node.ax_node.properties:
                ax_props = {}
                for prop in node.ax_node.properties:
                    ax_props[prop.name] = prop.value
                details["accessibility"]["properties"] = ax_props
        
        # Extract key attributes for selector generation
        attrs = node.attributes or {}
        details.update({
            "id": attrs.get("id", ""),
            "class": attrs.get("class", ""),
            "name": attrs.get("name", ""),
            "type": attrs.get("type", ""),
            "placeholder": attrs.get("placeholder", ""),
            "value": attrs.get("value", ""),
            "role": attrs.get("role", ""),
            "aria_label": attrs.get("aria-label", ""),
            "data_testid": attrs.get("data-testid", ""),
            "data_cy": attrs.get("data-cy", ""),
            "title": attrs.get("title", "")
        })
        
        # Get meaningful text content using browser-use's built-in method
        if hasattr(node, 'get_meaningful_text_for_llm'):
            details["meaningful_text"] = node.get_meaningful_text_for_llm()
        else:
            details["meaningful_text"] = node.get_all_children_text()[:200]  # Limit text length
        
        # Generate XPath using browser-use's built-in method
        if hasattr(node, 'xpath'):
            details["built_in_xpath"] = node.xpath
        
        # Generate comprehensive selectors for automation scripts
        selectors = self._generate_production_selectors(details, node)
        details["selectors"] = selectors
        
        return details
    
    def _generate_production_selectors(self, element_details: Dict[str, Any], node: EnhancedDOMTreeNode) -> Dict[str, str]:
        """Generate comprehensive selectors for production automation frameworks."""
        selectors = {}
        
        tag = element_details.get("tag_name", "")
        element_id = element_details.get("id", "")
        class_name = element_details.get("class", "")
        name = element_details.get("name", "")
        placeholder = element_details.get("placeholder", "")
        data_testid = element_details.get("data_testid", "")
        data_cy = element_details.get("data_cy", "")
        aria_label = element_details.get("aria_label", "")
        role = element_details.get("role", "")
        type_attr = element_details.get("type", "")
        meaningful_text = element_details.get("meaningful_text", "")[:50]  # Limit for selectors
        
        # Priority 1: Test automation attributes (most reliable)
        if data_testid:
            selectors["data_testid"] = f"[data-testid='{data_testid}']"
            selectors["css_data_testid"] = f"{tag}[data-testid='{data_testid}']" if tag else f"[data-testid='{data_testid}']"
            selectors["xpath_data_testid"] = f"//{tag}[@data-testid='{data_testid}']" if tag else f"//*[@data-testid='{data_testid}']"
            # Playwright-specific selector
            selectors["playwright_testid"] = f"[data-testid='{data_testid}']"
        
        if data_cy:
            selectors["data_cy"] = f"[data-cy='{data_cy}']"
            selectors["css_data_cy"] = f"{tag}[data-cy='{data_cy}']" if tag else f"[data-cy='{data_cy}']"
            selectors["xpath_data_cy"] = f"//{tag}[@data-cy='{data_cy}']" if tag else f"//*[@data-cy='{data_cy}']"
        
        # Priority 2: ID selectors (highly reliable)
        if element_id:
            selectors["id"] = f"#{element_id}"
            selectors["css_id"] = f"#{element_id}"
            selectors["xpath_id"] = f"//{tag}[@id='{element_id}']" if tag else f"//*[@id='{element_id}']"
        
        # Priority 3: Name attribute (good for forms)
        if name:
            selectors["name"] = f"[name='{name}']"
            selectors["css_name"] = f"{tag}[name='{name}']" if tag else f"[name='{name}']"
            selectors["xpath_name"] = f"//{tag}[@name='{name}']" if tag else f"//*[@name='{name}']"
        
        # Priority 4: Accessibility attributes
        if aria_label:
            selectors["css_aria_label"] = f"{tag}[aria-label='{aria_label}']" if tag else f"[aria-label='{aria_label}']"
            selectors["xpath_aria_label"] = f"//{tag}[@aria-label='{aria_label}']" if tag else f"//*[@aria-label='{aria_label}']"
        
        if role:
            selectors["css_role"] = f"{tag}[role='{role}']" if tag else f"[role='{role}']"
            selectors["xpath_role"] = f"//{tag}[@role='{role}']" if tag else f"//*[@role='{role}']"
        
        # Priority 5: Form-specific attributes
        if type_attr and tag in ['input', 'button']:
            selectors["css_type"] = f"{tag}[type='{type_attr}']"
            selectors["xpath_type"] = f"//{tag}[@type='{type_attr}']"
        
        if placeholder:
            selectors["css_placeholder"] = f"{tag}[placeholder='{placeholder}']" if tag else f"[placeholder='{placeholder}']"
            selectors["xpath_placeholder"] = f"//{tag}[@placeholder='{placeholder}']" if tag else f"//*[@placeholder='{placeholder}']"
        
        # Priority 6: Class-based selectors (less reliable but useful)
        if class_name:
            # Clean class names for CSS
            clean_classes = [cls.strip() for cls in class_name.split() if cls.strip()]
            if clean_classes:
                css_classes = ".".join(clean_classes)
                selectors["css_class"] = f"{tag}.{css_classes}" if tag else f".{css_classes}"
                # For XPath, use the full class attribute
                selectors["xpath_class"] = f"//{tag}[@class='{class_name}']" if tag else f"//*[@class='{class_name}']"
        
        # Priority 7: Text-based selectors (for buttons, links, etc.)
        if meaningful_text and meaningful_text.strip():
            clean_text = meaningful_text.strip().replace("'", "\"")
            if len(clean_text) > 2:  # Only for meaningful text
                selectors["xpath_text"] = f"//{tag}[contains(text(), '{clean_text}')]" if tag else f"//*[contains(text(), '{clean_text}')]"
                selectors["xpath_text_exact"] = f"//{tag}[text()='{clean_text}']" if tag else f"//*[text()='{clean_text}']"
        
        # Priority 8: Built-in XPath from browser-use (most comprehensive)
        if element_details.get("built_in_xpath"):
            selectors["browser_use_xpath"] = element_details["built_in_xpath"]
        
        # Priority 9: Fallback selectors using position/index
        if element_details.get("element_index"):
            selectors["index_based"] = f"[data-element-index='{element_details['element_index']}']"
        
        # Framework-specific selectors
        selectors.update(self._generate_framework_selectors(element_details, tag))
        
        return selectors
    
    def _generate_framework_selectors(self, element_details: Dict[str, Any], tag: str) -> Dict[str, str]:
        """Generate framework-specific selectors for different automation frameworks."""
        framework_selectors = {}
        
        # Playwright selectors (prioritizing data-testid)
        if element_details.get("data_testid"):
            framework_selectors["playwright_testid"] = f"[data-testid='{element_details['data_testid']}']"
        elif element_details.get("id"):
            framework_selectors["playwright_id"] = f"#{element_details['id']}"
        elif element_details.get("name"):
            framework_selectors["playwright_name"] = f"[name='{element_details['name']}']"
        
        # Add meaningful text for Playwright
        if element_details.get("meaningful_text"):
            clean_text = element_details["meaningful_text"].strip()[:30]
            if clean_text:
                framework_selectors["playwright_text"] = f"text={clean_text}"
        
        # Cypress selectors
        if element_details.get("data_cy"):
            framework_selectors["cypress_data_cy"] = f"[data-cy='{element_details['data_cy']}']"
        
        # Selenium WebDriver selectors (grouped by strategy)
        selenium_selectors = {}
        if element_details.get("id"):
            selenium_selectors["selenium_id"] = element_details["id"]
        if element_details.get("name"):
            selenium_selectors["selenium_name"] = element_details["name"]
        if element_details.get("class"):
            selenium_selectors["selenium_class_name"] = element_details["class"].split()[0] if element_details["class"] else ""
        
        framework_selectors.update(selenium_selectors)
        
        return framework_selectors
    
    def track_click(self, event: ClickElementEvent) -> None:
        """Track a click event."""
        element_details = self.extract_element_details(event.node)
        print(f"Tracking click event: {element_details}")  # Debug print
        
        interaction = {
            "action_type": "click",
            "timestamp": time.time(),
            "element_details": element_details,
            "metadata": {
                "button": event.button,
                "ctrl_held": event.while_holding_ctrl
            }
        }
        
        self.interactions.append(interaction)
        print(f"Total interactions after click: {len(self.interactions)}")  # Debug print
        
    def track_type_text(self, event: TypeTextEvent) -> None:
        """Track a type text event."""
        element_details = self.extract_element_details(event.node)
        print(f"Tracking type text event: {element_details}")  # Debug print
        
        interaction = {
            "action_type": "type_text",
            "timestamp": time.time(),
            "element_details": element_details,
            "metadata": {
                "text": event.text,
                "clear_existing": event.clear_existing
            }
        }
        
        self.interactions.append(interaction)
        print(f"Total interactions after type text: {len(self.interactions)}")  # Debug print
    
    def get_interactions(self) -> List[Dict[str, Any]]:
        """Get all tracked interactions."""
        return self.interactions.copy()
    
    def clear_interactions(self) -> None:
        """Clear all tracked interactions."""
        self.interactions = []
    
    def export_to_json(self, file_path: Optional[str] = None) -> str:
        """Export interactions to JSON format.
        
        Args:
            file_path: Optional file path to save JSON. If None, returns JSON string.
            
        Returns:
            JSON string representation of interactions
        """
        data = self.get_interactions_summary()
        json_str = json.dumps(data, indent=2, default=str)
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(json_str)
            except Exception as e:
                print(f"Error writing JSON file: {e}")
        
        return json_str
    
    def get_interactions_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of tracked interactions for script generation."""
        summary = {
            "total_interactions": len(self.interactions),
            "action_types": list(set(i["action_type"] for i in self.interactions)),
            "interactions": self.interactions,
            "unique_elements": len(set(
                i["element_details"].get("element_index", 0) 
                for i in self.interactions 
                if i["element_details"].get("element_index") is not None
            )),
            "automation_data": self.get_automation_script_data()
        }
        print(f"Interaction summary: {summary}")  # Debug print
        return summary
    
    def get_automation_script_data(self) -> Dict[str, Any]:
        """Get data specifically formatted for automation script generation."""
        script_data = {
            "page_interactions": [],
            "element_library": {},
            "action_sequence": [],
            "framework_selectors": {},
            "page_metadata": {
                "total_elements_interacted": len(set(
                    i["element_details"].get("element_index", 0) 
                    for i in self.interactions
                )),
                "interaction_types": list(set(i["action_type"] for i in self.interactions)),
                "generation_timestamp": time.time()
            }
        }
        
        for idx, interaction in enumerate(self.interactions):
            element_details = interaction["element_details"]
            element_index = element_details.get("element_index", 0)
            
            # Create action sequence entry
            action_entry = {
                "step_number": idx + 1,
                "action_type": interaction["action_type"],
                "element_reference": f"element_{element_index}",
                "selectors": element_details.get("selectors", {}),
                "metadata": interaction["metadata"],
                "element_context": {
                    "tag_name": element_details.get("tag_name", ""),
                    "meaningful_text": element_details.get("meaningful_text", ""),
                    "is_visible": element_details.get("is_visible", True),
                    "attributes": element_details.get("attributes", {})
                },
                "timestamp": interaction["timestamp"]
            }
            script_data["action_sequence"].append(action_entry)
            
            # Build element library for reuse
            element_key = f"element_{element_index}"
            if element_key not in script_data["element_library"]:
                script_data["element_library"][element_key] = {
                    "element_index": element_index,
                    "tag_name": element_details.get("tag_name", ""),
                    "selectors": element_details.get("selectors", {}),
                    "attributes": element_details.get("attributes", {}),
                    "position": element_details.get("absolute_position", {}),
                    "accessibility": element_details.get("accessibility", {}),
                    "meaningful_text": element_details.get("meaningful_text", ""),
                    "interactions_count": len([
                        i for i in self.interactions 
                        if i["element_details"].get("element_index") == element_index
                    ])
                }
            
            # Organize selectors by framework
            selectors = element_details.get("selectors", {})
            for selector_type, selector_value in selectors.items():
                if selector_type not in script_data["framework_selectors"]:
                    script_data["framework_selectors"][selector_type] = {}
                script_data["framework_selectors"][selector_type][element_key] = selector_value
        
        return script_data
    
    def export_for_framework(self, framework: str = "selenium") -> Dict[str, Any]:
        """Export interactions formatted for specific automation framework."""
        automation_data = self.get_automation_script_data()
        framework_data = {
            "framework": framework,
            "test_steps": [],
            "page_objects": {},
            "setup_data": {
                "required_imports": [],
                "setup_methods": [],
                "teardown_methods": []
            }
        }
        
        # Framework-specific formatting
        if framework.lower() == "selenium":
            framework_data["setup_data"]["required_imports"] = [
                "from selenium import webdriver",
                "from selenium.webdriver.common.by import By",
                "from selenium.webdriver.support.ui import WebDriverWait",
                "from selenium.webdriver.support import expected_conditions as EC"
            ]
        elif framework.lower() == "playwright":
            framework_data["setup_data"]["required_imports"] = [
                "from playwright.sync_api import Playwright, sync_playwright",
                "import pytest"
            ]
        elif framework.lower() == "cypress":
            framework_data["setup_data"]["required_imports"] = [
                "/// <reference types=\"cypress\" />"
            ]
        
        # Convert actions to framework-specific format
        for action in automation_data["action_sequence"]:
            step = self._convert_action_to_framework(action, framework)
            framework_data["test_steps"].append(step)
        
        # Generate page objects
        for element_key, element_data in automation_data["element_library"].items():
            page_object = self._generate_page_object_element(element_data, framework)
            framework_data["page_objects"][element_key] = page_object
        
        return framework_data
    
    def _convert_action_to_framework(self, action: Dict[str, Any], framework: str) -> Dict[str, Any]:
        """Convert a generic action to framework-specific format."""
        step = {
            "step_number": action["step_number"],
            "description": f"{action['action_type']} on {action['element_context']['tag_name']}",
            "action_type": action["action_type"],
            "element_reference": action["element_reference"]
        }
        
        if framework.lower() == "selenium":
            step["selenium_code"] = self._generate_selenium_code(action)
        elif framework.lower() == "playwright":
            step["playwright_code"] = self._generate_playwright_code(action)
        elif framework.lower() == "cypress":
            step["cypress_code"] = self._generate_cypress_code(action)
        
        return step
    
    def _generate_selenium_code(self, action: Dict[str, Any]) -> str:
        """Generate Selenium-specific code for an action."""
        selectors = action["selectors"]
        action_type = action["action_type"]
        
        # Choose best selector
        if "selenium_id" in selectors:
            locator = f'By.ID, "{selectors["selenium_id"]}"'
        elif "selenium_name" in selectors:
            locator = f'By.NAME, "{selectors["selenium_name"]}"'
        elif "css_id" in selectors:
            locator = f'By.CSS_SELECTOR, "{selectors["css_id"]}"'
        elif "css_data_testid" in selectors:
            locator = f'By.CSS_SELECTOR, "{selectors["css_data_testid"]}"'
        elif "xpath_id" in selectors:
            locator = f'By.XPATH, "{selectors["xpath_id"]}"'
        else:
            locator = f'By.TAG_NAME, "{action["element_context"]["tag_name"]}"'
        
        if action_type == "click":
            return f"driver.find_element({locator}).click()"
        elif action_type == "type_text":
            text = action["metadata"].get("text", "")
            return f"driver.find_element({locator}).send_keys('{text}')"
        
        return f"# {action_type} action on element"
    
    def _generate_playwright_code(self, action: Dict[str, Any]) -> str:
        """Generate Playwright-specific code for an action."""
        selectors = action["selectors"]
        action_type = action["action_type"]
        
        # Choose best selector for Playwright
        if "playwright_testid" in selectors:
            selector = selectors["playwright_testid"]
        elif "id" in selectors:
            selector = selectors["id"]
        elif "css_data_testid" in selectors:
            selector = selectors["css_data_testid"]
        elif "css_id" in selectors:
            selector = selectors["css_id"]
        else:
            selector = action["element_context"]["tag_name"]
        
        if action_type == "click":
            return f"page.click('{selector}')"
        elif action_type == "type_text":
            text = action["metadata"].get("text", "")
            return f"page.fill('{selector}', '{text}')"
        
        return f"# {action_type} action on {selector}"
    
    def _generate_cypress_code(self, action: Dict[str, Any]) -> str:
        """Generate Cypress-specific code for an action."""
        selectors = action["selectors"]
        action_type = action["action_type"]
        
        # Choose best selector for Cypress
        if "cypress_data_cy" in selectors:
            selector = selectors["cypress_data_cy"]
        elif "data_cy" in selectors:
            selector = selectors["data_cy"]
        elif "css_id" in selectors:
            selector = selectors["css_id"]
        elif "css_data_testid" in selectors:
            selector = selectors["css_data_testid"]
        else:
            selector = action["element_context"]["tag_name"]
        
        if action_type == "click":
            return f"cy.get('{selector}').click()"
        elif action_type == "type_text":
            text = action["metadata"].get("text", "")
            return f"cy.get('{selector}').type('{text}')"
        
        return f"// {action_type} action on {selector}"
    
    def _generate_page_object_element(self, element_data: Dict[str, Any], framework: str) -> Dict[str, Any]:
        """Generate page object element definition for framework."""
        page_object = {
            "tag_name": element_data["tag_name"],
            "selectors": element_data["selectors"],
            "attributes": element_data["attributes"],
            "meaningful_text": element_data["meaningful_text"]
        }
        
        if framework.lower() == "selenium":
            # Choose best selector for Selenium page object
            selectors = element_data["selectors"]
            if "selenium_id" in selectors:
                page_object["locator"] = f"(By.ID, '{selectors['selenium_id']}')"
            elif "css_id" in selectors:
                page_object["locator"] = f"(By.CSS_SELECTOR, '{selectors['css_id']}')"
            elif "css_data_testid" in selectors:
                page_object["locator"] = f"(By.CSS_SELECTOR, '{selectors['css_data_testid']}')"
        
        return page_object


# Global instance for tracking
element_tracker = ElementTracker()