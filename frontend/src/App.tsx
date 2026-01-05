import { useState, useEffect } from 'react';
import type { NewsArticle, SentimentDataPoint, Alert, SystemStats, WSMessage } from './types';
import APIService from './services/api';
import NewsTicker from './components/NewsTicker';
import AnalystChat from './components/AnalystChat';
import SentimentChart from './components/SentimentChart';
import AlertPanel from './components/AlertPanel';
import { Activity, TrendingUp, FileText, Users } from 'lucide-react';

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
      const [newsData, statsData] = await Promise.all([
        APIService.getLatestNews(20),
        APIService.getSystemStats(),
      ]);
      setArticles(newsData);
      setStats(statsData);
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
          // Add new article and keep only latest 50
          const updated = [newsArticle, ...prev];
          return updated.slice(0, 50);
        });
        break;

      case 'sentiment':
        const sentimentPoint = message.data as SentimentDataPoint;
        setSentimentData((prev) => {
          const updated = [...prev, sentimentPoint];
          // Keep last 30 data points (5 minutes if updated every 10 seconds)
          return updated.slice(-30);
        });
        break;

      case 'alert':
        const alert = message.data as Alert;
        setAlerts((prev) => {
          // Add new alert and keep latest 10
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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-3">
                <Activity className="w-8 h-8" />
                Live News Analyst
              </h1>
              <p className="text-blue-100 mt-1">Real-time AI-powered news analysis with Pathway</p>
            </div>
            <div className="flex items-center gap-6">
              <div className="text-right">
                <div className="text-sm text-blue-100">System Status</div>
                <div className={`flex items-center gap-2 ${wsConnected ? 'text-green-300' : 'text-yellow-300'}`}>
                  <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-300 animate-pulse' : 'bg-yellow-300'}`}></div>
                  <span className="font-semibold">{wsConnected ? 'Live' : 'Polling'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Stats Bar */}
          <div className="grid grid-cols-4 gap-4 mt-6">
            <div className="bg-white bg-opacity-10 rounded-lg p-3">
              <div className="flex items-center gap-2 text-blue-100 text-sm mb-1">
                <FileText className="w-4 h-4" />
                Total Articles
              </div>
              <div className="text-2xl font-bold">{stats.total_articles}</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-3">
              <div className="flex items-center gap-2 text-blue-100 text-sm mb-1">
                <TrendingUp className="w-4 h-4" />
                Last Hour
              </div>
              <div className="text-2xl font-bold">{stats.articles_last_hour}</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-3">
              <div className="flex items-center gap-2 text-blue-100 text-sm mb-1">
                <Users className="w-4 h-4" />
                Active Sources
              </div>
              <div className="text-2xl font-bold">{stats.active_sources}</div>
            </div>
            <div className="bg-white bg-opacity-10 rounded-lg p-3">
              <div className="flex items-center gap-2 text-blue-100 text-sm mb-1">
                <Activity className="w-4 h-4" />
                Avg Latency
              </div>
              <div className="text-2xl font-bold">{stats.avg_latency_ms.toFixed(0)}ms</div>
            </div>
          </div>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4">
          <div className="flex gap-8">
            <button
              onClick={() => setActiveTab('ticker')}
              className={`py-4 px-2 border-b-2 font-medium transition-colors ${
                activeTab === 'ticker'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              📰 Live News Ticker
            </button>
            <button
              onClick={() => setActiveTab('analyst')}
              className={`py-4 px-2 border-b-2 font-medium transition-colors ${
                activeTab === 'analyst'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              🤖 AI Analyst Chat
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {activeTab === 'ticker' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left: News Ticker (2/3 width) */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Latest Headlines</h2>
                <NewsTicker articles={articles} />
              </div>
            </div>

            {/* Right: Sentiment & Alerts (1/3 width) */}
            <div className="space-y-6">
              <SentimentChart data={sentimentData} />
              <AlertPanel alerts={alerts} />
            </div>
          </div>
        ) : (
          <div className="max-w-5xl mx-auto">
            <div className="bg-white rounded-lg border border-gray-200 shadow-sm" style={{ height: 'calc(100vh - 300px)' }}>
              <AnalystChat />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-300 mt-12 py-6">
        <div className="container mx-auto px-4 text-center">
          <p>🚀 Built with Pathway • Gemini • React • Powered by Differential Dataflow</p>
          <p className="text-sm mt-2 text-gray-400">DataQuest Hackathon 2025 • Real-Time RAG Architecture</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
