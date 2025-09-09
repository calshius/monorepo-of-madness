"""
UI utilities and shared functions.

This module contains common UI functions used across different screens.
"""

def format_text_for_display(text: str, max_width: int = 80) -> str:
    """Format text for display with proper line wrapping."""
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        if len(line) > max_width:
            # Word wrap long lines
            words = line.split(' ')
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 <= max_width:
                    current_line.append(word)
                    current_length += len(word) + 1
                else:
                    if current_line:
                        formatted_lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
            
            if current_line:
                formatted_lines.append(' '.join(current_line))
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)


def style_text(text: str, style: str) -> str:
    """Apply textual styling to text."""
    if style:
        return f"[{style}]{text}[/{style}]"
    return text


def get_text_style(text: str) -> str:
    """Determine appropriate style based on text content."""
    text_lower = text.lower()
    
    if "error" in text_lower or "cannot" in text_lower or "fail" in text_lower:
        return "error"
    elif "gained" in text_lower or "level up" in text_lower or "victory" in text_lower:
        return "success"
    elif "says:" in text or "dialogue" in text_lower:
        return "ai_response"
    
    return ""
