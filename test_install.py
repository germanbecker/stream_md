#!/usr/bin/env python3
"""
Quick test script to verify the package installation works correctly.
"""

def test_import():
    """Test that the package can be imported."""
    try:
        import stream_md
        print("✅ Package import successful")
        print(f"   Version: {stream_md.__version__}")
        print(f"   Author: {stream_md.__author__}")
        return True
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality."""
    try:
        from rich.console import Console
        from io import StringIO
        from stream_md import MarkDownRender
        
        # Create a console that writes to a string
        output = StringIO()
        console = Console(file=output, width=80, legacy_windows=False)
        renderer = MarkDownRender(console)
        
        # Test basic rendering
        renderer.stream_parse("# Hello **World**!")
        renderer.end_stream()
        
        result = output.getvalue()
        if "Hello" in result and "World" in result:
            print("✅ Basic functionality test passed")
            return True
        else:
            print("❌ Basic functionality test failed - output doesn't contain expected text")
            return False
            
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_streaming():
    """Test streaming functionality."""
    try:
        from rich.console import Console
        from io import StringIO
        from stream_md import MarkDownRender
        
        output = StringIO()
        console = Console(file=output, width=80, legacy_windows=False)
        renderer = MarkDownRender(console)
        
        # Test streaming in chunks
        chunks = ["# Streaming ", "**Test**\n\n", "This is ", "*working*!"]
        for chunk in chunks:
            renderer.stream_parse(chunk)
        
        renderer.end_stream()
        
        result = output.getvalue()
        if "Streaming" in result and "Test" in result and "working" in result:
            print("✅ Streaming functionality test passed")
            return True
        else:
            print("❌ Streaming functionality test failed")
            return False
            
    except Exception as e:
        print(f"❌ Streaming functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing stream-md package installation...\n")
    
    tests = [
        ("Import Test", test_import),
        ("Basic Functionality", test_basic_functionality),
        ("Streaming Functionality", test_streaming),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The package is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the installation.")
        return 1

if __name__ == "__main__":
    exit(main())