"""
AI integration using LangGraph and Google Gemini.

This module provides the AI-powered world generation, dialogue,
and narrative systems using LangGraph for orchestration.
"""

import os
import random
from typing import Dict, List, Optional, Any, TypedDict
from dataclasses import dataclass
import json

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.prompts import ChatPromptTemplate
    from langgraph.graph import Graph, StateGraph, START, END
    from langgraph.graph.message import add_messages
    from typing_extensions import Annotated
except ImportError:
    # Fallback for when dependencies aren't installed
    print("Warning: LangGraph and Gemini dependencies not installed. AI features will be limited.")
    ChatGoogleGenerativeAI = None
    HumanMessage = AIMessage = SystemMessage = None
    ChatPromptTemplate = None
    Graph = StateGraph = START = END = None
    add_messages = None
    Annotated = None


class AIState(TypedDict):
    """State for the AI workflow."""
    messages: Annotated[List, add_messages] if add_messages else List
    context: Dict[str, Any]
    task_type: str
    result: Optional[str]


@dataclass
class WorldGenerationRequest:
    """Request for AI world generation."""
    task_type: str  # "location", "npc", "item", "dialogue", "description"
    context: Dict[str, Any]
    parameters: Dict[str, Any]


class GeminiAIEngine:
    """AI engine using Google Gemini for content generation."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI engine."""
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            print("Warning: No Google API key found. Set GOOGLE_API_KEY environment variable.")
            self.llm = None
        else:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=self.api_key,
                    temperature=0.8,
                    max_tokens=1024
                ) if ChatGoogleGenerativeAI else None
            except Exception as e:
                print(f"Error initializing Gemini: {e}")
                self.llm = None
        
        self.workflow = self._create_workflow() if StateGraph else None
    
    def _create_workflow(self) -> Optional[StateGraph]:
        """Create the LangGraph workflow for AI operations."""
        if not StateGraph:
            return None
        
        workflow = StateGraph(AIState)
        
        # Add nodes
        workflow.add_node("analyze_request", self._analyze_request)
        workflow.add_node("generate_location", self._generate_location)
        workflow.add_node("generate_npc", self._generate_npc)
        workflow.add_node("generate_item", self._generate_item)
        workflow.add_node("generate_dialogue", self._generate_dialogue)
        workflow.add_node("generate_description", self._generate_description)
        workflow.add_node("format_response", self._format_response)
        
        # Add edges
        workflow.add_edge(START, "analyze_request")
        
        # Conditional routing based on task type
        workflow.add_conditional_edges(
            "analyze_request",
            self._route_task,
            {
                "location": "generate_location",
                "npc": "generate_npc",
                "item": "generate_item",
                "dialogue": "generate_dialogue",
                "description": "generate_description"
            }
        )
        
        # All generation nodes lead to formatting
        workflow.add_edge("generate_location", "format_response")
        workflow.add_edge("generate_npc", "format_response")
        workflow.add_edge("generate_item", "format_response")
        workflow.add_edge("generate_dialogue", "format_response")
        workflow.add_edge("generate_description", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def _route_task(self, state: AIState) -> str:
        """Route the task to the appropriate generation node."""
        return state.get("task_type", "description")
    
    async def _analyze_request(self, state: AIState) -> AIState:
        """Analyze the incoming request and prepare context."""
        # Extract useful information from context
        context = state.get("context", {})
        task_type = state.get("task_type", "description")
        
        # Add system context message
        system_msg = SystemMessage(content=f"""
You are an AI assistant for a text-based adventure game. You create immersive, 
detailed content that fits within a fantasy/medieval setting. Your task is to 
generate {task_type} content that is:

1. Descriptive and atmospheric
2. Consistent with existing game world
3. Engaging and interactive
4. Appropriate for a text adventure game

Always respond with valid JSON when requested.
""")
        
        messages = state.get("messages", [])
        messages.insert(0, system_msg)
        
        return {**state, "messages": messages}
    
    async def _generate_location(self, state: AIState) -> AIState:
        """Generate a new location."""
        if not self.llm:
            return {**state, "result": self._fallback_location()}
        
        context = state.get("context", {})
        
        prompt = f"""
Generate a new location for a text adventure game. Consider this context:
- Current location: {context.get('current_location', 'unknown')}
- Player direction: {context.get('direction', 'unknown')}
- Game state: {context.get('game_state', {})}

Create a JSON object with these fields:
- name: A unique identifier (snake_case)
- description: Detailed atmospheric description (2-3 sentences)
- exits: Dictionary of directions to other locations
- items: List of items that might be found here
- npcs: List of NPCs that might be present
- first_visit_description: Special description for first visit

Make it atmospheric and interesting!
"""
        
        try:
            messages = state.get("messages", [])
            messages.append(HumanMessage(content=prompt))
            
            response = await self.llm.ainvoke(messages)
            result = response.content
            
            messages.append(AIMessage(content=result))
            return {**state, "messages": messages, "result": result}
        except Exception as e:
            print(f"Error generating location: {e}")
            return {**state, "result": self._fallback_location()}
    
    async def _generate_npc(self, state: AIState) -> AIState:
        """Generate a new NPC."""
        if not self.llm:
            return {**state, "result": self._fallback_npc()}
        
        context = state.get("context", {})
        
        prompt = f"""
Generate an NPC for a text adventure game. Context:
- Location: {context.get('location', 'unknown')}
- Game state: {context.get('game_state', {})}

Create a JSON object with:
- name: Character name
- description: Physical and personality description
- dialogue_state: "initial" 
- disposition: "friendly", "neutral", or "hostile"
- properties: Dictionary with relevant traits

Make them interesting and memorable!
"""
        
        try:
            messages = state.get("messages", [])
            messages.append(HumanMessage(content=prompt))
            
            response = await self.llm.ainvoke(messages)
            result = response.content
            
            messages.append(AIMessage(content=result))
            return {**state, "messages": messages, "result": result}
        except Exception as e:
            print(f"Error generating NPC: {e}")
            return {**state, "result": self._fallback_npc()}
    
    async def _generate_item(self, state: AIState) -> AIState:
        """Generate a new item."""
        if not self.llm:
            return {**state, "result": self._fallback_item()}
        
        context = state.get("context", {})
        
        prompt = f"""
Generate an item for a text adventure game. Context:
- Location: {context.get('location', 'unknown')}
- Item type hint: {context.get('item_type', 'misc')}

Create a JSON object with:
- name: Item name
- description: Detailed description
- item_type: "weapon", "armor", "key", "consumable", "treasure", or "misc"
- weight: Number (0-10)
- value: Number (0-1000)
- usable: Boolean
- consumable: Boolean
- properties: Dictionary with special attributes

Make it fit the fantasy setting!
"""
        
        try:
            messages = state.get("messages", [])
            messages.append(HumanMessage(content=prompt))
            
            response = await self.llm.ainvoke(messages)
            result = response.content
            
            messages.append(AIMessage(content=result))
            return {**state, "messages": messages, "result": result}
        except Exception as e:
            print(f"Error generating item: {e}")
            return {**state, "result": self._fallback_item()}
    
    async def _generate_dialogue(self, state: AIState) -> AIState:
        """Generate NPC dialogue."""
        if not self.llm:
            return {**state, "result": "The NPC nods mysteriously and says nothing."}
        
        context = state.get("context", {})
        
        prompt = f"""
Generate dialogue for an NPC in a text adventure game. Context:
- NPC: {context.get('npc_name', 'unknown character')}
- Player action: {context.get('player_action', 'talks to NPC')}
- Conversation history: {context.get('dialogue_history', [])}
- NPC disposition: {context.get('disposition', 'neutral')}

Respond as the NPC would, staying in character. Keep it to 1-3 sentences.
Be helpful but maintain some mystery. Don't break the fourth wall.
"""
        
        try:
            messages = state.get("messages", [])
            messages.append(HumanMessage(content=prompt))
            
            response = await self.llm.ainvoke(messages)
            result = response.content
            
            messages.append(AIMessage(content=result))
            return {**state, "messages": messages, "result": result}
        except Exception as e:
            print(f"Error generating dialogue: {e}")
            return {**state, "result": "The character looks at you thoughtfully but remains silent."}
    
    async def _generate_description(self, state: AIState) -> AIState:
        """Generate atmospheric descriptions."""
        if not self.llm:
            return {**state, "result": "Something interesting happens."}
        
        context = state.get("context", {})
        
        prompt = f"""
Generate an atmospheric description for a text adventure game. Context:
- Action: {context.get('action', 'unknown action')}
- Location: {context.get('location', 'unknown location')}
- Game state: {context.get('game_state', {})}

Create a 1-2 sentence description that brings the action to life.
Be descriptive and immersive but concise.
"""
        
        try:
            messages = state.get("messages", [])
            messages.append(HumanMessage(content=prompt))
            
            response = await self.llm.ainvoke(messages)
            result = response.content
            
            messages.append(AIMessage(content=result))
            return {**state, "messages": messages, "result": result}
        except Exception as e:
            print(f"Error generating description: {e}")
            return {**state, "result": "You sense that something significant has occurred."}
    
    async def _format_response(self, state: AIState) -> AIState:
        """Format the final response."""
        result = state.get("result", "")
        task_type = state.get("task_type", "")
        
        # For JSON responses, try to parse and validate
        if task_type in ["location", "npc", "item"]:
            try:
                # Extract JSON from response if it's wrapped in markdown or other text
                json_start = result.find('{')
                json_end = result.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = result[json_start:json_end]
                    parsed = json.loads(json_str)
                    result = json.dumps(parsed, indent=2)
            except (json.JSONDecodeError, ValueError):
                # If parsing fails, use fallback
                if task_type == "location":
                    result = self._fallback_location()
                elif task_type == "npc":
                    result = self._fallback_npc()
                elif task_type == "item":
                    result = self._fallback_item()
        
        return {**state, "result": result}
    
    def _fallback_location(self) -> str:
        """Fallback location generation when AI is unavailable."""
        import random
        
        templates = [
            {
                "name": "mysterious_chamber",
                "description": "A dimly lit chamber with strange symbols carved into the walls.",
                "exits": {"north": "unknown_passage", "back": "previous_location"},
                "items": ["ancient_artifact"],
                "npcs": [],
                "first_visit_description": "You discover a hidden chamber that seems untouched by time."
            },
            {
                "name": "forest_clearing",
                "description": "A peaceful clearing surrounded by ancient trees. Sunlight filters through the canopy above.",
                "exits": {"north": "deep_woods", "south": "forest_path", "east": "old_oak"},
                "items": ["wildflowers"],
                "npcs": [],
                "first_visit_description": "You emerge into a beautiful clearing that feels magical and serene."
            }
        ]
        
        return json.dumps(random.choice(templates), indent=2)
    
    def _fallback_npc(self) -> str:
        """Fallback NPC generation when AI is unavailable."""
        import random
        
        templates = [
            {
                "name": "Mysterious Traveler",
                "description": "A cloaked figure with knowing eyes who seems to have seen much of the world.",
                "dialogue_state": "initial",
                "disposition": "neutral",
                "properties": {"helpful": True, "mysterious": True}
            },
            {
                "name": "Village Elder",
                "description": "An elderly person with wisdom etched in their weathered face.",
                "dialogue_state": "initial",
                "disposition": "friendly",
                "properties": {"wise": True, "local_knowledge": True}
            }
        ]
        
        return json.dumps(random.choice(templates), indent=2)
    
    def _fallback_item(self) -> str:
        """Fallback item generation when AI is unavailable."""
        import random
        
        templates = [
            {
                "name": "strange rune",
                "description": "A small stone carved with mysterious symbols that seem to shift when you're not looking directly at them.",
                "item_type": "misc",
                "weight": 1,
                "value": 25,
                "usable": False,
                "consumable": False,
                "properties": {"magical": True}
            },
            {
                "name": "worn leather pouch",
                "description": "A well-used leather pouch that jingles softly when moved.",
                "item_type": "misc",
                "weight": 1,
                "value": 10,
                "usable": True,
                "consumable": False,
                "properties": {"container": True}
            }
        ]
        
        return json.dumps(random.choice(templates), indent=2)
    
    def _fallback_combat(self) -> str:
        """Generate fallback combat scenarios."""
        scenarios = [
            "You engage in fierce battle! Your weapon clashes against the enemy's defenses. After a tense struggle, you emerge victorious!",
            "The fight is intense! You dodge a vicious attack and counter with a powerful strike. Your enemy falls defeated!",
            "Combat ensues! You use your skills wisely, finding an opening in your opponent's guard. Victory is yours!",
            "The battle rages! Though wounded, your determination carries you through. Your enemy retreats in defeat!",
            "You clash with your foe! Using clever tactics, you outmaneuver your opponent and claim victory!"
        ]
        return random.choice(scenarios)
    
    def _fallback_dialogue(self) -> str:
        """Generate fallback dialogue responses."""
        responses = [
            "The character nods thoughtfully and shares some local wisdom with you.",
            "They seem friendly and tell you about interesting places nearby.",
            "The character warns you about dangers ahead but offers helpful advice.",
            "They share a fascinating story about the area's mysterious history.",
            "The character seems knowledgeable and points out useful information about your surroundings."
        ]
        return random.choice(responses)
    
    async def generate_content(self, request: WorldGenerationRequest) -> str:
        """Generate content using the AI workflow."""
        if not self.workflow:
            # Fallback when workflow is not available
            if request.task_type == "location":
                return self._fallback_location()
            elif request.task_type == "npc":
                return self._fallback_npc()
            elif request.task_type == "item":
                return self._fallback_item()
            elif request.task_type == "combat":
                return self._fallback_combat()
            elif request.task_type == "dialogue":
                return self._fallback_dialogue()
            else:
                return "Something interesting happens in the game world."
        
        initial_state = AIState(
            messages=[],
            context=request.context,
            task_type=request.task_type,
            result=None
        )
        
        try:
            result = await self.workflow.ainvoke(initial_state)
            return result.get("result", "")
        except Exception as e:
            print(f"Error in AI workflow: {e}")
            # Use fallbacks
            if request.task_type == "location":
                return self._fallback_location()
            elif request.task_type == "npc":
                return self._fallback_npc()
            elif request.task_type == "item":
                return self._fallback_item()
            elif request.task_type == "combat":
                return self._fallback_combat()
            elif request.task_type == "dialogue":
                return self._fallback_dialogue()
            else:
                return "The world responds mysteriously to your actions."
