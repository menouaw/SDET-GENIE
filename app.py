import sys
import asyncio
from dotenv import load_dotenv
import streamlit as st

from src.Utilities.utils import load_css
from src.ui import sidebar, main_view
from src.logic import handlers
from src.config import APP_CONFIG

# Load environment variables
load_dotenv()

# Handle Windows asyncio policy
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title=APP_CONFIG["page_title"], 
        layout=APP_CONFIG["page_layout"]
    )
    
    # Load external CSS
    load_css("static/style.css")
    
    # Initialize session state if not already done
    handlers.initialize_session_state()
    
    # Render UI components
    selected_framework = sidebar.render_sidebar()
    main_view.render_header()
    user_story = main_view.render_user_story_input()
    
    # Handle button clicks by calling handlers
    enhance, manual, gherkin, execute, generate, self_heal = main_view.render_action_buttons()
    
    if enhance:
        handlers.handle_enhance_story(user_story)
    if manual:
        handlers.handle_generate_manual_tests()
    if gherkin:
        handlers.handle_generate_gherkin()
    if execute:
        handlers.handle_execute_steps()
    if generate and selected_framework:
        handlers.handle_generate_code(selected_framework)
    if self_heal:
        handlers.handle_self_healing()
    
    # Display the results from session_state
    main_view.render_enhanced_story()
    main_view.render_manual_test_cases()
    main_view.render_gherkin_scenarios()
    main_view.render_execution_results()
    if selected_framework:
        main_view.render_generated_code(selected_framework)
    
    # Footer
    main_view.render_footer()


if __name__ == "__main__":
    main()
