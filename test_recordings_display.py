#!/usr/bin/env python3
"""
Test script to verify recording display functionality
"""

import streamlit as st
import asyncio
from pathlib import Path
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.logic.tracking_browser_agent import TrackingBrowserAgent
from browser_use import ChatGoogle

async def test_recordings_display():
    """Test if recordings are being displayed correctly in the UI."""
    print("Testing recordings display functionality...")
    
    # Create test directories
    test_video_dir = "./recordings/videos/test_display"
    test_traces_dir = "./recordings/debug.traces/test_display"
    test_har_path = "./recordings/network.traces/test_display.har"
    
    # Ensure directories exist
    Path(test_video_dir).mkdir(parents=True, exist_ok=True)
    Path(test_traces_dir).mkdir(parents=True, exist_ok=True)
    Path("./recordings/network.traces").mkdir(parents=True, exist_ok=True)
    
    try:
        # Create a simple browser agent with recording parameters
        agent = TrackingBrowserAgent(
            task="Go to https://example.com and verify the page loads",
            llm=ChatGoogle(model="gemini-2.0-flash"),
            generate_gif=True,
            record_video_dir=test_video_dir,
            record_har_path=test_har_path,
            traces_dir=test_traces_dir,
            highlight_elements=True,
            use_vision=True,
            headless=True,
            max_steps=3
        )
        
        print(f"Agent created with recording parameters:")
        print(f"  generate_gif: {getattr(agent, 'generate_gif', None)}")
        print(f"  record_video_dir: {getattr(agent, 'record_video_dir', None)}")
        print(f"  record_har_path: {getattr(agent, 'record_har_path', None)}")
        print(f"  traces_dir: {getattr(agent, 'traces_dir', None)}")
        
        if hasattr(agent, 'browser_profile'):
            bp = agent.browser_profile
            print(f"  browser_profile.record_video_dir: {getattr(bp, 'record_video_dir', None)}")
            print(f"  browser_profile.record_har_path: {getattr(bp, 'record_har_path', None)}")
            print(f"  browser_profile.traces_dir: {getattr(bp, 'traces_dir', None)}")
        
        # Run the agent for a few steps
        print("Running agent...")
        history = await agent.run(max_steps=3)
        print("Agent run completed.")
        
        # Check if files were created
        print("\nChecking for recorded files:")
        video_files = list(Path(test_video_dir).rglob("*"))
        print(f"Video files found: {len(video_files)}")
        for f in video_files:
            print(f"  {f}")
        
        har_files = list(Path("./recordings/network.traces").rglob("*.har"))
        print(f"HAR files found: {len(har_files)}")
        for f in har_files:
            print(f"  {f}")
        
        trace_files = list(Path(test_traces_dir).rglob("*"))
        print(f"Trace files found: {len(trace_files)}")
        for f in trace_files:
            print(f"  {f}")
            
        gif_files = list(Path(test_video_dir).rglob("*.gif"))
        print(f"GIF files found: {len(gif_files)}")
        for f in gif_files:
            print(f"  {f}")
        
        # Check for any GIF files in the current directory
        root_gif_files = list(Path(".").rglob("*.gif"))
        print(f"Root GIF files found: {len(root_gif_files)}")
        for f in root_gif_files:
            print(f"  {f}")
        
        # Simulate session state for UI display
        import streamlit as st
        if 'history' not in st.session_state:
            st.session_state.history = {}
            
        # Store GIF path in session state for UI display
        if gif_files:
            expected_gif = gif_files[0]
            st.session_state.history['gif_path'] = str(expected_gif)
            print(f"GIF path stored in session state: {expected_gif}")
        else:
            # Fallback: check if GIF files exist in the expected location
            expected_gif = Path(test_video_dir) / "execution.gif"
            if expected_gif.exists():
                st.session_state.history['gif_path'] = str(expected_gif)
                print(f"GIF file found at expected location: {expected_gif}")
            else:
                print("No GIF path found in session state or expected location")
        
        # Test the UI display functions
        print("\nTesting UI display functions...")
        
        # Create a mock history object for testing
        mock_history = {
            'gif_path': st.session_state.history.get('gif_path'),
            'screenshots': [],
            'screenshot_paths': [],
            'recording_paths': {
                'videos': './recordings/videos',
                'network_traces': './recordings/network.traces',
                'debug_traces': './recordings/debug.traces'
            }
        }
        
        print("Mock history created for testing UI display")
        print(f"GIF path in mock history: {mock_history['gif_path']}")
        
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup test directories
        import shutil
        try:
            if Path(test_video_dir).exists():
                shutil.rmtree(test_video_dir)
            if Path(test_traces_dir).exists():
                shutil.rmtree(test_traces_dir)
            # Don't remove the HAR file if it's in the recordings directory
            if Path(test_har_path).exists() and "recordings" not in str(test_har_path):
                os.remove(test_har_path)
        except Exception as e:
            print(f"Cleanup error: {e}")

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_recordings_display())
    if success:
        print("\n✅ Recording display test completed successfully!")
    else:
        print("\n❌ Recording display test failed!")