<script lang="ts">
    let chatMessages = [];
    let currentMessage = '';
    let audioUrl = null;
    let isLoading = false;

    async function sendMessage() {
        if (!currentMessage.trim()) return;

        chatMessages = [...chatMessages, { text: currentMessage, sender: 'user' }];
        const userMessage = currentMessage;
        currentMessage = '';
        isLoading = true;

        try {
            const response = await fetch('http://127.0.0.1:8001/generate_music', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: userMessage })
            });

            if (!response.ok) {
                const errorText = await response.text();
                chatMessages = [...chatMessages, { text: `Error: ${errorText}`, sender: 'system' }];
                return;
            }

            const blob = await response.blob();
            audioUrl = URL.createObjectURL(blob);
            chatMessages = [...chatMessages, { text: 'Playing music...', sender: 'system' }];

        } catch (error) {
            console.error("Error:", error);
            chatMessages = [...chatMessages, { text: `Error: ${error}`, sender: 'system' }];
        } finally {
            isLoading = false;
        }
    }
</script>

<style>
    .chat-container {
        max-width: 600px;
        margin: 20px auto;
    }

    .message {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
    }

    .user {
        background-color: #e0f7fa;
        text-align: right;
    }

    .system {
        background-color: #f0f0f0;
        text-align: left;
    }

    .input-area {
        margin-top: 10px;
    }
</style>

<section class="section">
    <div class="container chat-container">
        <h1 class="title">Orchestra Chat</h1>

        <div class="messages">
            {#each chatMessages as message}
                <div class="message" class:user={message.sender === 'user'} class:system={message.sender === 'system'}>
                    {message.text}
                </div>
            {/each}
        </div>

        {#if audioUrl}
            <div class="box">
                <audio controls src={audioUrl}></audio>
            </div>
        {/if}

        <div class="input-area">
            <div class="field has-addons">
                <div class="control is-expanded">
                    <input class="input" type="text" placeholder="Enter your request" bind:value={currentMessage} on:keydown={(e) => e.key === 'Enter' ? sendMessage() : null}>
                </div>
                <div class="control">
                    <button class="button is-info" on:click={sendMessage} disabled={isLoading}>
                        {#if isLoading}
                            <span class="icon is-small">
                                <i class="fas fa-spinner fa-spin"></i>
                            </span>
                            <span>Loading</span>
                        {:else}
                            <span>Send</span>
                        {/if}
                    </button>
                </div>
            </div>
        </div>
    </div>
</section>

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" integrity="sha512-9usAa10IRO0HhonpyAIVpjrylPvoDwiPUiKdWk5t3PyolY1cOd4DSE0Ga+ri4AuTroPR5aQvXU9xC6qOPnzFeg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
