import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.logic.tracking_browser_agent import TrackingBrowserAgent
from browser_use import ChatGoogle, BrowserProfile

async def test_recordings():
    """Test if recordings are being saved correctly after our fixes."""
    print("Testing recordings functionality...")
    
    # Create test directories
    test_video_dir = "./recordings/test_videos"
    test_traces_dir = "./recordings/test_traces"
    test_har_path = "./recordings/test_network.har"
    
    # Ensure directories exist
    Path(test_video_dir).mkdir(parents=True, exist_ok=True)
    Path(test_traces_dir).mkdir(parents=True, exist_ok=True)
    Path("./recordings").mkdir(parents=True, exist_ok=True)
    
    try:
        # Create a simple browser agent with recording parameters
        agent = TrackingBrowserAgent(
            task="Go to https://example.com and click on the first link",
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
        
        har_files = list(Path(".").rglob("*.har"))
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
        
        # Check if GIF path is stored in session state (simulated)
        import streamlit as st
        if 'history' in st.session_state and 'gif_path' in st.session_state.history:
            print(f"GIF path in session state: {st.session_state.history['gif_path']}")
        else:
            # Fallback: check if GIF files exist in the expected location
            expected_gif = Path(test_video_dir) / "execution.gif"
            if expected_gif.exists():
                print(f"GIF file found at expected location: {expected_gif}")
            else:
                print("No GIF path found in session state or expected location")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
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
    asyncio.run(test_recordings())