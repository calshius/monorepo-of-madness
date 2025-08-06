import * as vscode from 'vscode';
import { RecipeProvider } from './recipeSearch';

export function activate(context: vscode.ExtensionContext) {
    console.log('Activating Recipe Finder Copilot participant...');

    try {
        const recipeProvider = new RecipeProvider();
        console.log('RecipeProvider created successfully');

        // Register as a Language Model Tool for agent mode
        const tool = vscode.lm.registerTool('recipe_search', recipeProvider);
        context.subscriptions.push(tool);
        console.log('Language Model Tool registered for agent mode');

        // Register the search command
        const searchCommand = vscode.commands.registerCommand('recipe-finder.search', async () => {
            vscode.window.showInformationMessage('Recipe Finder extension is active! Use @recipe in chat or the recipe_search tool in agent mode.');
        });
        context.subscriptions.push(searchCommand);

        // Create a chat participant for recipe searching
        const participant = vscode.chat.createChatParticipant('recipe.finder', async (request, context, stream, token) => {
            console.log('Recipe participant invoked with:', request.prompt);

            try {
                const query = request.prompt.trim();

                if (!query) {
                    stream.markdown('Please tell me what recipe you\'re looking for! Examples:\n- `@recipe chicken curry`\n- `@recipe chocolate cake`\n- `@recipe pasta with tomatoes`\n- `@recipe vegetarian soup`');
                    return;
                }

                stream.markdown(`🔍 Searching BBC Food for "${query}" recipes...\n\n`);

                // Use the recipe provider to search
                const result = await recipeProvider.invoke({
                    input: { query, maxResults: 8 }
                } as any, token);

                // Stream the result - access the content array correctly
                if (result && result.content && Array.isArray(result.content)) {
                    for (const part of result.content) {
                        if (part && typeof part === 'object' && 'value' in part) {
                            stream.markdown((part as any).value);
                        }
                    }
                } else {
                    stream.markdown('No recipes found. Try searching for different ingredients or dish names.');
                }

            } catch (error) {
                console.error('Error in recipe participant:', error);
                stream.markdown(`❌ Error searching for recipes: ${error instanceof Error ? error.message : 'Unknown error'}`);
            }
        });

        participant.iconPath = new vscode.ThemeIcon('home');
        participant.followupProvider = {
            provideFollowups(result, context, token) {
                return [
                    {
                        prompt: 'Show me quick dinner recipes',
                        label: '🍽️ Quick dinners'
                    },
                    {
                        prompt: 'Find vegetarian recipes',
                        label: '🥬 Vegetarian'
                    },
                    {
                        prompt: 'Search for dessert recipes',
                        label: '🍰 Desserts'
                    },
                    {
                        prompt: 'Show me chicken recipes',
                        label: '� Chicken dishes'
                    }
                ];
            }
        };

        context.subscriptions.push(participant);
        console.log('Recipe chat participant registered successfully');

        console.log('Recipe Finder is now active in both chat participant and agent modes');
    } catch (error) {
        console.error('Error activating Recipe Finder participant:', error);
    }
}