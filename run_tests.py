#!/usr/bin/env python3
"""
Simple test runner to check if our tests work.
"""

import sys
import unittest
from io import StringIO

def run_tests():
    """Run all tests and report results."""
    # Discover and run tests
    loader = unittest.TestLoader()
    suite = loader.discover('tests', pattern='test_*.py')
    
    # Run tests with verbose output
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    
    # Print results
    print(stream.getvalue())
    
    # Summary
    print(f"\nRan {result.testsRun} tests")
    if result.failures:
        print(f"Failures: {len(result.failures)}")
        for test, traceback in result.failures:
            print(f"  FAIL: {test}")
            print(f"    {traceback}")
    
    if result.errors:
        print(f"Errors: {len(result.errors)}")
        for test, traceback in result.errors:
            print(f"  ERROR: {test}")
            print(f"    {traceback}")
    
    if result.wasSuccessful():
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())