"""
Test environment setup utilities for stream_md tests.

This module provides utilities to properly initialize the markdown container
and other shared state needed for testing tokens.
"""

import pytest
from stream_md.tokens.base import MarkdownContainer


def setup_markdown_container():
    """Initialize the markdown container for testing."""
    MarkdownContainer.initialize()
    return MarkdownContainer.get()


@pytest.fixture(scope="function")
def markdown_container():
    """Pytest fixture that provides an initialized markdown container for each test."""
    setup_markdown_container()
    container = MarkdownContainer.get()
    yield container
    # Reset for next test
    MarkdownContainer._instance = None


@pytest.fixture(scope="function", autouse=True)
def auto_setup_container():
    """Automatically setup container for all tests in this session."""
    setup_markdown_container()
    yield
    # Reset for next test
    MarkdownContainer._instance = None


def reset_container():
    """Reset the container state - useful for test cleanup."""
    MarkdownContainer._instance = None