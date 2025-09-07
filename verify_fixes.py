#!/usr/bin/env python3
"""
Verification script to check that the recording display fixes are in place
"""

import os
from pathlib import Path

def check_debug_view_fixes():
    """Check if the debug view fixes are in place."""
    print("Checking debug view fixes...")
    
    # Check if debug_view.py exists
    debug_view_path = Path("src/ui/debug_view.py")
    if not debug_view_path.exists():
        print("❌ debug_view.py not found")
        return False
    
    # Read the file content
    with open(debug_view_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the fixes
    fixes = [
        ('use_container_width=True', 'Fixed deprecated use_column_width parameter'),
        ('_render_recordings', 'Recordings rendering function exists'),
        ('_render_screenshots', 'Screenshots rendering function exists')
    ]
    
    all_passed = True
    for fix, description in fixes:
        if fix in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - Fix not found")
            all_passed = False
    
    return all_passed

def check_main_view_fixes():
    """Check if the main view fixes are in place."""
    print("\nChecking main view fixes...")
    
    # Check if main_view.py exists
    main_view_path = Path("src/ui/main_view.py")
    if not main_view_path.exists():
        print("❌ main_view.py not found")
        return False
    
    # Read the file content
    with open(main_view_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for the fixes
    fixes = [
        ('use_container_width=True', 'Fixed deprecated use_column_width parameter'),
        ('st.image(gif_path, caption="Execution Animation", use_container_width=True)', 'GIF display fix')
    ]
    
    all_passed = True
    for fix, description in fixes:
        if fix in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - Fix not found")
            all_passed = False
    
    return all_passed

def check_directory_structure():
    """Check if the recordings directory structure is in place."""
    print("\nChecking directory structure...")
    
    required_dirs = [
        "recordings",
        "recordings/videos",
        "recordings/network.traces",
        "recordings/debug.traces"
    ]
    
    all_passed = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path} exists")
        else:
            print(f"❌ {dir_path} missing")
            all_passed = False
    
    return all_passed

def main():
    """Run all verification checks."""
    print("Verifying recording display fixes...\n")
    
    checks = [
        check_debug_view_fixes,
        check_main_view_fixes,
        check_directory_structure
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 All fixes verified successfully!")
        print("\nSummary of fixes:")
        print("1. Fixed deprecated use_column_width parameter in debug_view.py")
        print("2. Enhanced GIF display in main_view.py")
        print("3. Improved screenshot display in debug_view.py")
        print("4. Verified directory structure for recordings")
    else:
        print("❌ Some fixes failed verification. Please check the errors above.")

if __name__ == "__main__":
    main()