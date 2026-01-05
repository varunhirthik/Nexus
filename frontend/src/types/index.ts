// TypeScript interfaces for Pathway backend data models

export interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  content: string;
  link: string;
  published: string;
  source: string;
  timestamp: number;
}

export interface QueryRequest {
  query: string;
  user?: string;
  top_k?: number;
}

export interface RetrievedContext {
  text: string;
  link: string;
  source: string;
  timestamp: number;
  relevance_score?: number;
}

export interface QueryResponse {
  query: string;
  answer: string;
  context: RetrievedContext[];
  latency_ms: number;
  timestamp: number;
}

export interface Alert {
  id: string;
  keyword: string;
  count: number;
  window: string; // e.g., "last 1 hour"
  timestamp: number;
  articles: string[]; // article links
}

export interface SentimentDataPoint {
  timestamp: number;
  sentiment_score: number; // -1 to 1
  window_label: string; // e.g., "10:30 AM"
}

export interface SystemStats {
  total_articles: number;
  articles_last_hour: number;
  active_sources: number;
  avg_latency_ms: number;
  last_update: number;
}

// WebSocket message types
export interface WSMessage {
  type: 'news' | 'sentiment' | 'alert' | 'stats';
  data: NewsArticle | SentimentDataPoint | Alert | SystemStats;
}
