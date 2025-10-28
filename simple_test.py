#!/usr/bin/env python3
"""
Simple test to verify the package works correctly.
"""

def test_basic_imports():
    """Test that basic imports work."""
    try:
        from stream_md import MarkDownRender
        from stream_md.type_defs import StackStylePop, StreamElementPrintable
        from rich.console import Console
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic markdown rendering."""
    try:
        from stream_md import MarkDownRender
        from rich.console import Console
        from io import StringIO
        
        # Create console that captures output
        output = StringIO()
        console = Console(file=output, width=80, legacy_windows=False)
        renderer = MarkDownRender(console)
        
        # Test simple text
        renderer.stream_parse("Hello World")
        renderer.end_stream()
        
        result = output.getvalue()
        if "Hello World" in result:
            print("✅ Basic text rendering works")
            return True
        else:
            print(f"❌ Basic text rendering failed. Output: {result!r}")
            return False
            
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_markdown_elements():
    """Test various markdown elements."""
    try:
        from stream_md import MarkDownRender
        from rich.console import Console
        from io import StringIO
        
        output = StringIO()
        console = Console(file=output, width=80, legacy_windows=False)
        renderer = MarkDownRender(console)
        
        # Test heading
        renderer.stream_parse("# Test Heading\n")
        renderer.end_stream()
        
        result = output.getvalue()
        if "Test Heading" in result:
            print("✅ Heading rendering works")
            return True
        else:
            print(f"❌ Heading rendering failed. Output: {result!r}")
            return False
            
    except Exception as e:
        print(f"❌ Markdown elements test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Running simple tests for stream-md...\n")
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Markdown Elements", test_markdown_elements),
    ]
    
    passed = 0
    for name, test_func in tests:
        print(f"Running {name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed.")
        return 1

if __name__ == "__main__":
    exit(main())