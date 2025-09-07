"""
Sidebar UI components for SDET-GENIE application.
Handles framework selection and about WaiGenie information.
"""

import streamlit as st
from src.config import FRAMEWORK_GENERATORS, URLS, UI_TEXT, ABOUT_CONTENT, BUTTON_LABELS
from src.models_config import SUPPORTED_MODELS


def render_sidebar():
    """
    Render the sidebar with framework selection and about WaiGenie information.
    
    Returns:
        str: Selected framework name
    """
    with st.sidebar:
        # Main WaiGenie heading
        st.markdown(
            f'<div class="sidebar-heading"><a href="{URLS["waigenie_website"]}" target="_blank" style="color: white; text-decoration: none;">{UI_TEXT["sidebar_heading"]}</a></div>', 
            unsafe_allow_html=True
        )

        # Model selection
        st.markdown('<div class="sidebar-heading">🤖 Model Selection</div>', unsafe_allow_html=True)
        
        # Provider selection
        selected_provider = st.selectbox(
            "Select LLM Provider:",
            list(SUPPORTED_MODELS.keys()),
            key='selected_provider'
        )
        
        # Model selection (updates based on provider)
        if selected_provider:  # Add safety check
            available_models = list(SUPPORTED_MODELS[selected_provider]["models"].keys())
            selected_model = st.selectbox(
                "Select Model:",
                available_models,
                key='selected_model'
            )
            
            # Display required API key
            api_key_env = SUPPORTED_MODELS[selected_provider]["api_key_env"]
            st.info(f"This model requires the '{api_key_env}' environment variable to be set.")
        else:
            st.error("Please select a provider first.")
        
        st.markdown("---")

        # Framework selection
        st.markdown(
            f'<div class="sidebar-heading">{UI_TEXT["frameworks_heading"]}</div>', 
            unsafe_allow_html=True
        )
        selected_framework = st.selectbox(
            "Select framework:",
            list(FRAMEWORK_GENERATORS.keys()),
            index=0
        )

        # About WaiGenie section with tabs
        with st.expander("About WaiGenie"):
            _render_about_tabs()

        # Contact button
        st.markdown("---")
        _render_contact_button()

        # Logo and branding
        _render_branding()

        # YouTube demo button
        _render_youtube_button()

    return selected_framework


def _render_about_tabs():
    """Render the About WaiGenie tabs."""
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Vision & Mission",
        "Features",
        "How It Works",
        "Workflow",
        "Benefits"
    ])

    with tab1:
        st.subheader("Our Vision")
        st.write(ABOUT_CONTENT["vision"])

        st.subheader("Our Mission")
        st.write(ABOUT_CONTENT["mission"])

    with tab2:
        for title, description in ABOUT_CONTENT["features"]:
            st.markdown(f"#### {title}")
            st.write(description)

    with tab3:
        _render_how_it_works()

    with tab4:
        _render_workflow()

    with tab5:
        for benefit in ABOUT_CONTENT["benefits"]:
            st.write(f"• {benefit}")


def _render_how_it_works():
    """Render the How It Works section."""
    steps = [
        ("Sign Up", "Create your WaiGenie account and set up your organization profile."),
        ("Connect", "Integrate WaiGenie with your existing QA tools and workflows."),
        ("Analyze", "Let our AI analyze your application and generate test scenarios."),
        ("Optimize", "Continuously improve your QA process with AI-driven insights.")
    ]
    
    for i, (title, description) in enumerate(steps, 1):
        col1, col2 = st.columns([1, 5])
        with col1:
            st.markdown(f"### {i}")
        with col2:
            st.markdown(f"#### {title}")
            st.write(description)


def _render_workflow():
    """Render the AI-Powered QA Workflow section."""
    st.subheader("AI-Powered QA Workflow")
    
    workflow_steps = [
        ("1. QA Agent", [
            "• Converts user stories into Gherkin scenarios",
            "• Generates positive and negative test cases"
        ]),
        ("2. Browser Agent", [
            "• Executes Gherkin scenarios in a browser",
            "• Captures detailed DOM information",
            "• Records element details like XPaths"
        ]),
        ("3. Code Generation Agent", [
            "• Transforms scenarios into automation scripts",
            "• Includes necessary imports and dependencies",
            "• Handles errors and provides helper functions"
        ])
    ]
    
    for title, items in workflow_steps:
        st.markdown(f"#### {title}")
        for item in items:
            st.write(item)


def _render_contact_button():
    """Render the contact us button."""
    email = URLS["contact_email"]
    gmail_link = f"https://mail.google.com/mail/?view=cm&fs=1&to={email}"
    st.markdown(
        f'<a href="{gmail_link}" target="_blank"><button style="width: 100%; background: linear-gradient(90deg, #6A0572, #240046); color: white; padding: 0.6rem 1.2rem; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s ease;">{BUTTON_LABELS["contact_us"]}</button></a>',
        unsafe_allow_html=True
    )


def _render_branding():
    """Render the logo and branding section."""
    st.markdown(f"""
    <div style="text-align: center; margin-top: 30px;">
        <img src="{URLS["logo_url"]}" style="width: 96px; height: auto; margin-bottom: 10px;">
        <img src="{URLS["logotext_url"]}" style="width: 180px; height: auto; display: block; margin: 0 auto;">
        <p style="font-size: 0.75rem; color: #E6E6FA; margin-top: 10px;">© 2025 www.waigenie.tech. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)


def _render_youtube_button():
    """Render the YouTube demo button."""
    st.markdown(
        f'<a href="{URLS["youtube_demo"]}" target="_blank"><button style="width: 100%; background: linear-gradient(90deg, #FF0000, #CC0000); color: white; padding: 0.6rem 1.2rem; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.3s ease;">{BUTTON_LABELS["youtube_demo"]}</button></a>',
        unsafe_allow_html=True
    )