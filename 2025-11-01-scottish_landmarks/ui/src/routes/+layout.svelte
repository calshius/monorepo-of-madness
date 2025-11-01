<script lang="ts">
	import favicon from '$lib/assets/favicon.svg';
	import '../app.css';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<title>Scottish Landmarks Travel Planner</title>
	<meta name="description" content="Plan your Scottish adventure with AI-powered travel recommendations" />
</svelte:head>

<main>
	{@render children()}
</main>
