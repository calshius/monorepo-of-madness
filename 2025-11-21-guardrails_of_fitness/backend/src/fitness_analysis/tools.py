"""Tools for the fitness analysis agent."""

from typing import Annotated, Any, Dict
from langchain_core.tools import tool
import httpx
from .data_loader import FitnessDataLoader

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


# Initialize data loader
data_loader = FitnessDataLoader()


@tool
def get_fitness_data_summary(days: Annotated[int, "Number of days to analyze"] = 30) -> str:
    """Get a comprehensive summary of fitness data including nutrition and activity data.
    
    Args:
        days: Number of recent days to analyze (default: 30)
    
    Returns:
        A formatted string with nutrition and activity statistics
    """
    return data_loader.get_combined_summary(days)


@tool
def get_nutrition_details(days: Annotated[int, "Number of days to analyze"] = 30) -> Dict[str, Any]:
    """Get detailed nutrition statistics including macros breakdown.
    
    Args:
        days: Number of recent days to analyze (default: 30)
    
    Returns:
        Dictionary with detailed nutrition statistics
    """
    return data_loader.get_nutrition_summary(days)


@tool
def get_activity_details(days: Annotated[int, "Number of days to analyze"] = 30) -> Dict[str, Any]:
    """Get detailed activity and exercise statistics.
    
    Args:
        days: Number of recent days to analyze (default: 30)
    
    Returns:
        Dictionary with detailed activity statistics
    """
    return data_loader.get_activity_summary(days)


@tool
async def search_recipes(
    query: Annotated[str, "Search query for recipes"],
    max_results: Annotated[int, "Maximum number of recipes to return"] = 5
) -> str:
    """Search for recipes online by ingredient or dish name and return detailed recipe information.
    
    Args:
        query: The recipe search query (ingredient, dish name, etc.)
        max_results: Maximum number of recipes to return (default: 5)
    
    Returns:
        A formatted string with recipe details including title, description, and link
    """
    if not HAS_BS4:
        return "Recipe search requires beautifulsoup4. Please install it: pip install beautifulsoup4"
    
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            # Search BBC Food - using the correct query parameter 'q' instead of 'query'
            search_url = f"https://www.bbc.co.uk/food/search?q={query}"
            response = await client.get(
                search_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
            )
            
            if response.status_code != 200:
                return f"Could not search recipes (status {response.status_code})"
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            recipes = []
            
            # Look for recipe links - BBC Food uses links that contain recipe info in link text
            recipe_links = soup.find_all('a', href=lambda href: href and '/food/recipes/' in href, limit=max_results * 2)
            
            for link in recipe_links[:max_results]:
                try:
                    href = link.get('href', '')
                    if not href:
                        continue
                    
                    # Get clean text content, excluding any image tags
                    link_text = link.get_text(strip=True)
                    
                    # Skip if not enough info
                    if not link_text or len(link_text) < 10:
                        continue
                    
                    # Build full URL
                    url = href if href.startswith('http') else f"https://www.bbc.co.uk{href}"
                    
                    # Parse link text for recipe info
                    # Format: "Recipe Name by Chef COURSE Serves X Prep: Y Cook: Z"
                    title = link_text
                    chef = None
                    servings = None
                    cook_time = None
                    
                    # Extract title and chef (everything before " by ")
                    if ' by ' in link_text:
                        parts = link_text.split(' by ', 1)
                        title = parts[0].strip()
                        remainder = parts[1] if len(parts) > 1 else ''
                        
                        # Extract chef (before course info in CAPS)
                        import re
                        course_match = re.search(r'\s+(MAIN COURSE|STARTER|DESSERT|SIDE DISH|SNACK|BREAKFAST|LIGHT MEALS)', remainder)
                        if course_match:
                            chef = remainder[:course_match.start()].strip()
                            course_info = remainder[course_match.start():]
                            
                            # Extract servings
                            serves_match = re.search(r'Serves?\s+([^P]+?)(?=\s+Prep:|$)', course_info)
                            if serves_match:
                                servings = serves_match.group(1).strip()
                            
                            # Extract cook time
                            cook_match = re.search(r'Cook:\s*(.+?)$', course_info)
                            if cook_match:
                                cook_time = cook_match.group(1).strip()
                        else:
                            chef = remainder.strip()
                    
                    # Only add if we have a meaningful title
                    if title and len(title) > 3 and 'srcSet' not in title:
                        recipe_info = {
                            "title": title,
                            "url": url,
                            "chef": chef,
                            "servings": servings,
                            "cook_time": cook_time
                        }
                        recipes.append(recipe_info)
                        
                except Exception:
                    continue
            
            # If we still don't have recipes, try finding any recipe links
            if not recipes:
                all_links = soup.find_all('a', href=True)
                for link in all_links[:max_results]:
                    href = link.get('href', '')
                    if '/food/recipes/' in href and len(href) > 20:
                        url = href if href.startswith('http') else f"https://www.bbc.co.uk{href}"
                        title = link.get_text(strip=True) or 'BBC Food Recipe'
                        
                        if len(title) > 5:
                            recipes.append({
                                "title": title,
                                "url": url,
                                "chef": None,
                                "servings": None,
                                "cook_time": None
                            })
            
            if not recipes:
                return f"No recipes found for '{query}'. Try a different search term."
            
            # Format the results
            result = f"Found {len(recipes)} recipe(s) for '{query}':\n\n"
            
            for i, recipe in enumerate(recipes, 1):
                result += f"**{i}. {recipe['title']}**\n"
                
                # Add cooking time if available
                if recipe.get('cook_time'):
                    result += f"   ⏱️ {recipe['cook_time']}\n"
                
                # Add chef if available
                if recipe.get('chef'):
                    result += f"   👨‍🍳 {recipe['chef']}\n"
                
                # Add servings if available
                if recipe.get('servings'):
                    result += f"   👥 Serves {recipe['servings']}\n"
                
                result += f"   Link: {recipe['url']}\n\n"
            
            return result.strip()
            
    except httpx.TimeoutException:
        return "Request timed out while searching for recipes. Please try again."
    except Exception as e:
        return f"Error searching recipes: {str(e)}"


