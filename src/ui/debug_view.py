"""
Debug view UI components for SDET-GENIE application.
Handles the display of advanced debugging and recording features.
"""

import streamlit as st
import pandas as pd
import base64
from pathlib import Path
from typing import Dict, Any
import datetime

from src.config import SESSION_KEYS


def render_debug_info(history: Dict[str, Any]):
    """Render advanced debugging information."""
    st.markdown('<h4 class="glow-text">🔬 Advanced Debugging</h4>', unsafe_allow_html=True)
    
    # Create tabs for different debugging views
    debug_tab1, debug_tab2, debug_tab3, debug_tab4, debug_tab5 = st.tabs([
        "🎥 Recordings", 
        "📸 Screenshots", 
        "🌐 Network Traces", 
        "🔧 Execution Traces",
        "🧠 LLM Responses"
    ])
    
    with debug_tab1:
        _render_recordings(history)
    
    with debug_tab2:
        _render_screenshots(history)
    
    with debug_tab3:
        _render_network_traces(history)
    
    with debug_tab4:
        _render_execution_traces(history)
        
    with debug_tab5:
        _render_llm_responses(history)


def _render_recordings(history: Dict[str, Any]):
    """Render video recordings information."""
    st.markdown("### 🎥 Video Recordings")
    
    # Check for GIF animation in scenario directories
    recording_paths = history.get('recording_paths', {})
    videos_dir = recording_paths.get('videos', './recordings/videos')
    
    # First check for GIF in the specific execution directory
    gif_path = history.get('gif_path')
    if gif_path and Path(gif_path).exists():
        st.success("✅ Execution GIF animation generated successfully")
        st.info(f"Location: {gif_path}")
        # Display the GIF here
        st.image(gif_path, caption="Execution Animation", use_column_width=True)
    else:
        # Check for GIF files in scenario directories
        if videos_dir and Path(videos_dir).exists():
            # Look for GIF files in scenario directories
            gif_files = list(Path(videos_dir).rglob("*.gif"))
            if gif_files:
                st.success(f"✅ {len(gif_files)} GIF animation(s) available")
                for gif_file in gif_files:
                    with st.expander(f"GIF: {gif_file.parent.name}"):
                        st.info(f"Location: {gif_file}")
                        # Display the GIF here
                        if gif_file.exists():
                            st.image(str(gif_file), caption=f"Execution Animation - {gif_file.parent.name}", use_column_width=True)
            else:
                st.info("No GIF animations were generated for this execution.")
        else:
            st.info("No GIF animations were generated for this execution.")
    
    # Check for video recordings in scenario directories
    if videos_dir and Path(videos_dir).exists():
        # Look for video files in scenario directories
        video_files = list(Path(videos_dir).rglob("*.webm"))
        if video_files:
            st.success(f"✅ {len(video_files)} video recording(s) available")
            for video_file in video_files:
                with st.expander(f"Video: {video_file.parent.name}"):
                    st.info(f"Location: {video_file}")
                    # Provide a download link and video player
                    if video_file.exists():
                        st.video(str(video_file))
                        with open(video_file, "rb") as file:
                            st.download_button(
                                label="Download Video",
                                data=file,
                                file_name=video_file.name,
                                mime="video/webm"
                            )
        else:
            st.info("No video recordings found in the recordings directory.")
    else:
        st.info("Video recording is not configured or the directory does not exist.")


def _render_screenshots(history: Dict[str, Any]):
    """Render screenshots information."""
    st.markdown("### 📸 Execution Screenshots")
    
    # Get screenshots from history
    screenshots = history.get('screenshots', [])
    screenshot_paths = history.get('screenshot_paths', [])
    
    if screenshots or screenshot_paths:
        st.success(f"✅ {len(screenshots) or len(screenshot_paths)} screenshot(s) captured")
        
        # Show screenshot paths
        if screenshot_paths:
            st.markdown("<p><strong>Screenshot Locations:</strong></p>", unsafe_allow_html=True)
            for path in screenshot_paths:
                st.markdown(f"<div style='background-color: #e3f2fd; padding: 5px; margin: 2px 0; border-radius: 3px;'>{path}</div>", unsafe_allow_html=True)
        
        # Show base64 screenshots if available
        if screenshots:
            st.markdown("<p><strong>Preview (first 3 screenshots):</strong></p>", unsafe_allow_html=True)
            for i, screenshot in enumerate(screenshots[:3]):
                try:
                    # Decode base64 screenshot
                    st.markdown(f"<p><strong>Screenshot {i+1}:</strong></p>", unsafe_allow_html=True)
                    # Display the image
                    st.image(base64.b64decode(screenshot), caption=f"Screenshot {i+1}", use_column_width=True)
                except Exception as e:
                    st.warning(f"Could not display screenshot {i+1}: {str(e)}")
    else:
        # Check if there are screenshots in the scenario directories
        recording_paths = history.get('recording_paths', {})
        videos_dir = recording_paths.get('videos', './recordings/videos')
        if videos_dir and Path(videos_dir).exists():
            # Look for screenshot files in scenario directories
            screenshot_files = list(Path(videos_dir).rglob("*.png"))
            if screenshot_files:
                st.success(f"✅ {len(screenshot_files)} screenshot(s) found in recordings")
                for screenshot_file in screenshot_files:
                    with st.expander(f"Screenshot: {screenshot_file.parent.name}"):
                        st.info(f"Location: {screenshot_file}")
                        # Display the image
                        if screenshot_file.exists():
                            st.image(str(screenshot_file), caption=f"Screenshot - {screenshot_file.parent.name}", use_column_width=True)
            else:
                st.info("No screenshots were captured during execution.")
        else:
            st.info("No screenshots were captured during execution.")


