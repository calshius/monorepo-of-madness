import * as vscode from 'vscode';
import fetch from 'node-fetch';
import * as cheerio from 'cheerio';

interface RecipeSearchInput {
    query: string;
    maxResults?: number;
}

interface Recipe {
    title: string;
    url: string;
    description: string;
    cookingTime?: string;
    servings?: string;
    difficulty?: string;
    imageUrl?: string;
    chef?: string;
}

export class RecipeProvider implements vscode.LanguageModelTool<RecipeSearchInput> {
    private cache = new Map<string, Recipe[]>();
    private readonly baseUrl = 'https://www.bbc.co.uk/food/recipes';

    async prepareInvocation(
        options: vscode.LanguageModelToolInvocationPrepareOptions<RecipeSearchInput>,
        _token: vscode.CancellationToken
    ) {
        const confirmationMessages = {
            title: 'Search BBC Food for Recipes',
            message: new vscode.MarkdownString(
                `Search BBC Food for "${options.input.query}" recipes?` +
                (options.input.maxResults 
                    ? ` (showing up to ${options.input.maxResults} results)`
                    : ' (showing up to 8 results)')
            ),
        };

        return {
            invocationMessage: `Searching BBC Food for "${options.input.query}" recipes...`,
            confirmationMessages,
        };
    }

    async invoke(
        options: vscode.LanguageModelToolInvocationOptions<RecipeSearchInput>,
        _token: vscode.CancellationToken
    ): Promise<vscode.LanguageModelToolResult> {
        const input = options.input;

        try {
            const recipes = await this.searchRecipes(input.query, input.maxResults || 10);

            if (recipes.length === 0) {
                return new vscode.LanguageModelToolResult([
                    new vscode.LanguageModelTextPart(
                        `No recipes found for "${input.query}". Try searching for ingredients like "chicken", "pasta", or dish names like "curry", "soup".`
                    )
                ]);
            }

            return new vscode.LanguageModelToolResult([
                new vscode.LanguageModelTextPart(
                    this.formatRecipes(recipes, input.query)
                )
            ]);
        } catch (error) {
            return new vscode.LanguageModelToolResult([
                new vscode.LanguageModelTextPart(
                    `Error searching for recipes: ${error instanceof Error ? error.message : 'Unknown error'}`
                )
            ]);
        }
    }

    private async searchRecipes(query: string, maxResults: number): Promise<Recipe[]> {
        // Check cache first
        const cacheKey = `${query}_${maxResults}`;
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey)!;
        }

        // BBC Food search URL - using the correct format
        const searchUrl = `https://www.bbc.co.uk/food/search?q=${encodeURIComponent(query)}`;
        const response = await fetch(searchUrl, {
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to search recipes: ${response.status} ${response.statusText}`);
        }

        const html = await response.text();
        const $ = cheerio.load(html);

        const recipes: Recipe[] = [];

        // Look for recipe links in the search results
        // BBC Food uses links that contain recipe information in the link text
        $('a[href*="/food/recipes/"]').each((index, element) => {
            if (index >= maxResults) return false; // Stop when we have enough

            const $link = $(element);
            const href = $link.attr('href');
            
            // Get clean text content, excluding any image tags
            const $clone = $link.clone();
            $clone.find('img').remove(); // Remove any images
            const linkText = $clone.text().trim();
            
            if (!href || !linkText || linkText.length < 10) return; // Skip if not enough info
            
            // Parse the link text which contains recipe info
            // Format: "Recipe Name by Chef COURSE Serves X Prep: Y Cook: Z"
            const url = href.startsWith('http') ? href : `https://www.bbc.co.uk${href}`;
            
            // Extract recipe title (everything before " by ")
            let title = linkText;
            let chef = '';
            let courseInfo = '';
            let prepTime = '';
            let cookTime = '';
            let servings = '';
            
            const byMatch = linkText.match(/^(.+?)\s+by\s+(.+?)(\s+[A-Z][A-Z\s]+.*)$/);
            if (byMatch) {
                title = byMatch[1].trim();
                const remainder = byMatch[2] + byMatch[3];
                
                // Find where the chef name ends and course info begins
                const courseMatch = remainder.match(/^(.+?)\s+(MAIN COURSE|STARTER|DESSERT|SIDE DISH|SNACK|CANAPÉ|BREAKFAST|LIGHT MEALS|DINNER PARTY|AFTERNOON TEA|DESSERTS)(.*)$/);
                if (courseMatch) {
                    chef = courseMatch[1].trim();
                    courseInfo = courseMatch[2] + courseMatch[3];
                } else {
                    chef = remainder.trim();
                }
            }
            
            // Extract serving, prep, and cook info from courseInfo
            if (courseInfo) {
                const servesMatch = courseInfo.match(/Serves?\s+([^P]+?)(?=\s+Prep:|$)/);
                if (servesMatch) servings = servesMatch[1].trim();
                
                const prepMatch = courseInfo.match(/Prep:\s+([^C]+?)(?=\s+Cook:|$)/);
                if (prepMatch) prepTime = prepMatch[1].trim();
                
                const cookMatch = courseInfo.match(/Cook:\s*(.+?)$/);
                if (cookMatch) cookTime = cookMatch[1].trim();
            }
            
            // Only add if we have a meaningful title
            if (title && title.length > 3 && !title.includes('srcSet')) {
                recipes.push({
                    title,
                    url,
                    description: chef ? `by ${chef}` : '',
                    chef: chef || undefined,
                    servings: servings || undefined,
                    cookingTime: cookTime || undefined
                });
            }
        });

        // If we still don't have recipes, try alternative selectors
        if (recipes.length === 0) {
            // Look for any links with recipe URLs
            $('a').each((index, element) => {
                if (index >= maxResults) return false;
                
                const $link = $(element);
                const href = $link.attr('href');
                
                if (href && href.includes('/food/recipes/') && href.length > 20) {
                    const url = href.startsWith('http') ? href : `https://www.bbc.co.uk${href}`;
                    const title = $link.text().trim() || 'BBC Food Recipe';
                    
                    if (title.length > 5) {
                        recipes.push({
                            title,
                            url,
                            description: 'Recipe from BBC Food'
                        });
                    }
                }
            });
        }

        // Cache the results
        this.cache.set(cacheKey, recipes);

        return recipes;
    }

    private formatRecipes(recipes: Recipe[], query: string): string {
        let result = `# 🍳 BBC Food Recipes for "${query}"\n\n`;
        result += `Found ${recipes.length} recipe${recipes.length === 1 ? '' : 's'}:\n\n`;

        recipes.forEach((recipe, index) => {
            // Format: "Recipe Name (hyperlink) - Cook time - by Chef"
            let line = `${index + 1}. **[${recipe.title}](${recipe.url})**`;
            
            // Add cooking time if available
            if (recipe.cookingTime) {
                line += ` - ⏱️ ${recipe.cookingTime}`;
            }
            
            // Add chef if available
            if (recipe.chef) {
                line += ` - 👨‍🍳 ${recipe.chef}`;
            }
            
            // Add servings if available
            if (recipe.servings) {
                line += ` - 👥 Serves ${recipe.servings}`;
            }
            
            result += line + '\n\n';
        });

        result += '*Recipes from BBC Food*';

        return result;
    }
}