@tool
def calculate_tdee(
    age: Annotated[int, "Age in years"],
    weight_kg: Annotated[float, "Weight in kilograms"],
    height_cm: Annotated[float, "Height in centimeters"],
    activity_level: Annotated[str, "Activity level: sedentary, light, moderate, active, very_active"],
    gender: Annotated[str, "Gender: male or female"]
) -> Dict[str, Any]:
    """Calculate Total Daily Energy Expenditure (TDEE) and recommended macros.
    
    Args:
        age: Age in years
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        activity_level: Activity level (sedentary, light, moderate, active, very_active)
        gender: Gender (male or female)
    
    Returns:
        Dictionary with TDEE and macro recommendations
    """
    # Calculate BMR using Mifflin-St Jeor Equation
    if gender.lower() == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    
    # Activity multipliers
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.55)
    tdee = bmr * multiplier
    
    # Calculate macros (using standard recommendations)
    protein_g = weight_kg * 2.2  # 2.2g per kg for active individuals
    fat_g = tdee * 0.25 / 9  # 25% of calories from fat
    carbs_g = (tdee - (protein_g * 4) - (fat_g * 9)) / 4  # Remaining calories from carbs
    
    return {
        "bmr": round(bmr, 1),
        "tdee": round(tdee, 1),
        "recommended_macros": {
            "protein_g": round(protein_g, 1),
            "fat_g": round(fat_g, 1),
            "carbs_g": round(carbs_g, 1)
        },
        "macro_percentages": {
            "protein": round((protein_g * 4 / tdee) * 100, 1),
            "fat": round((fat_g * 9 / tdee) * 100, 1),
            "carbs": round((carbs_g * 4 / tdee) * 100, 1)
        }
    }


