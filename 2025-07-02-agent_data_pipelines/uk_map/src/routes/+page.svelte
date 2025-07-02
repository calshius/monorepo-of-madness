<script lang="ts">
  import UfoMapClientOnly from '$lib/UfoMapClientOnly.svelte';
  import sightings from '../data/sighting_geos.json';

  let query = '';
  let filteredSightings = sightings;

  let showTable = false;
  let tableSearch = '';

  let showMap = true;

  function search() {
    const q = query.trim().toLowerCase();
    if (!q) {
      filteredSightings = sightings;
      return;
    }
    filteredSightings = sightings.filter(s =>
      (s.incident && s.incident.toLowerCase().includes(q)) ||
      (s.town && s.town.toLowerCase().includes(q)) ||
      (s.area && s.area.toLowerCase().includes(q)) ||
      (s.date && s.date.toLowerCase().includes(q))
    );
  }

  $: tableFiltered = tableSearch
    ? sightings.filter(s =>
        (s.incident && s.incident.toLowerCase().includes(tableSearch.toLowerCase())) ||
        (s.town && s.town.toLowerCase().includes(tableSearch.toLowerCase())) ||
        (s.area && s.area.toLowerCase().includes(tableSearch.toLowerCase())) ||
        (s.date && s.date.toLowerCase().includes(tableSearch.toLowerCase()))
      )
    : sightings;
</script>

<!-- Centered Show Table Button -->
<div class="mb-6 flex justify-center">
  <button
    class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
    on:click={() => showTable = !showTable}
    aria-expanded={showTable}
  >
    {showTable ? 'Hide' : 'Show'} Sightings Table
  </button>
</div>

{#if showTable}
  <div class="mt-4 bg-white rounded shadow p-4">
    <input
      type="text"
      placeholder="Search all sightings..."
      bind:value={tableSearch}
      class="mb-4 w-full px-3 py-2 border rounded focus:outline-none focus:ring focus:border-blue-300"
    />
    <div class="overflow-x-auto max-h-[60vh] overflow-y-auto">
      <table class="min-w-full border border-gray-200 text-sm">
        <thead class="bg-blue-100 sticky top-0">
          <tr>
            <th class="p-2 border">Date</th>
            <th class="p-2 border">Time</th>
            <th class="p-2 border">Town</th>
            <th class="p-2 border">Area</th>
            <th class="p-2 border">Incident</th>
          </tr>
        </thead>
        <tbody>
          {#each tableFiltered as s}
            <tr class="hover:bg-blue-50">
              <td class="p-2 border">{s.date}</td>
              <td class="p-2 border">{s.time}</td>
              <td class="p-2 border">{s.town}</td>
              <td class="p-2 border">{s.area}</td>
              <td class="p-2 border">{s.incident}</td>
            </tr>
          {/each}
        </tbody>
      </table>
      {#if tableFiltered.length === 0}
        <div class="text-center text-gray-500 py-4">No sightings found.</div>
      {/if}
    </div>
  </div>
{/if}

<h1 class="text-2xl font-bold mb-4">UK UFO Sightings Map</h1>
<input
  type="text"
  placeholder="Search by town, area, date, or incident..."
  bind:value={query}
  on:input={search}
  class="w-full px-3 py-2 border rounded mb-4 focus:outline-none focus:ring focus:border-blue-300"
/>

<!-- Centered Show Map Button -->
<div class="flex justify-center mb-4">
  <button
    class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
    on:click={() => showMap = !showMap}
    aria-expanded={showMap}
  >
    {showMap ? 'Hide' : 'Show'} Map
  </button>
</div>

{#if showMap}
  <UfoMapClientOnly {filteredSightings} />
{/if}

<p class="mt-2 text-gray-600">{filteredSightings.length} sightings shown.</p>