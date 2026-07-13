#!/usr/bin/env python3
"""
Basic usage example for stream_md.

This example demonstrates how to use the streaming markdown parser
to render markdown content as it arrives.
"""

import time
import random
import logging
from rich.console import Console

from stream_md import MarkDownRender
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.warning("Hola")

def random_chunks(text: str, min_len: int = 1, max_len: int = 20):
    """Split text into random-sized chunks to simulate streaming."""
    chunks = []
    i = 0
    n = len(text)
    
    while i < n:
        size = random.randint(min_len, max_len)
        chunk = text[i:i + size]
        chunks.append(chunk)
        i += size
    
    return chunks


def main():
    """Main example function."""
    console = Console()
    renderer = MarkDownRender(console)
    
    # Sample markdown content
    markdown_content = """# Stream MD Example

Welcome to **Stream MD**, a streaming markdown parser for Python Rich!

## Features

- *Real-time* parsing and rendering
- **Beautiful** terminal output
- Support for various markdown elements

## Code Example

Here's a simple Python example:

```python
from rich.console import Console
from stream_md import MarkDownRender

console = Console()
renderer = MarkDownRender(console)

# Parse markdown in chunks
renderer.stream_parse("# Hello ")
renderer.stream_parse("**World**!")
renderer.end_stream()
```

## Lists and More

- Item 1
- Item 2 with *emphasis*
- Item 3 with **bold text**
- Item 4 with `code`

## Table

| Item | Price | Qty | Notes |
|:-----|------:|:---:|:------|
| Widget | $9.99 | 12 | In stock |
| Gadget | $149.00 | 3 | Backordered |
| Gizmo | $0.50 | 1000 | Bulk only |

| a | b |
| - | - |
| Uno | **Dos** |
| Tres | Cuatro | 

| Hola soy una `tabla` |a *que* **bueno**  s | chau |
| - | - | - |
| Que lindo | que feo | `qeu` grande

a **que** **bueno** s

**That's all for now!**"""

    print("🚀 Starting streaming markdown demo...\n")
    
    # Split content into random chunks to simulate streaming
    chunks = random_chunks(markdown_content, min_len=5, max_len=30)
    
    print(f"📦 Processing {len(chunks)} chunks...\n")
    print("=" * 60)
    
    # Process each chunk with a small delay to show streaming effect
    for i, chunk in enumerate(chunks):
        renderer.stream_parse(chunk)
        
        # Add a small delay to simulate network latency
        time.sleep(0.0)
        
        # Show progress
        if False and i % 10 == 0:
            print(f"\n[Progress: {i+1}/{len(chunks)} chunks processed]", end="")
    
    # Signal end of stream
    renderer.end_stream()
    
    print("\n" + "=" * 60)
    print("✅ Streaming complete!")


if __name__ == "__main__":
    console= Console()
    render = MarkDownRender(console)
    render.stream_parse("Hola *fasd* ***asdasdasd* `code` del ojete")
    render.end_stream()
    main()