@tool
def generate_mermaid_diagram(
    diagram_type: Annotated[str, "Type of diagram: flowchart, sequence, gantt, pie, class, or xychart"],
    description: Annotated[str, "Description of what the diagram should visualize"],
    data_points: Annotated[str, "Key data points or steps to include in the diagram"] = ""
) -> str:
    """Generate a Mermaid diagram based on user requirements. Use this when users ask for visualizations, diagrams, charts, graphs, or flowcharts.
    
    Args:
        diagram_type: Type of diagram (flowchart, sequence, gantt, pie, class, xychart)
        description: What the diagram should show
        data_points: Specific data or steps to include
    
    Returns:
        Instructions for generating a properly formatted mermaid diagram
    """
    
    if diagram_type == "xychart":
        return f"""Generate an XY chart for '{description}' using this EXACT syntax format:

```mermaid
xychart
    title "{description}"
    x-axis [label1, label2, label3, label4, label5, label6]
    y-axis "Y-axis Label" minValue --> maxValue
    line [value1, value2, value3, value4, value5, value6]
```

CRITICAL RULES for xychart:
1. Start with ONLY 'xychart' on the first line (NOT 'graph' or 'flowchart')
2. Use 'title' for the chart title
3. x-axis must be: x-axis [item1, item2, item3]
4. y-axis format: y-axis "Label" min --> max
5. Data format: line [num1, num2, num3] or bar [num1, num2, num3]
6. You can combine: both line and bar in same chart
7. Number of data points MUST match number of x-axis labels

Example for weight loss over 6 months (90kg to 85kg):
```mermaid
xychart
    title "Expected Weight Loss Progress"
    x-axis [Month 0, Month 1, Month 2, Month 3, Month 4, Month 5, Month 6]
    y-axis "Weight (kg)" 84 --> 91
    line [90, 89.2, 88.3, 87.5, 86.7, 85.8, 85]
```

Data to include: {data_points if data_points else 'Use relevant numerical data'}

Now generate the xychart with proper syntax."""
    
    # Return instructions for other diagram types
    return f"""To create a {diagram_type} diagram for '{description}':

1. Use proper Mermaid syntax for {diagram_type} diagrams
2. Include these elements: {data_points if data_points else 'relevant information from context'}
3. Format it in a code block with ```mermaid at the start
4. Make it clear, well-structured, and easy to read

Example structure for {diagram_type}:
{_get_mermaid_example(diagram_type)}

Now generate the actual diagram based on the user's request."""


def _get_mermaid_example(diagram_type: str) -> str:
    """Get example mermaid syntax for different diagram types."""
    examples = {
        "flowchart": """```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C{Decision}
    C -->|Yes| D[Result 1]
    C -->|No| E[Result 2]
```""",
        "sequence": """```mermaid
sequenceDiagram
    participant User
    participant System
    User->>System: Request
    System->>User: Response
```""",
        "gantt": """```mermaid
gantt
    title Project Timeline
    dateFormat YYYY-MM-DD
    section Phase 1
    Task 1 :2024-01-01, 30d
```""",
        "pie": """```mermaid
pie title Distribution
    "Category A" : 45
    "Category B" : 30
    "Category C" : 25
```""",
        "class": """```mermaid
classDiagram
    class ClassName {
        +attribute
        +method()
    }
```""",
        "xychart": """```mermaid
xychart
    title "Example Chart"
    x-axis [jan, feb, mar, apr, may, jun]
    y-axis "Values" 0 --> 100
    bar [45, 60, 75, 80, 65, 70]
    line [40, 55, 70, 85, 75, 65]
```

For XY charts you can:
- Use 'bar' for bar charts with data like: bar [value1, value2, ...]
- Use 'line' for line charts with data like: line [value1, value2, ...]
- Combine both bar and line in the same chart
- Set x-axis with categories: x-axis [cat1, cat2, ...]
- Set y-axis with title and range: y-axis "Title" min --> max
- Use 'horizontal' for horizontal orientation: xychart horizontal
- Add title with: title "Chart Title"
"""
    }
    return examples.get(diagram_type, examples["flowchart"])


# List of all tools for the agent
ALL_TOOLS = [
    get_fitness_data_summary,
    get_nutrition_details,
    get_activity_details,
    search_recipes,
    calculate_tdee,
    generate_mermaid_diagram,
]
