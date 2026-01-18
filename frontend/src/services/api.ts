// API Service for communicating with Pathway backend

import axios from 'axios';
import type { QueryRequest, QueryResponse, NewsArticle, WSMessage, SystemStats } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Derive WebSocket URL from API URL (https -> wss, http -> ws)
const getWsUrl = () => {
  const wsEnv = import.meta.env.VITE_WS_URL;
  if (wsEnv) return wsEnv;
  
  // Derive from API URL
  if (API_BASE_URL.startsWith('https://')) {
    return API_BASE_URL.replace('https://', 'wss://');
  } else if (API_BASE_URL.startsWith('http://')) {
    return API_BASE_URL.replace('http://', 'ws://');
  }
  return 'ws://localhost:8000';
};

const WS_BASE_URL = getWsUrl();

class APIService {
  private ws: WebSocket | null = null;
  private wsReconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  // REST API Methods
  async query(request: QueryRequest): Promise<QueryResponse> {
    try {
      const response = await axios.post(`${API_BASE_URL}/query`, request, {
        headers: { 'Content-Type': 'application/json' },
        timeout: 30000, // 30 second timeout
      });
      return response.data;
    } catch (error) {
      console.error('Query error:', error);
      throw new Error('Failed to query the news analyst. Please try again.');
    }
  }

  async getLatestNews(limit: number = 20): Promise<NewsArticle[]> {
    try {
      const response = await axios.get(`${API_BASE_URL}/news/latest`, {
        params: { limit },
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch latest news:', error);
      return [];
    }
  }

  async getSystemStats(): Promise<SystemStats> {
    try {
      const response = await axios.get(`${API_BASE_URL}/stats`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch system stats:', error);
      return {
        total_articles: 0,
        articles_last_hour: 0,
        active_sources: 0,
        avg_latency_ms: 0,
        last_update: Date.now(),
      };
    }
  }

  async getSentimentData(): Promise<{ current: { sentiment_score: number }; history: Array<{ timestamp: string; sentiment_score: number; title: string; source: string }> }> {
    try {
      const response = await axios.get(`${API_BASE_URL}/sentiment`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch sentiment data:', error);
      return {
        current: { sentiment_score: 0 },
        history: []
      };
    }
  }

  // WebSocket Methods
  connectWebSocket(
    onMessage: (message: WSMessage) => void,
    onError?: (error: Event) => void,
    onClose?: () => void
  ): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    try {
      this.ws = new WebSocket(`${WS_BASE_URL}/ws`);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.wsReconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);
          onMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (onError) onError(error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket closed');
        if (onClose) onClose();
        
        // Attempt reconnection
        if (this.wsReconnectAttempts < this.maxReconnectAttempts) {
          this.wsReconnectAttempts++;
          console.log(`Reconnecting... Attempt ${this.wsReconnectAttempts}`);
          setTimeout(() => {
            this.connectWebSocket(onMessage, onError, onClose);
          }, 2000 * this.wsReconnectAttempts); // Exponential backoff
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }

  disconnectWebSocket(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isWebSocketConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

export default new APIService();
