<script lang="ts">
  import { onMount } from 'svelte';
  export let filteredSightings = [];

  let UfoMap;
  let mounted = false;

  onMount(async () => {
    const mod = await import('./UfoMap.svelte');
    UfoMap = mod.default;
    mounted = true;
  });
</script>

{#if mounted && UfoMap}
  <svelte:component this={UfoMap} {filteredSightings} />
{/if}