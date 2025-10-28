# Stream MD

A streaming markdown parser and formatter for Python Rich that renders markdown content as it's being received, perfect for real-time applications like chat interfaces, streaming APIs, or progressive content loading.

## Features

- **Streaming Processing**: Parse and render markdown content incrementally as it arrives
- **Rich Integration**: Beautiful terminal rendering using Python Rich
- **Real-time Rendering**: Perfect for chat applications, streaming APIs, or progressive content loading
- **Extensible Architecture**: Token-based parsing system that's easy to extend
- **Syntax Highlighting**: Code blocks with syntax highlighting via Pygments

## Supported Markdown Elements

- **Text Formatting**: Bold (`**text**`), Italic (`*text*`)
- **Headings**: All levels (`# H1` through `###### H6`)
- **Code Blocks**: Fenced code blocks with syntax highlighting
- **Paragraphs**: Regular text paragraphs
- **Nested Formatting**: Complex combinations of formatting elements

## Installation

```bash
pip install stream-md
```

## Quick Start

```python
from rich.console import Console
from stream_md import MarkDownRender

console = Console()
renderer = MarkDownRender(console)

# Simulate streaming content
markdown_chunks = [
    "# Hello ",
    "**World**\n\n",
    "This is *streaming* ",
    "markdown!\n\n",
    "```python\n",
    "print('Hello, World!')\n",
    "```\n"
]

for chunk in markdown_chunks:
    renderer.stream_parse(chunk)

# Signal end of stream
renderer.end_stream()
```

## Use Cases

### Chat Applications
Perfect for rendering markdown messages as they're being typed or received:

```python
def on_message_chunk(chunk):
    renderer.stream_parse(chunk)

def on_message_complete():
    renderer.end_stream()
```

### Streaming APIs
Render API responses that stream markdown content:

```python
import requests

response = requests.get('https://api.example.com/markdown', stream=True)
for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
    renderer.stream_parse(chunk)
renderer.end_stream()
```

### Progressive Content Loading
Display content as it loads from files or network:

```python
with open('large_document.md', 'r') as f:
    while chunk := f.read(1024):
        renderer.stream_parse(chunk)
renderer.end_stream()
```

## Architecture

Stream MD uses a token-based parsing architecture:

- **Block Tokens**: Handle block-level elements (headings, paragraphs, code blocks)
- **Inline Tokens**: Handle inline formatting (bold, italic)
- **Container Tokens**: Manage nested structures and state
- **Streaming State**: Maintains parsing state across chunks

## API Reference

### MarkDownRender

The main class for rendering streaming markdown.

#### `__init__(console: Console)`
Initialize the renderer with a Rich console.

#### `stream_parse(s: str)`
Parse and render a chunk of markdown text.

#### `end_stream()`
Signal the end of the stream and flush any remaining content.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### 0.1.0
- Initial release
- Basic streaming markdown parsing
- Support for headings, paragraphs, code blocks, and inline formatting
- Rich integration for beautiful terminal output