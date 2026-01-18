import { useState, useEffect } from 'react';
import type { NewsArticle, SentimentDataPoint, Alert, SystemStats, WSMessage } from './types';
import APIService from './services/api';
import NewsTicker from './components/NewsTicker';
import AnalystChat from './components/AnalystChat';
import SentimentChart from './components/SentimentChart';
import AlertPanel from './components/AlertPanel';
import { Activity, TrendingUp, FileText, Rss, Sun, Moon, Newspaper, Bot, Zap } from 'lucide-react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState<'ticker' | 'analyst'>('ticker');
  const [articles, setArticles] = useState<NewsArticle[]>([]);
  const [sentimentData, setSentimentData] = useState<SentimentDataPoint[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<SystemStats>({
    total_articles: 0,
    articles_last_hour: 0,
    active_sources: 0,
    avg_latency_ms: 0,
    last_update: Date.now(),
  });
  const [wsConnected, setWsConnected] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('theme');
    return (saved as 'light' | 'dark') || 'light';
  });

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  useEffect(() => {
    // Initial data fetch
    fetchInitialData();

    // WebSocket connection for real-time updates
    APIService.connectWebSocket(
      handleWSMessage,
      (error) => {
        console.error('WebSocket error:', error);
        setWsConnected(false);
      },
      () => {
        setWsConnected(false);
      }
    );

    // Polling fallback (every 5 seconds) in case WebSocket fails
    const pollInterval = setInterval(() => {
      if (!APIService.isWebSocketConnected()) {
        fetchInitialData();
      }
    }, 5000);

    return () => {
      clearInterval(pollInterval);
      APIService.disconnectWebSocket();
    };
  }, []);

  const fetchInitialData = async () => {
    try {
      const [newsData, statsData, sentimentResponse] = await Promise.all([
        APIService.getLatestNews(20),
        APIService.getSystemStats(),
        APIService.getSentimentData(),
      ]);
      setArticles(newsData);
      setStats(statsData);
      
      // Set sentiment data from history
      if (sentimentResponse.history && sentimentResponse.history.length > 0) {
        setSentimentData(sentimentResponse.history.map(s => {
          // Parse timestamp to create window label
          let windowLabel = '';
          try {
            const date = new Date(s.timestamp);
            windowLabel = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
          } catch {
            windowLabel = 'N/A';
          }
          
          return {
            timestamp: Date.now(),
            sentiment_score: s.sentiment_score,
            window_label: windowLabel
          };
        }));
      }
    } catch (error) {
      console.error('Failed to fetch initial data:', error);
    }
  };

  const handleWSMessage = (message: WSMessage) => {
    setWsConnected(true);

    switch (message.type) {
      case 'news':
        const newsArticle = message.data as NewsArticle;
        setArticles((prev) => {
          const updated = [newsArticle, ...prev];
          return updated.slice(0, 50);
        });
        break;

      case 'sentiment':
        const sentimentPoint = message.data as SentimentDataPoint;
        setSentimentData((prev) => {
          const updated = [...prev, sentimentPoint];
          return updated.slice(-30);
        });
        break;

      case 'alert':
        const alert = message.data as Alert;
        setAlerts((prev) => {
          const updated = [alert, ...prev];
          return updated.slice(0, 10);
        });
        break;

      case 'stats':
        setStats(message.data as SystemStats);
        break;

      default:
        console.log('Unknown message type:', message.type);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="header-top">
            <div className="header-brand">
              <div className="header-logo">
                <Zap />
              </div>
              <div>
                <h1 className="header-title">Nexus</h1>
                <p className="header-subtitle">Real-time AI-powered news analysis with Pathway</p>
              </div>
            </div>
            
            <div className="header-controls">
              {/* Theme Toggle */}
              <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
                <div className="theme-toggle-track">
                  <div className="theme-toggle-thumb">
                    {theme === 'light' ? <Sun /> : <Moon />}
                  </div>
                </div>
                <span>{theme === 'light' ? 'Light' : 'Dark'}</span>
              </button>
              
              {/* Status Indicator */}
              <div className="status-indicator">
                <div className={`status-dot ${wsConnected ? 'live' : 'polling'}`}></div>
                <span>{wsConnected ? 'Live' : 'Polling'}</span>
              </div>
            </div>
          </div>

          {/* Stats Bar */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">
                <FileText />
                Total Articles
              </div>
              <div className="stat-value">{stats.total_articles}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">
                <TrendingUp />
                Last Hour
              </div>
              <div className="stat-value">{stats.articles_last_hour}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">
                <Rss />
                Active Sources
              </div>
              <div className="stat-value">{stats.active_sources}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">
                <Activity />
                Avg Latency
              </div>
              <div className="stat-value">{stats.avg_latency_ms.toFixed(0)}ms</div>
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <nav className="tab-nav">
        <div className="tab-nav-content">
          <button
            onClick={() => setActiveTab('ticker')}
            className={`tab-btn ${activeTab === 'ticker' ? 'active' : ''}`}
          >
            <span className="tab-icon"><Newspaper /></span>
            Live News Ticker
          </button>
          <button
            onClick={() => setActiveTab('analyst')}
            className={`tab-btn ${activeTab === 'analyst' ? 'active' : ''}`}
          >
            <span className="tab-icon"><Bot /></span>
            AI Analyst Chat
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {activeTab === 'ticker' ? (
          <div className="content-grid">
            {/* Left: News Ticker */}
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">
                  <Newspaper />
                  Latest Headlines
                </h2>
                <span style={{ fontSize: '0.875rem', color: 'var(--text-tertiary)' }}>
                  {articles.length} articles
                </span>
              </div>
              <div className="card-body no-padding">
                <NewsTicker articles={articles} />
              </div>
            </div>

            {/* Right: Sidebar */}
            <div className="sidebar-stack">
              <SentimentChart data={sentimentData} />
              <AlertPanel alerts={alerts} />
            </div>
          </div>
        ) : (
          <div className="content-full">
            <div className="card chat-container">
              <AnalystChat />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <p className="footer-main">
            🚀 Built with Pathway • Gemini • React • Powered by Differential Dataflow
          </p>
          <p className="footer-sub">
            DataQuest Hackathon 2025 • Real-Time RAG Architecture
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
