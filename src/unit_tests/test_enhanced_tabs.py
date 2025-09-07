"""
Test script to verify the enhanced tabs functionality in SDET-GENIE.
This script creates sample data to test the enhanced tab rendering.
"""

import streamlit as st
import sys
import os
import pandas as pd

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.main_view import _render_results_tab, _render_actions_tab, _render_elements_tab, _render_details_tab

# Sample test data that mimics the structure of actual session data
sample_history = {
    "urls": [
        "https://www.saucedemo.com/",
        "https://www.saucedemo.com/inventory.html",
        "https://www.saucedemo.com/cart.html"
    ],
    "action_names": [
        "Navigate to login page",
        "Enter username",
        "Enter password",
        "Click login button",
        "Click add to cart button",
        "Navigate to cart"
    ],
    "detailed_actions": [
        {
            "name": "Navigate to login page",
            "index": 0,
            "element_details": {}
        },
        {
            "name": "Enter username",
            "index": 1,
            "element_details": {
                "index": 1,
                "xpath": "//input[@id='user-name']",
                "tag_name": "input"
            }
        },
        {
            "name": "Enter password",
            "index": 2,
            "element_details": {
                "index": 2,
                "xpath": "//input[@id='password']",
                "tag_name": "input"
            }
        },
        {
            "name": "Click login button",
            "index": 3,
            "element_details": {
                "index": 3,
                "xpath": "//input[@id='login-button']",
                "tag_name": "input"
            }
        }
    ],
    "element_xpaths": {
        "1": "//input[@id='user-name']",
        "2": "//input[@id='password']",
        "3": "//input[@id='login-button']",
        "4": "//button[@id='add-to-cart-sauce-labs-bolt-t-shirt']",
        "5": "//a[@class='shopping_cart_link']"
    },
    "extracted_content": [
        "Swag Labs - Login",
        "Login successful",
        "Sauce Labs Bolt T-Shirt added to cart"
    ],
    "errors": [],
    "model_actions": [
        {"action": "navigate", "url": "https://www.saucedemo.com/"},
        {"action": "input_text", "element_index": 1, "text": "standard_user"},
        {"action": "input_text", "element_index": 2, "text": "secret_sauce"},
        {"action": "click_element", "element_index": 3}
    ],
    "execution_date": "2025-09-06 14:30:25",
    "element_interactions": {
        "total_interactions": 5,
        "unique_elements": 5,
        "action_types": ["click", "type_text", "navigate"],
        "automation_data": {
            "element_library": {
                "element_1": {
                    "element_index": 1,
                    "tag_name": "input",
                    "meaningful_text": "Username",
                    "interactions_count": 1,
                    "attributes": {
                        "id": "user-name",
                        "type": "text",
                        "class": "input_error form_input",
                        "placeholder": "Username"
                    },
                    "position": {
                        "x": 112.046875,
                        "y": 124.0,
                        "width": 522.890625,
                        "height": 39.0
                    },
                    "selectors": {
                        "id": "#user-name",
                        "css_id": "#user-name",
                        "xpath_id": "//input[@id='user-name']",
                        "name": "[name='user-name']",
                        "css_name": "input[name='user-name']",
                        "xpath_name": "//input[@name='user-name']",
                        "css_type": "input[type='text']",
                        "xpath_type": "//input[@type='text']",
                        "css_placeholder": "input[placeholder='Username']",
                        "xpath_placeholder": "//input[@placeholder='Username']",
                        "css_class": "input.input_error.form_input",
                        "xpath_class": "//input[@class='input_error form_input']"
                    }
                },
                "element_2": {
                    "element_index": 2,
                    "tag_name": "input",
                    "meaningful_text": "Password",
                    "interactions_count": 1,
                    "attributes": {
                        "id": "password",
                        "type": "password",
                        "class": "input_error form_input",
                        "placeholder": "Password"
                    },
                    "position": {
                        "x": 112.046875,
                        "y": 178.0,
                        "width": 522.890625,
                        "height": 39.0
                    },
                    "selectors": {
                        "id": "#password",
                        "css_id": "#password",
                        "xpath_id": "//input[@id='password']",
                        "name": "[name='password']",
                        "css_name": "input[name='password']",
                        "xpath_name": "//input[@name='password']",
                        "css_type": "input[type='password']",
                        "xpath_type": "//input[@type='password']",
                        "css_placeholder": "input[placeholder='Password']",
                        "xpath_placeholder": "//input[@placeholder='Password']",
                        "css_class": "input.input_error.form_input",
                        "xpath_class": "//input[@class='input_error form_input']"
                    }
                },
                "element_3": {
                    "element_index": 3,
                    "tag_name": "input",
                    "meaningful_text": "Login",
                    "interactions_count": 1,
                    "attributes": {
                        "type": "submit",
                        "class": "submit-button btn_action",
                        "id": "login-button",
                        "value": "Login"
                    },
                    "position": {
                        "x": 112.046875,
                        "y": 272.0,
                        "width": 522.890625,
                        "height": 49.0
                    },
                    "selectors": {
                        "id": "#login-button",
                        "css_id": "#login-button",
                        "xpath_id": "//input[@id='login-button']",
                        "name": "[name='login-button']",
                        "css_name": "input[name='login-button']",
                        "xpath_name": "//input[@name='login-button']",
                        "css_type": "input[type='submit']",
                        "xpath_type": "//input[@type='submit']",
                        "css_class": "input.submit-button.btn_action",
                        "xpath_class": "//input[@class='submit-button btn_action']"
                    }
                }
            },
            "framework_selectors": {
                "id": {
                    "element_1": "#user-name",
                    "element_2": "#password",
                    "element_3": "#login-button"
                },
                "css_id": {
                    "element_1": "#user-name",
                    "element_2": "#password",
                    "element_3": "#login-button"
                },
                "xpath_id": {
                    "element_1": "//input[@id='user-name']",
                    "element_2": "//input[@id='password']",
                    "element_3": "//input[@id='login-button']"
                },
                "name": {
                    "element_1": "[name='user-name']",
                    "element_2": "[name='password']",
                    "element_3": "[name='login-button']"
                }
            }
        }
    },
    "framework_exports": {
        "selenium": {"framework": "selenium"},
        "playwright": {"framework": "playwright"},
        "cypress": {"framework": "cypress"}
    }
}

def test_enhanced_tabs():
    """Test the enhanced tab rendering functions."""
    st.set_page_config(page_title="Enhanced Tabs Test", layout="wide")
    st.title("🧪 Testing Enhanced Tabs")
    
    # Test Results tab
    st.header("📊 Summary Tab")
    _render_results_tab(sample_history)
    
    st.markdown("---")
    
    # Test Actions tab
    st.header("⚡ Actions Tab")
    _render_actions_tab(sample_history)
    
    st.markdown("---")
    
    # Test Elements tab
    st.header("🔍 Elements Tab")
    _render_elements_tab(sample_history)
    
    st.markdown("---")
    
    # Test Details tab
    st.header("📋 Details Tab")
    _render_details_tab(sample_history)

if __name__ == "__main__":
    test_enhanced_tabs()