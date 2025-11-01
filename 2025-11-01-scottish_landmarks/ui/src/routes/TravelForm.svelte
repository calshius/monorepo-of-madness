<script lang="ts">
  import type { TravelPlanRequest, LandmarkCategory } from '$lib/types';
  import './styles/form.css';

  let daysAvailable = $state(3);
  let startLocation = $state('Edinburgh');
  let budget = $state('medium');
  let interests = $state<Record<LandmarkCategory, boolean>>({
    castle: true,
    mountain: false,
    loch: false,
    historic_site: false,
    natural_wonder: false,
    city: false,
    island: false,
  });

  let error = $state<string | null>(null);

  interface Props {
    onSubmit: (request: TravelPlanRequest) => void;
    isLoading?: boolean;
  }

  const { onSubmit, isLoading: loading = false } = $props();

  function handleSubmit() {
    error = null;

    const selectedInterests = Object.entries(interests)
      .filter(([_, selected]) => selected)
      .map(([category]) => category as LandmarkCategory);

    if (selectedInterests.length === 0) {
      error = 'Please select at least one interest';
      return;
    }

    if (daysAvailable < 1 || daysAvailable > 14) {
      error = 'Days available must be between 1 and 14';
      return;
    }

    const request: TravelPlanRequest = {
      days_available: daysAvailable,
      interests: selectedInterests,
      start_location: startLocation,
      budget: budget || undefined,
    };

    onSubmit(request);
  }
</script>

<div class="travel-form">
  <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }}>
    {#if error}
      <div class="notification is-danger">
        <button class="delete" onclick={() => (error = null)} title="Dismiss error"></button>
        {error}
      </div>
    {/if}

    <div class="field">
      <label class="label" for="days">Days Available</label>
      <div class="control">
        <input
          id="days"
          class="input"
          type="number"
          min="1"
          max="14"
          bind:value={daysAvailable}
          disabled={loading}
        />
      </div>
      <p class="help">How many days do you have for your trip? (1-14 days)</p>
    </div>

    <div class="field">
      <label class="label" for="location">Starting Location</label>
      <div class="control">
        <input
          id="location"
          class="input"
          type="text"
          bind:value={startLocation}
          placeholder="e.g., Edinburgh"
          disabled={loading}
        />
      </div>
      <p class="help">Where will you start your journey?</p>
    </div>

    <div class="field">
      <label class="label" for="budget">Budget Level</label>
      <div class="control">
        <div class="select">
          <select id="budget" bind:value={budget} disabled={loading}>
            <option value="budget">Budget</option>
            <option value="medium">Medium</option>
            <option value="luxury">Luxury</option>
          </select>
        </div>
      </div>
    </div>

    <div class="field">
      <fieldset>
        <legend class="label" id="interests-label">Interests</legend>
        <div class="interests-grid" role="group" aria-labelledby="interests-label">
          {#each Object.keys(interests) as category (category)}
            <label class="checkbox">
              <input
                type="checkbox"
                bind:checked={interests[category as LandmarkCategory]}
                disabled={loading}
              />
              {category.replace(/_/g, ' ')}
            </label>
          {/each}
        </div>
      </fieldset>
      <p class="help">Select at least one interest to explore</p>
    </div>

    <div class="field">
      <div class="control">
        <button
          class="button is-primary is-fullwidth"
          type="submit"
          disabled={loading}
        >
          {#if loading}
            <span class="icon">
              <i class="fas fa-spinner fa-spin"></i>
            </span>
            <span>Creating Your Travel Plan...</span>
          {:else}
            <span class="icon">
              <i class="fas fa-map"></i>
            </span>
            <span>Create Travel Plan</span>
          {/if}
        </button>
      </div>
    </div>
  </form>
</div>
