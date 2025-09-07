"""
Verification script to check that our fixes are correctly implemented.
This script checks the code changes without running the actual application.
"""

import ast
import os
from pathlib import Path

def check_browser_executor_fixes():
    """Check that browser_executor.py has the correct fixes."""
    file_path = "./src/logic/browser_executor.py"
    
    if not os.path.exists(file_path):
        print("❌ browser_executor.py not found")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that browser_agent is created
    if "browser_agent = TrackingBrowserAgent(" not in content:
        print("❌ browser_agent is not created in browser_executor.py")
        return False
    
    # Check that recording parameters are passed
    required_params = [
        "record_video_dir=scenario_video_dir",
        "record_har_path=scenario_har_path", 
        "traces_dir=scenario_traces_dir",
        "generate_gif=True"
    ]
    
    for param in required_params:
        if param not in content:
            print(f"❌ Missing parameter in browser_agent creation: {param}")
            return False
    
    print("✅ browser_executor.py fixes verified")
    return True

def check_tracking_browser_agent_fixes():
    """Check that tracking_browser_agent.py has the correct fixes."""
    file_path = "./src/logic/tracking_browser_agent.py"
    
    if not os.path.exists(file_path):
        print("❌ tracking_browser_agent.py not found")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that recording parameters are properly handled
    required_elements = [
        "self.record_video_dir = kwargs.pop('record_video_dir', None)",
        "self.record_har_path = kwargs.pop('record_har_path', None)",
        "self.traces_dir = kwargs.pop('traces_dir', None)",
        "record_video_dir=self.record_video_dir",
        "record_har_path=self.record_har_path",
        "traces_dir=self.traces_dir",
        "from browser_use.agent.gif import create_history_gif"
    ]
    
    for element in required_elements:
        if element not in content:
            print(f"❌ Missing element in tracking_browser_agent.py: {element}")
            return False
    
    print("✅ tracking_browser_agent.py fixes verified")
    return True

def check_debug_view_fixes():
    """Check that debug_view.py has the correct fixes."""
    file_path = "./src/ui/debug_view.py"
    
    if not os.path.exists(file_path):
        print("❌ debug_view.py not found")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that GIF path is properly handled
    if "gif_path = history.get('gif_path')" not in content:
        print("❌ GIF path handling not found in debug_view.py")
        return False
    
    print("✅ debug_view.py fixes verified")
    return True

def main():
    """Run all verification checks."""
    print("Verifying code fixes...\n")
    
    checks = [
        check_browser_executor_fixes,
        check_tracking_browser_agent_fixes,
        check_debug_view_fixes
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All fixes verified successfully!")
        print("\nSummary of fixes:")
        print("1. Fixed browser_agent creation in browser_executor.py")
        print("2. Properly pass recording parameters to TrackingBrowserAgent")
        print("3. Enhanced GIF generation in tracking_browser_agent.py")
        print("4. Improved recording display in debug_view.py")
    else:
        print("❌ Some fixes failed verification. Please check the errors above.")

if __name__ == "__main__":
    main()