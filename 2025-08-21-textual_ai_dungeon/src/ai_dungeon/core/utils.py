"""
Core utility functions and helpers for the AI Dungeon game.
"""

import re
from typing import Dict
from ai_dungeon.core.models import CommandType, GameCommand


class CommandParser:
    """Parses natural language commands into structured game commands."""
    
    def __init__(self):
        self.movement_patterns = [
            r'\b(go|move|walk|run|head|travel)\s+(north|south|east|west|up|down|n|s|e|w)\b',
            r'\b(north|south|east|west|up|down|n|s|e|w)\b'
        ]
        
        self.inventory_patterns = [
            r'\b(take|get|pick up|grab)\s+(.+)',
            r'\b(drop|put down|leave)\s+(.+)',
            r'\b(inventory|inv|items)\b',
            r'\b(use|consume|eat|drink)\s+(.+)'
        ]
        
        self.interaction_patterns = [
            r'\b(look|examine|inspect|check)\s+(.+)',
            r'\b(look|l)\b$',
            r'\b(attack|fight|hit|strike)\s+(.+)',
            r'\b(talk to|speak to|talk with|speak with)\s+(.+)',
            r'\b(open|close|unlock|lock)\s+(.+)'
        ]
        
        self.system_patterns = [
            r'\b(help|h|\?)\b',
            r'\b(quit|exit|q)\b',
            r'\b(save|save game)\b',
            r'\b(load|load game)\b',
            r'\b(status|stats)\b'
        ]
        
        # Direction mappings
        self.direction_map = {
            'n': 'north', 's': 'south', 'e': 'east', 'w': 'west',
            'north': 'north', 'south': 'south', 'east': 'east', 'west': 'west',
            'up': 'up', 'down': 'down'
        }
    
    def parse_command(self, raw_command: str) -> GameCommand:
        """Parse a raw command string into a structured GameCommand."""
        command = raw_command.lower().strip()
        
        if not command:
            return GameCommand(
                raw_command=raw_command,
                command_type=CommandType.UNKNOWN,
                action="empty"
            )
        
        # Try to match movement patterns
        for pattern in self.movement_patterns:
            match = re.search(pattern, command)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    direction = self.direction_map.get(groups[1], groups[1])
                elif len(groups) == 1:
                    direction = self.direction_map.get(groups[0], groups[0])
                else:
                    continue
                
                return GameCommand(
                    raw_command=raw_command,
                    command_type=CommandType.MOVEMENT,
                    action="move",
                    target=direction
                )
        
        # Try to match inventory patterns
        for pattern in self.inventory_patterns:
            match = re.search(pattern, command)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    action = groups[0].replace(" ", "_")
                    target = groups[1].strip()
                    return GameCommand(
                        raw_command=raw_command,
                        command_type=CommandType.INVENTORY,
                        action=action,
                        target=target
                    )
                elif "inventory" in groups[0] or "inv" in groups[0] or "items" in groups[0]:
                    return GameCommand(
                        raw_command=raw_command,
                        command_type=CommandType.INVENTORY,
                        action="show_inventory"
                    )
        
        # Try to match interaction patterns
        for pattern in self.interaction_patterns:
            match = re.search(pattern, command)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    action = groups[0].replace(" ", "_")
                    target = groups[1].strip()
                    return GameCommand(
                        raw_command=raw_command,
                        command_type=CommandType.INTERACTION,
                        action=action,
                        target=target
                    )
                elif len(groups) == 1 and (groups[0] == "look" or groups[0] == "l"):
                    return GameCommand(
                        raw_command=raw_command,
                        command_type=CommandType.INTERACTION,
                        action="look_around"
                    )
        
        # Try to match system patterns
        for pattern in self.system_patterns:
            match = re.search(pattern, command)
            if match:
                action = match.group(1)
                if action in ['h', '?']:
                    action = 'help'
                elif action in ['q']:
                    action = 'quit'
                
                return GameCommand(
                    raw_command=raw_command,
                    command_type=CommandType.SYSTEM,
                    action=action
                )
        
        # Check for dialogue patterns
        if any(word in command for word in ['say', 'tell', 'ask', 'talk', 'speak']):
            return GameCommand(
                raw_command=raw_command,
                command_type=CommandType.DIALOGUE,
                action="dialogue",
                target=command
            )
        
        # Default to unknown command
        return GameCommand(
            raw_command=raw_command,
            command_type=CommandType.UNKNOWN,
            action="unknown",
            target=command
        )


def format_text(text: str, max_width: int = 80) -> str:
    """Format text for display with proper line wrapping."""
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= max_width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return '\n'.join(lines)


def sanitize_name(name: str) -> str:
    """Sanitize a name for use as an identifier."""
    # Replace spaces and special characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    return sanitized.strip('_')


def calculate_distance(location1: str, location2: str, world_map: Dict) -> int:
    """Calculate the distance between two locations."""
    # Simple BFS to find shortest path
    if location1 == location2:
        return 0
    
    from collections import deque
    
    queue = deque([(location1, 0)])
    visited = {location1}
    
    while queue:
        current_location, distance = queue.popleft()
        
        if current_location not in world_map:
            continue
        
        location_obj = world_map[current_location]
        for exit_location in location_obj.exits.values():
            if exit_location == location2:
                return distance + 1
            
            if exit_location not in visited:
                visited.add(exit_location)
                queue.append((exit_location, distance + 1))
    
    return -1  # No path found
