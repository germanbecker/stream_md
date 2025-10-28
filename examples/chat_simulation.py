#!/usr/bin/env python3
"""
Chat simulation example for stream_md.

This example simulates a chat application where markdown messages
are received and rendered in real-time.
"""

import time
import random
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from stream_md import MarkDownRender


class ChatSimulator:
    """Simulates a chat application with streaming markdown messages."""
    
    def __init__(self):
        self.console = Console()
        self.renderer = MarkDownRender(self.console)
    
    def simulate_typing_delay(self, text: str, base_delay: float = 0.05):
        """Simulate realistic typing delays."""
        for char in text:
            yield char
            # Vary delay based on character type
            if char == ' ':
                time.sleep(base_delay * 2)  # Longer pause for spaces
            elif char in '.,!?':
                time.sleep(base_delay * 3)  # Longer pause for punctuation
            else:
                time.sleep(base_delay + random.uniform(0, base_delay))
    
    def send_message(self, sender: str, message: str, typing_speed: float = 0.05):
        """Simulate sending a message with typing indicator."""
        # Show typing indicator
        typing_text = Text(f"{sender} is typing...", style="dim italic")
        typing_panel = Panel(typing_text, title="💬 Chat", border_style="blue")
        
        with self.console.status("", spinner="dots"):
            self.console.print(typing_panel)
            time.sleep(1)  # Show typing indicator briefly
        
        # Clear the typing indicator
        self.console.clear()
        
        # Show sender name
        sender_text = Text(f"{sender}:", style="bold cyan")
        self.console.print(sender_text)
        
        # Stream the message character by character
        for char in self.simulate_typing_delay(message, typing_speed):
            self.renderer.stream_parse(char)
        
        # End the message
        self.renderer.end_stream()
        self.console.print()  # Add spacing between messages
    
    def run_simulation(self):
        """Run the chat simulation."""
        self.console.print(Panel(
            "Welcome to the Stream MD Chat Demo!\n"
            "Watch as markdown messages are rendered in real-time.",
            title="🚀 Stream MD Chat",
            border_style="green"
        ))
        self.console.print()
        
        # Simulate a conversation
        messages = [
            ("Alice", "Hey everyone! 👋"),
            ("Bob", "Hi Alice! How's the new **streaming markdown parser** coming along?"),
            ("Alice", "It's going great! Check out this code:\n\n```python\nrenderer = MarkDownRender(console)\nrenderer.stream_parse('# Hello **World**!')\n```"),
            ("Charlie", "That looks *amazing*! Does it support lists too?"),
            ("Alice", "Absolutely! Here's an example:\n\n- ✅ **Bold** and *italic* text\n- ✅ Code blocks with syntax highlighting\n- ✅ Headings and paragraphs\n- ✅ Real-time streaming!"),
            ("Bob", "## This is incredible! 🎉\n\nI can see this being useful for:\n\n1. **Chat applications** (like this demo)\n2. *Streaming APIs* that return markdown\n3. **Progressive content loading**"),
            ("Charlie", "The future is *streaming*! 🚀"),
        ]
        
        for sender, message in messages:
            self.send_message(sender, message)
            time.sleep(2)  # Pause between messages
        
        # Final message
        self.console.print(Panel(
            "Demo complete! Thanks for watching the Stream MD chat simulation.",
            title="✨ End of Demo",
            border_style="magenta"
        ))


def main():
    """Main function."""
    simulator = ChatSimulator()
    simulator.run_simulation()


if __name__ == "__main__":
    main()