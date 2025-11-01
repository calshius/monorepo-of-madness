<script lang="ts">
  import { TravelPlannerAPI } from '$lib/api';
  import type { TravelPlanRequest, TravelPlan, WebSocketMessage } from '$lib/types';
  import TravelForm from './TravelForm.svelte';
  import TravelPlanDisplay from './TravelPlan.svelte';

  let travelPlan = $state<TravelPlan | null>(null);
  let isLoading = $state(false);
  let progress = $state(0);
  let statusMessage = $state('');
  let error = $state<string | null>(null);
  let wsConnection: ReturnType<typeof TravelPlannerAPI.streamTravelPlan> | null = null;

  function handleFormSubmit(request: TravelPlanRequest) {
    isLoading = true;
    error = null;
    progress = 0;
    statusMessage = 'Connecting to travel planner...';
    travelPlan = null;

    wsConnection = TravelPlannerAPI.streamTravelPlan(
      request,
      (message: WebSocketMessage) => {
        if (message.type === 'status') {
          statusMessage = message.message || 'Processing...';
        } else if (message.type === 'step') {
          statusMessage = `${message.step?.replace(/_/g, ' ')}...`;
          progress = Math.round((message.progress || 0) * 100);
        } else if (message.type === 'result') {
          travelPlan = message.data || null;
          statusMessage = 'Travel plan ready!';
          progress = 100;
          isLoading = false;
        } else if (message.type === 'error') {
          error = message.message || 'An error occurred while generating your travel plan';
          isLoading = false;
        }
      },
      (err: string) => {
        error = err;
        isLoading = false;
      },
      () => {
        if (!travelPlan) {
          error = 'Connection closed unexpectedly';
          isLoading = false;
        }
      }
    );
  }

  function handleReset() {
    travelPlan = null;
    isLoading = false;
    progress = 0;
    statusMessage = '';
    error = null;
    if (wsConnection) {
      wsConnection.close();
    }
  }
</script>

{#if travelPlan}
  <section class="section">
    <div class="container">
      <div class="mb-4">
        <button class="button is-light" onclick={handleReset}> ← Create Another Plan </button>
      </div>
      <TravelPlanDisplay plan={travelPlan} />
    </div>
  </section>
{:else}
  <section class="hero is-primary">
    <div class="hero-body">
      <div class="container">
        <h1 class="title">Scottish Landmarks Travel Planner</h1>
        <p class="subtitle">Discover Scotland's most beautiful landmarks with AI-powered planning</p>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="columns is-centered">
        <div class="column is-half">
          <TravelForm {isLoading} onSubmit={handleFormSubmit} />

          {#if isLoading}
            <div class="mt-4">
              <progress class="progress is-primary" value={progress} max="100"></progress>
              <p class="has-text-centered mt-2">
                <span class="icon">
                  <i class="fas fa-spinner fa-spin"></i>
                </span>
                <span>{statusMessage}</span>
              </p>
            </div>
          {/if}

          {#if error}
            <div class="notification is-danger mt-4">
              <button class="delete" onclick={() => (error = null)} title="Dismiss error"></button>
              <strong>Error:</strong> {error}
            </div>
          {/if}
        </div>
      </div>
    </div>
  </section>
{/if}

<style>
  .mt-4 {
    margin-top: 1.5rem;
  }

  .mt-2 {
    margin-top: 0.5rem;
  }
</style>