def _render_network_traces(history: Dict[str, Any]):
    """Render network trace information."""
    st.markdown("### 🌐 Network Traces")
    
    # Check for HAR files in scenario directories
    recording_paths = history.get('recording_paths', {})
    network_traces_dir = recording_paths.get('network_traces', './recordings/network.traces')
    if network_traces_dir and Path(network_traces_dir).exists():
        # Look for HAR files in scenario directories
        har_files = list(Path(network_traces_dir).rglob("*.har"))
        if har_files:
            st.success(f"✅ {len(har_files)} network trace file(s) generated")
            for har_file in har_files:
                with st.expander(f"Network Trace: {har_file.parent.name}"):
                    st.info(f"Location: {har_file}")
                    if har_file.exists():
                        st.markdown("<p><strong>File Size:</strong> {:.2f} KB</p>".format(har_file.stat().st_size / 1024), unsafe_allow_html=True)
                        st.info("HAR files contain detailed network activity information including requests, responses, and timings.")
                        # Provide download button
                        with open(har_file, "rb") as file:
                            st.download_button(
                                label="Download HAR File",
                                data=file,
                                file_name=har_file.name,
                                mime="application/json"
                            )
        else:
            st.info("No network traces were recorded for this execution.")
    else:
        # Fallback to original configuration
        from src.config import BROWSER_CONFIG
        har_path = BROWSER_CONFIG.get('record_har_path')
        if har_path and Path(har_path).exists():
            # Check if it's a directory or file
            har_path_obj = Path(har_path)
            if har_path_obj.is_dir():
                # Look for HAR files in the directory
                har_files = list(har_path_obj.rglob("*.har"))
                if har_files:
                    st.success(f"✅ {len(har_files)} network trace file(s) generated")
                    for har_file in har_files:
                        with st.expander(f"Network Trace: {har_file.parent.name}"):
                            st.info(f"Location: {har_file}")
                            if har_file.exists():
                                st.markdown("<p><strong>File Size:</strong> {:.2f} KB</p>".format(har_file.stat().st_size / 1024), unsafe_allow_html=True)
                                st.info("HAR files contain detailed network activity information including requests, responses, and timings.")
                                # Provide download button
                                with open(har_file, "rb") as file:
                                    st.download_button(
                                        label="Download HAR File",
                                        data=file,
                                        file_name=har_file.name,
                                        mime="application/json"
                                    )
                else:
                    st.info("No network traces were recorded for this execution.")
            else:
                # Single HAR file
                st.success("✅ Network trace (HAR) file generated")
                st.info(f"Location: {har_path}")
                if har_path_obj.exists():
                    st.markdown("<p><strong>File Size:</strong> {:.2f} KB</p>".format(har_path_obj.stat().st_size / 1024), unsafe_allow_html=True)
                    st.info("HAR files contain detailed network activity information including requests, responses, and timings.")
                    # Provide download button
                    with open(har_path_obj, "rb") as file:
                        st.download_button(
                            label="Download HAR File",
                            data=file,
                            file_name=har_path_obj.name,
                            mime="application/json"
                        )
        else:
            st.info("No network traces were recorded for this execution.")


