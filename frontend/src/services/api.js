/**
 * Centralized API service for all backend communication.
 * Provides error handling, request/response interceptors, and type safety.
 */

// Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Error classes
class APIError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

class NetworkError extends Error {
  constructor(message) {
    super(message);
    this.name = 'NetworkError';
  }
}

// Core API client
class APIClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      
      // Handle response
      let data;
      try {
        data = await response.json();
      } catch (e) {
        data = null;
      }

      if (!response.ok) {
        throw new APIError(
          data?.error || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          data
        );
      }

      return data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new NetworkError(`Network request failed: ${error.message}`);
    }
  }

  get(endpoint, params = {}) {
    const searchParams = new URLSearchParams(params);
    const query = searchParams.toString();
    const url = query ? `${endpoint}?${query}` : endpoint;
    
    return this.request(url, {
      method: 'GET',
    });
  }

  post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: data,
    });
  }

  put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: data,
    });
  }

  delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  }
}

// Create singleton instance
const apiClient = new APIClient();

// Game State API
export const GameStateAPI = {
  async getSystem() {
    return apiClient.get('/system');
  },

  async getGameState() {
    return apiClient.get('/game_state');
  },

  async getPlayerUnits(playerId) {
    return apiClient.get(`/player_units/${playerId}`);
  },

  async getUnit(unitId, unitName) {
    const params = {};
    if (unitId) params.unit_id = unitId;
    if (unitName) params.unit_name = unitName;
    return apiClient.get('/unit', params);
  },

  async getCurrentTime() {
    return apiClient.get('/current_time');
  },

  async healthCheck() {
    return apiClient.get('/health');
  },
};

// Movement API
export const MovementAPI = {
  async moveUnit(unitId, direction = null, spaceId = null) {
    const data = { unit_id: unitId };
    if (direction !== null) data.direction = direction;
    if (spaceId) data.space_id = spaceId;
    
    return apiClient.post('/move_unit', data);
  },

  async getMovementOptions(unitId) {
    return apiClient.get('/movement_options', { unit_id: unitId });
  },
};

// Collection API
export const CollectionAPI = {
  async collectResource(unitId, resourceId, quantity = null, spaceId = null, structureId = null) {
    const data = {
      unit_id: unitId,
      resource_id: resourceId,
    };
    
    if (quantity !== null) data.quantity = quantity;
    if (spaceId) data.space_id = spaceId;
    if (structureId) data.structure_id = structureId;
    
    return apiClient.post('/collect_item', data);
  },
};

// Building API
export const BuildingAPI = {
  async buildStructure(unitId, structureType) {
    return apiClient.post('/build_structure', {
      unit_id: unitId,
      structure_type: structureType,
    });
  },

  async getBuildingRequirements(structureType) {
    return apiClient.get(`/building_requirements/${structureType}`);
  },

  async canAffordStructure(unitId, structureType) {
    return apiClient.get(`/can_afford/${unitId}/${structureType}`);
  },
};

// Time API
export const TimeAPI = {
  async advanceTime() {
    return apiClient.post('/advance_time');
  },

  async getCurrentTime() {
    return apiClient.get('/current_time');
  },
};

// Utility functions for common patterns
export const APIUtils = {
  // Handle API errors with user-friendly messages
  handleError(error, defaultMessage = 'An unexpected error occurred') {
    console.error('API Error:', error);
    
    if (error instanceof NetworkError) {
      return 'Network connection failed. Please check your internet connection.';
    }
    
    if (error instanceof APIError) {
      return error.message || defaultMessage;
    }
    
    return defaultMessage;
  },

  // Retry mechanism for failed requests
  async retry(apiCall, maxRetries = 3, delay = 1000) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await apiCall();
      } catch (error) {
        if (attempt === maxRetries || error instanceof APIError) {
          throw error;
        }
        
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, delay * attempt));
      }
    }
  },

  // Batch multiple API calls
  async batch(apiCalls) {
    try {
      return await Promise.all(apiCalls);
    } catch (error) {
      // If any call fails, return partial results with error info
      const results = await Promise.allSettled(apiCalls);
      return results.map(result => 
        result.status === 'fulfilled' 
          ? result.value 
          : { error: result.reason }
      );
    }
  },
};

// Export error classes for component use
export { APIError, NetworkError };

// Default export for convenience
export default {
  GameStateAPI,
  MovementAPI,
  CollectionAPI,
  BuildingAPI,
  TimeAPI,
  APIUtils,
};