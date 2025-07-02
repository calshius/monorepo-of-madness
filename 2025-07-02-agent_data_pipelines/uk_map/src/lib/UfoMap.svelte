<script lang="ts">
  import { browser } from "$app/environment";
  import { LeafletMap, TileLayer, Marker, Popup } from "svelte-leafletjs";
  import { type MapOptions } from "leaflet";
  export let filteredSightings = [];

  const ukCenter = [54.5, -3.5];
  const zoom = 6;

  const mapOptions: MapOptions = {
    center: ukCenter,
    zoom,
  };

  const tileUrl = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  const tileOptions = {
    attribution: "&copy; OpenStreetMap contributors",
  };
</script>

{#if browser}
  <div class="map-container">
    <LeafletMap options={mapOptions} style="height: 80vh; width: 100%;">
      <TileLayer url={tileUrl} options={tileOptions} />
      {#each filteredSightings as s}
        {#if s.coordinates && s.coordinates[0] !== "NA" && s.coordinates[1] !== "NA"}
          <Marker
            latLng={[
              parseFloat(s.coordinates[0]),
              parseFloat(s.coordinates[1]),
            ]}
          >
            <Popup>
              <b>{s.town || s.area}</b><br />
              <small>{s.date} {s.time}</small><br />
              {s.incident}
            </Popup>
          </Marker>
        {/if}
      {/each}
    </LeafletMap>
  </div>
{/if}

<style>
  .map-container {
    background: #b3c6e7 !important;
    min-height: 80vh !important;
    height: 80vh !important;
  }
</style>