def _render_execution_traces(history: Dict[str, Any]):
    """Render execution trace information."""
    st.markdown("### 🔧 Execution Traces")
    
    # Check for trace files in scenario directories
    recording_paths = history.get('recording_paths', {})
    debug_traces_dir = recording_paths.get('debug_traces', './recordings/debug.traces')
    if debug_traces_dir and Path(debug_traces_dir).exists():
        # Look for trace files in scenario directories
        trace_files = list(Path(debug_traces_dir).rglob("*"))
        # Filter out directories
        trace_files = [f for f in trace_files if f.is_file()]
        if trace_files:
            st.success(f"✅ {len(trace_files)} trace file(s) generated")
            for trace_file in trace_files:
                with st.expander(f"Trace: {trace_file.parent.name} - {trace_file.name}"):
                    if trace_file.exists():
                        st.markdown(f"<div style='background-color: #e8f5e9; padding: 5px; margin: 2px 0; border-radius: 3px; display: flex; justify-content: space-between;'><span>{trace_file.name}</span> <span>{trace_file.stat().st_size / 1024:.2f} KB</span></div>", unsafe_allow_html=True)
                        # Provide download button for trace files
                        with open(trace_file, "rb") as file:
                            st.download_button(
                                label="Download Trace File",
                                data=file,
                                file_name=trace_file.name,
                                mime="application/json"
                            )
            st.info("Trace files contain detailed execution information for debugging purposes.")
        else:
            st.info("No trace files found in the traces directory.")
    else:
        # Fallback to original configuration
        from src.config import BROWSER_CONFIG
        traces_dir = BROWSER_CONFIG.get('traces_dir')
        if traces_dir and Path(traces_dir).exists():
            trace_files = list(Path(traces_dir).rglob("*"))
            # Filter out directories
            trace_files = [f for f in trace_files if f.is_file()]
            if trace_files:
                st.success(f"✅ {len(trace_files)} trace file(s) generated")
                for trace_file in trace_files:
                    with st.expander(f"Trace: {trace_file.parent.name} - {trace_file.name}"):
                        if trace_file.exists():
                            st.markdown(f"<div style='background-color: #e8f5e9; padding: 5px; margin: 2px 0; border-radius: 3px; display: flex; justify-content: space-between;'><span>{trace_file.name}</span> <span>{trace_file.stat().st_size / 1024:.2f} KB</span></div>", unsafe_allow_html=True)
                            # Provide download button for trace files
                            with open(trace_file, "rb") as file:
                                st.download_button(
                                    label="Download Trace File",
                                    data=file,
                                    file_name=trace_file.name,
                                    mime="application/json"
                                )
                st.info("Trace files contain detailed execution information for debugging purposes.")
            else:
                st.info("No trace files found in the traces directory.")
        else:
            st.info("Execution tracing is not configured or the directory does not exist.")


def _render_llm_responses(history: Dict[str, Any]):
    """Render LLM responses and model outputs."""
    st.markdown("### 🧠 LLM Responses & Model Outputs")
    
    # Get model outputs from history
    model_outputs = history.get('model_outputs', [])
    final_result = history.get('final_result')
    is_done = history.get('is_done')
    is_successful = history.get('is_successful')
    
    # Display execution status
    if is_done is not None:
        if is_done:
            st.success("✅ Execution completed")
        else:
            st.info("⏳ Execution in progress")
    
    if is_successful is not None:
        if is_successful:
            st.success("✅ Execution successful")
        elif is_done:  # Only show failure if execution is done
            st.error("❌ Execution failed")
    
    # Display final result
    if final_result:
        st.markdown("### 🏁 Final Result")
        st.markdown(f"<div style='background-color: #e8f5e9; padding: 10px; border-radius: 5px;'><pre>{final_result}</pre></div>", unsafe_allow_html=True)
    
    # Display model outputs
    if model_outputs:
        st.markdown("### 🤖 Model Responses")
        st.info(f"Total LLM responses: {len(model_outputs)}")
        
        # Show each model output in an expander
        for i, output in enumerate(model_outputs):
            with st.expander(f"Step {i+1}: LLM Response"):
                if isinstance(output, dict):
                    st.json(output)
                else:
                    st.markdown(f"<div style='background-color: #f5f5f5; padding: 10px; border-radius: 5px;'><pre>{output}</pre></div>", unsafe_allow_html=True)
    else:
        st.info("No LLM responses were captured during execution.")


def render_ai_vision_info(history: Dict[str, Any]):
    """Render AI vision and element highlighting information."""
    st.markdown('<h4 class="glow-text">👁️ AI Vision & Element Highlighting</h4>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background-color: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid #ff9800;'>
        <h5>🤖 AI Vision Capabilities</h5>
        <p>During execution, the AI agent utilized computer vision to:</p>
        <ul>
            <li>🔍 Analyze webpage screenshots for element identification</li>
            <li>🎯 Highlight interactive elements for better decision making</li>
            <li>📊 Process visual information alongside DOM structure</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Show element highlighting info
    st.markdown("""
    <div style='background-color: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #2196f3; margin-top: 15px;'>
        <h5>✨ Element Highlighting</h5>
        <p>Interactive elements were visually highlighted during execution to assist the AI agent:</p>
        <ul>
            <li>🔘 Buttons and links were outlined in blue</li>
            <li>📝 Input fields were highlighted in green</li>
            <li>📋 Selectable items were marked with visual indicators</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Show vision details if available
    vision_details = history.get('vision_details')
    if vision_details:
        st.markdown("### 🔍 Vision Analysis Details")
        with st.expander("View Vision Data"):
            st.json(vision_details)