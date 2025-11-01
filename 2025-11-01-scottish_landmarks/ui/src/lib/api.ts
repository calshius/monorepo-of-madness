import type { TravelPlanRequest, WebSocketMessage, TravelPlan } from './types';

const API_BASE_URL = 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000';

export class TravelPlannerAPI {
  /**
   * Get all available Scottish landmarks
   */
  static async getLandmarks(): Promise<string[]> {
    const response = await fetch(`${API_BASE_URL}/api/travel/landmarks`);
    if (!response.ok) throw new Error('Failed to fetch landmarks');
    const data = await response.json();
    return data.landmarks;
  }

  /**
   * Get workflow configuration
   */
  static async getWorkflow() {
    const response = await fetch(`${API_BASE_URL}/api/travel/workflow`);
    if (!response.ok) throw new Error('Failed to fetch workflow');
    return response.json();
  }

  /**
   * Create a travel plan via REST API (non-streaming)
   */
  static async createTravelPlan(request: TravelPlanRequest): Promise<TravelPlan> {
    const response = await fetch(`${API_BASE_URL}/api/travel/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });
    if (!response.ok) throw new Error('Failed to create travel plan');
    return response.json();
  }

  /**
   * Stream travel plan generation via WebSocket
   * Returns an async generator that yields WebSocket messages
   */
  static streamTravelPlan(
    request: TravelPlanRequest,
    onMessage: (message: WebSocketMessage) => void,
    onError: (error: string) => void,
    onClose: () => void
  ): { close: () => void } {
    const ws = new WebSocket(`${WS_BASE_URL}/ws/travel-plan`);

    ws.onopen = () => {
      ws.send(JSON.stringify(request));
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        onMessage(message);
      } catch (e) {
        onError(`Failed to parse message: ${e}`);
      }
    };

    ws.onerror = () => {
      onError('WebSocket connection error');
    };

    ws.onclose = () => {
      onClose();
    };

    return {
      close: () => ws.close(),
    };
  }

  /**
   * Health check
   */
  static async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}
