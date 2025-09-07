"""
Test script to verify element tracking functionality
"""

import asyncio
import json
from src.logic.tracking_browser_agent import TrackingBrowserAgent
from src.logic.element_tracker import element_tracker
from browser_use import Browser
from browser_use import Agent, ChatGoogle
# from langchain_google_genai import ChatGoogleGenerativeAI
import os

async def test_element_tracking():
    """Test element tracking with a simple scenario"""
    print("Testing element tracking functionality...")
    
    # Clear any previous interactions
    element_tracker.clear_interactions()
    
    # Create a simple browser agent for testing
    browser = Browser(headless=True)  # Run in headless mode for testing
    
    # Simple test task
    test_task = """
    Go to https://www.saucedemo.com and login with username 'standard_user' and password 'secret_sauce'.
    """
    
    # Get API key from environment
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables")
        return
    
    # Create LLM instance
    llm = ChatGoogle(model="gemini-2.0-flash", api_key=api_key)
    
    # Create tracking browser agent
    agent = TrackingBrowserAgent(
        task=test_task,
        llm=llm,
        browser=browser,
        use_vision=True,
        generate_gif=True  # Enable GIF generation
    )
    
    # Note: Event handlers are now registered automatically when the agent runs
    # No need to manually register them
    
    try:
        print("Running browser agent...")
        # Run the agent for a few steps
        history = await agent.run()
        
        print("Agent execution completed")
        print(f"Visited URLs: {history.urls()}")
        print(f"Action names: {history.action_names()}")
        
        # Check element tracking
        interactions_summary = element_tracker.get_interactions_summary()
        print(f"\nElement interactions summary:")
        print(f"Total interactions: {interactions_summary['total_interactions']}")
        print(f"Action types: {interactions_summary['action_types']}")
        print(f"Unique elements: {interactions_summary['unique_elements']}")
        
        # Export to JSON for inspection
        json_data = element_tracker.export_to_json()
        print(f"\nJSON export length: {len(json_data)} characters")
        
        # Save to file for inspection
        with open("test_element_tracking_output.json", "w") as f:
            f.write(json_data)
        print("Element tracking data saved to test_element_tracking_output.json")
        
        # Check framework exports
        selenium_export = element_tracker.export_for_framework("selenium")
        print(f"\nSelenium export has {len(selenium_export['test_steps'])} test steps")
        
        playwright_export = element_tracker.export_for_framework("playwright")
        print(f"Playwright export has {len(playwright_export['test_steps'])} test steps")
        
        cypress_export = element_tracker.export_for_framework("cypress")
        print(f"Cypress export has {len(cypress_export['test_steps'])} test steps")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    # finally:
    #     # Clean up
    #     await browser.close()

if __name__ == "__main__":
    asyncio.run(test_element_tracking())