# Stream MD Architecture Documentation

## Overview

Stream MD is a **streaming markdown parser** designed for real-time processing of markdown content. It uses a token-based architecture with a hierarchical state machine approach to handle partial content and maintain parsing state across multiple input chunks.

## Core Architecture

### 1. Main Components

#### MarkDownRender (Entry Point)
- **Purpose**: Main orchestrator class that manages the entire parsing pipeline
- **Key Responsibilities**:
  - Maintains parsing buffer for incomplete chunks
  - Manages Rich Console for terminal output
  - Coordinates between parsing and rendering
  - Handles stream lifecycle (start → chunks → end)

#### Token System (Parsing Engine)
- **Purpose**: Hierarchical parsing system where each token type handles specific markdown elements
- **Key Features**:
  - State machine approach for robust parsing
  - Supports nested elements (bold inside headings, etc.)
  - Extensible design for adding new markdown elements

#### Style Management
- **StyleStack**: Manages Rich formatting state for nested styles
- **StreamElements**: Represent both content and style operations

### 2. Token Hierarchy

```
Token (abstract base)
├── BlockToken (block-level elements)
│   ├── ContainerToken (can contain other elements)
│   │   └── Root (document root, entry point)
│   └── LeafToken (terminal elements)
│       ├── Heading (# ## ### etc.)
│       ├── Paragraph (regular text blocks)
│       └── CodeFence (```language code```)
└── InlineToken (inline formatting)
    └── Emphasis (** bold **, * italic *)
```

### 3. Processing Pipeline

```
Input Chunk → Buffer → Root.process() → find_child() → consume() → render() → Output
                ↑                           ↓
            State Management         Token Stack Management
```

#### Detailed Flow:
1. **Input Buffering**: Incomplete chunks are buffered until processable
2. **Token Processing**: Each token follows preprocess → process → postprocess
3. **Child Detection**: Tokens scan for nested elements they can contain
4. **Content Consumption**: Tokens consume their specific markdown syntax
5. **Style Management**: Push/pop operations manage nested formatting
6. **Rich Rendering**: Converted to Rich renderables for terminal output

### 4. State Management

#### TokenStack
- Manages nested parsing context
- Tracks which token is currently processing
- Handles token lifecycle (creation, processing, cleanup)

#### StyleStack (Rich Integration)
- Maintains formatting state for nested styles
- Supports push/pop operations for entering/exiting formatted regions
- Integrates with Rich's styling system

#### Parsing State
- **Buffer**: Holds incomplete content between chunks
- **ProcessOutput**: Contains processed elements and remaining text
- **ConsumeResults**: Results from token consumption

## Key Design Patterns

### 1. State Machine Pattern
Each token acts as a state in a parsing state machine:
- **Entry**: Token creation and stack push
- **Processing**: Content consumption and child detection
- **Exit**: Stack pop and cleanup

### 2. Visitor Pattern
Tokens "visit" input text and decide how to process it:
- `rule()`: Determines if token applies to input
- `consume()`: Processes the token's content
- `find_child()`: Discovers nested elements

### 3. Strategy Pattern
Different token classes implement different parsing strategies:
- Heading tokens look for `#` markers
- Emphasis tokens look for `*` or `**` markers
- Code fence tokens look for ``` markers

### 4. Observer Pattern
Style stack changes notify the rendering system:
- Style push/pop operations create StreamElements
- Renderer observes these elements and updates display

## Streaming Capabilities

### Chunk Processing
- **Partial Content**: Can process incomplete markdown chunks
- **State Preservation**: Maintains parsing state between chunks
- **Buffer Management**: Handles content that spans multiple chunks

### Real-time Rendering
- **Incremental Output**: Renders content as it's parsed
- **Rich Integration**: Beautiful terminal formatting
- **Style Continuity**: Maintains formatting across chunks

## Extension Points

### Adding New Markdown Elements

1. **Create Token Class**: Inherit from appropriate base (Block/Inline)
2. **Implement Methods**:
   - `rule()`: Detection logic
   - `consume()`: Processing logic
   - `find_child()`: Nested element detection
3. **Register Token**: Add to parent's child detection logic

### Example: Adding Strikethrough
```python
class Strikethrough(MarkDownInline):
    @classmethod
    def get_marker(cls) -> str:
        return "~~"
    
    @classmethod
    def rule(cls, s: str, end_stream: bool = False) -> RuleResult:
        # Implementation for detecting ~~text~~
        pass
    
    def consume(self, input_text: str, end_stream: bool = False) -> ConsumeResults:
        # Implementation for processing strikethrough
        pass
```

## Dependencies & Integration

### Core Dependencies
- **rich**: Terminal rendering and styling system
- **pygments**: Syntax highlighting for code blocks
- **class-property**: Decorator for class-level properties

### Rich Integration
- Uses Rich's Console for output
- Leverages Rich's Style system for formatting
- Integrates with Rich's renderable protocol

## Performance Considerations

### Memory Management
- Tokens are created and destroyed as needed
- Buffer size is managed to prevent memory leaks
- Style stack is bounded by nesting depth

### Processing Efficiency
- Lazy evaluation where possible
- Minimal backtracking in parsing
- Efficient string operations for chunk processing

## Error Handling

### Graceful Degradation
- Invalid markdown falls back to plain text
- Partial content is buffered until complete
- Malformed elements don't crash the parser

### Logging
- Warning logs for unexpected conditions
- Debug information for development
- Error tracking for troubleshooting

## Testing Strategy

### Unit Tests
- Individual token behavior
- State management correctness
- Edge cases and error conditions

### Integration Tests
- End-to-end parsing scenarios
- Multi-chunk streaming tests
- Rich rendering verification

### Example-based Testing
- Real-world markdown documents
- Chat message scenarios
- Progressive loading simulations

This architecture enables Stream MD to handle real-time markdown parsing while maintaining clean separation of concerns and extensibility for future enhancements.