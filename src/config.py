"""
Configuration file for SDET-GENIE application.
Contains all constants, framework configurations, and descriptions.
"""

from src.Prompts.agno_prompts import (
    generate_selenium_pytest_bdd,
    generate_playwright_python,
    generate_cypress_js,
    generate_robot_framework,
    generate_java_selenium
)

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
FRAMEWORK_DESCRIPTIONS = {
    "Selenium + PyTest BDD (Python)": "Popular Python testing framework combining Selenium WebDriver with PyTest BDD for behavior-driven development. Best for Python developers who want strong test organization and reporting.",
    "Playwright (Python)": "Modern, powerful browser automation framework with built-in async support and cross-browser testing capabilities. Excellent for modern web applications and complex scenarios.",
    "Cypress (JavaScript)": "Modern, JavaScript-based end-to-end testing framework with real-time reloading and automatic waiting. Perfect for front-end developers and modern web applications.",
    "Robot Framework": "Keyword-driven testing framework that uses simple, tabular syntax. Great for teams with mixed technical expertise and for creating readable test cases.",
    "Selenium + Cucumber (Java)": "Robust combination of Selenium WebDriver with Cucumber for Java, supporting BDD. Ideal for Java teams and enterprise applications."
}

# Application Configuration
APP_CONFIG = {
    "page_title": "SDET-GENIE",
    "page_layout": "wide",
    "execution_date": "February 26, 2025"
}

# Browser Execution Configuration
BROWSER_CONFIG = {
    "generate_gif": True,
    "use_vision": True,
    "highlight_elements": True,
    "record_video_dir": "./recordings/videos",
    "record_har_path": "./recordings/network.traces",
    "traces_dir": "./recordings/debug.traces",
    "headless": False,
    "window_size": {"width": 1280, "height": 720},
    "record_har_content": "embed",
    "record_har_mode": "full",
    "vision_detail_level": "auto",
    "max_history_items": None,
    "save_conversation_path": "./recordings/conversation_history.json"
}

# URLs and Links
URLS = {
    "waigenie_website": "https://www.waigenie.tech/",
    "youtube_demo": "https://youtu.be/qH30GvQebqg?feature=shared",
    "logo_url": "https://www.waigenie.tech/logo.png",
    "logotext_url": "https://www.waigenie.tech/logotext.svg",
    "contact_email": "richardsongunde@waigenie.tech"
}

# Session State Keys
SESSION_KEYS = {
    "enhanced_user_story": "enhanced_user_story",
    "manual_test_cases": "manual_test_cases",
    "edited_manual_test_cases": "edited_manual_test_cases",
    "generated_steps": "generated_steps",
    "edited_steps": "edited_steps",
    "history": "history",
    "automation_code": "automation_code",
    "changes_saved": "changes_saved",
    "manual_changes_saved": "manual_changes_saved",
    "execution_date": "execution_date"
}

# UI Text Content
UI_TEXT = {
    "main_title": "SDET - GENIE",
    "subtitle": "User Stories to Automated Tests : The Future of QA Automation using AI Agents",
    "header_text": "AI Agents powered by AGNO and BROWSER-USE",
    "footer_text": "© 2025 WAIGENIE | AI-Powered Test Automation",
    "user_story_placeholder": "e.g., As a user, I want to log in with valid credentials so that I can access my account.",
    "sidebar_heading": "WAIGENIE",
    "frameworks_heading": "Available Frameworks"
}

# About WaiGenie Content
ABOUT_CONTENT = {
    "vision": "Revolutionizing Quality Assurance with AI-powered solutions that empower teams to deliver flawless software at unprecedented speeds.",
    "mission": "Empower QA teams with cutting-edge AI solutions tailored for enterprise needs, enabling them to deliver high-quality software faster and more efficiently than ever before.",
    "features": [
        ("🧠 AI-Powered Test Generation", "Generate comprehensive test scenarios using advanced AI algorithms."),
        ("🔍 Intelligent Element Inspector", "Automatically identify and analyze web elements with precision."),
        ("📝 Gherkin Feature Generator", "Transform user stories into clear, concise Gherkin feature files."),
        ("💻 Automated Code Generation", "Generate test automation scripts in multiple languages automatically."),
        ("🤖 Web Agent Explorer", "Leverage AI to automatically explore and test complex user journeys."),
        ("📊 Advanced Analytics", "Gain insights into your testing processes and identify areas for improvement.")
    ],
    "benefits": [
        "90% reduction in time-to-test",
        "Enhanced test coverage",
        "Consistent code implementation",
        "Lower maintenance overhead",
        "Bridges skill gaps",
        "Preserves testing knowledge"
    ]
}

# Button Labels
BUTTON_LABELS = {
    "enhance_story": "✨ Enhance User Story",
    "generate_manual": "📝 Generate Manual Test Cases",
    "generate_gherkin": " Generate Gherkin",
    "execute_steps": "▶️ Execute Steps",
    "generate_code": "💻 Generate Code",
    "self_healing": "🔧 Self-Healing",
    "save_changes": "💾 Save Changes",
    "save_manual_changes": "💾 Save Manual Changes",
    "contact_us": "Contact Us",
    "youtube_demo": "▶️ YouTube Demo"
}

# Status Messages
STATUS_MESSAGES = {
    "story_enhanced": "User story enhanced successfully!",
    "manual_generated": "Manual test cases generated successfully!",
    "gherkin_generated": "Gherkin scenarios generated successfully!",
    "execution_completed": "Test execution completed!",
    "code_generated": "Automation code generated successfully!",
    "changes_saved": "Changes saved successfully!",
    "manual_changes_saved": "Manual test case changes saved successfully!",
    "enhance_first": "Please enhance the user story first.",
    "generate_manual_first": "Please generate manual test cases first.",
    "generate_gherkin_first": "Please generate Gherkin scenarios first.",
    "execute_first": "Please generate and execute Gherkin scenarios first.",
    "unsaved_changes": "* You have unsaved changes",
    "unsaved_warning": "You have unsaved changes. Please save your changes before executing steps.",
    "parse_error": "Failed to parse manual test cases from agent output.",
    "execution_error": "An error occurred during test execution: {error}",
    "generation_error": "Error generating {framework} code: {error}"
}