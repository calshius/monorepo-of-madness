<script lang="ts">
	const API_BASE = 'http://localhost:8000';

	interface Item {
		id: number;
		name: string;
		description: string;
	}

	let items: Item[] = $state([]);
	let name = $state('');
	let description = $state('');
	let error = $state('');

	async function fetchItems() {
		try {
			const res = await fetch(`${API_BASE}/items`);
			items = await res.json();
			error = '';
		} catch {
			error = 'Failed to load items';
		}
	}

	async function addItem() {
		if (!name.trim()) return;
		try {
			const res = await fetch(`${API_BASE}/items`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ name, description })
			});
			if (res.ok) {
				name = '';
				description = '';
				await fetchItems();
			}
		} catch {
			error = 'Failed to add item';
		}
	}

	fetchItems();
</script>

<main>
	<h1>Items</h1>

	<form onsubmit={(e) => { e.preventDefault(); addItem(); }}>
		<input bind:value={name} placeholder="Name" data-testid="name-input" />
		<input bind:value={description} placeholder="Description" data-testid="desc-input" />
		<button type="submit">Add Item</button>
	</form>

	{#if error}
		<p class="error" role="alert">{error}</p>
	{/if}

	{#if items.length === 0}
		<p data-testid="empty-message">No items yet.</p>
	{:else}
		<ul>
			{#each items as item (item.id)}
				<li data-testid="item">
					<strong>{item.name}</strong>
					{#if item.description} — {item.description}{/if}
				</li>
			{/each}
		</ul>
	{/if}
</main>

<style>
	main {
		max-width: 600px;
		margin: 2rem auto;
		font-family: system-ui, sans-serif;
	}
	form {
		display: flex;
		gap: 0.5rem;
		margin-bottom: 1rem;
	}
	input {
		padding: 0.4rem;
		border: 1px solid #ccc;
		border-radius: 4px;
	}
	button {
		padding: 0.4rem 1rem;
		background: #333;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
	}
	.error {
		color: red;
	}
	ul {
		list-style: none;
		padding: 0;
	}
	li {
		padding: 0.5rem 0;
		border-bottom: 1px solid #eee;
	}
</style>
