<script lang="ts">
  import type { TravelPlan, Itinerary } from '$lib/types';
  import './styles/plan.css';

  interface Props {
    plan: TravelPlan;
  }

  const { plan } = $props();

  let selectedDay = $state(1);

  const currentItinerary = $derived.by(() => {
    return plan.itinerary.find((i: Itinerary) => i.day === selectedDay);
  });
</script>

<div class="travel-plan">
  <section class="hero is-primary">
    <div class="hero-body">
      <div class="container">
        <h1 class="title">{plan.title}</h1>
        <p class="subtitle">{plan.summary}</p>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="columns">
        <div class="column is-one-quarter">
          <div class="box">
            <h2 class="subtitle is-5">Trip Details</h2>
            <div class="trip-stats">
              <div class="stat-item">
                <span class="stat-label">Duration:</span>
                <span class="stat-value">{plan.itinerary.length} days</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Distance:</span>
                <span class="stat-value">{plan.total_distance_km.toFixed(1)} km</span>
              </div>
              {#if plan.estimated_cost}
                <div class="stat-item">
                  <span class="stat-label">Est. Cost:</span>
                  <span class="stat-value">{plan.estimated_cost}</span>
                </div>
              {/if}
            </div>

            <div class="day-selector">
              <h3 class="subtitle is-6">Select Day</h3>
              <div class="buttons are-small">
                {#each plan.itinerary as itinerary (itinerary.day)}
                  <button
                    class="button"
                    class:is-primary={selectedDay === itinerary.day}
                    onclick={() => (selectedDay = itinerary.day)}
                  >
                    Day {itinerary.day}
                  </button>
                {/each}
              </div>
            </div>
          </div>
        </div>

        <div class="column is-three-quarters">
          {#if currentItinerary}
            <div class="itinerary-content">
              <div class="box">
                <h2 class="title is-4">Day {currentItinerary.day}</h2>
                <p class="content mb-4">{currentItinerary.notes}</p>

                <div class="locations">
                  {#each currentItinerary.locations as location (location.landmark_name)}
                    <div class="card location-card">
                      <div class="card-header">
                        <p class="card-header-title">{location.landmark_name}</p>
                        <span class="tag is-light">{location.category.replace(/_/g, ' ')}</span>
                      </div>

                      <div class="card-content">
                        <div class="content">
                          <p>{location.description}</p>
                          <p class="mt-3"><strong>Best time to visit:</strong> {location.best_time_to_visit}</p>
                          <p><strong>Duration:</strong> {location.estimated_duration}</p>
                        </div>
                      </div>

                      {#if location.photo_links.length > 0}
                        <div class="images-section">
                          <h4 class="subtitle is-6">Images</h4>
                          <div class="image-gallery">
                            {#each location.photo_links as photo (photo.url)}
                              <div class="image-item">
                                <figure class="image is-square">
                                  <img src={photo.url} alt={photo.title || location.landmark_name} />
                                </figure>
                                {#if photo.title}
                                  <p class="is-size-7 mt-2">{photo.title}</p>
                                {/if}
                              </div>
                            {/each}
                          </div>
                        </div>
                      {/if}

                      {#if location.review_links.length > 0}
                        <div class="reviews-section">
                          <h4 class="subtitle is-6">Reviews</h4>
                          <div class="reviews-list">
                            {#each location.review_links as review (review.url)}
                              <div class="review-item">
                                <div class="review-header">
                                  <strong>{review.source}</strong>
                                  {#if review.rating}
                                    <div class="rating">
                                      {#each Array(5) as _, i}
                                        <span class="star" class:filled={i < Math.round(review.rating)}
                                          >★</span
                                        >
                                      {/each}
                                      <span class="rating-value">({review.rating}/5)</span>
                                    </div>
                                  {/if}
                                </div>
                                <a href={review.url} target="_blank" rel="noopener noreferrer" class="is-size-7">
                                  Read full reviews →
                                </a>
                              </div>
                            {/each}
                          </div>
                        </div>
                      {/if}

                      {#if location.hotspots.length > 0}
                        <div class="hotspots-section">
                          <h4 class="subtitle is-6">Highlights</h4>
                          <ul class="hotspots-list">
                            {#each location.hotspots as hotspot (hotspot.name)}
                              <li class="hotspot-item">
                                <strong>{hotspot.name}</strong>
                                <p class="is-size-7">{hotspot.description}</p>
                                <p class="is-size-7 has-text-info">Why visit: {hotspot.why_visit}</p>
                              </li>
                            {/each}
                          </ul>
                        </div>
                      {/if}
                    </div>
                  {/each}
                </div>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </section>
</div>

<style>
  .star {
    color: #ddd;
    font-size: 0.9rem;
  }
  .star.filled {
    color: #ffc107;
  }
  .rating-value {
    margin-left: 0.5rem;
    font-size: 0.85rem;
    color: #666;
  }
</style>
