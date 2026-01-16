import React, { useEffect, useState } from 'react';
import type { NewsArticle } from '../types';
import { formatDistanceToNow } from 'date-fns';
import { ExternalLink, Clock, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface NewsTickerProps {
  articles: NewsArticle[];
}

const NewsTicker: React.FC<NewsTickerProps> = ({ articles }) => {
  const [displayArticles, setDisplayArticles] = useState<NewsArticle[]>([]);

  useEffect(() => {
    // Sort by timestamp (most recent first)
    const sorted = [...articles].sort((a, b) => b.timestamp - a.timestamp);
    setDisplayArticles(sorted.slice(0, 20)); // Show latest 20
  }, [articles]);

  const getSourceClass = (source: string): string => {
    const classes: Record<string, string> = {
      'BBC': 'bbc',
      'Reuters': 'reuters',
      'TechCrunch': 'techcrunch',
      'HackerNews': 'hackernews',
      'FileWatcher': 'filewatcher',
    };
    return classes[source] || 'default';
  };

  const formatTimestamp = (timestamp: number): string => {
    try {
      return formatDistanceToNow(new Date(timestamp * 1000), { addSuffix: true });
    } catch {
      return 'just now';
    }
  };

  const getSentimentInfo = (score?: number) => {
    if (score === undefined || score === null) {
      return { label: 'Neutral', class: 'neutral', icon: <Minus className="w-3 h-3" /> };
    }
    if (score > 0.1) {
      return { label: `+${score.toFixed(2)}`, class: 'positive', icon: <TrendingUp className="w-3 h-3" /> };
    }
    if (score < -0.1) {
      return { label: score.toFixed(2), class: 'negative', icon: <TrendingDown className="w-3 h-3" /> };
    }
    return { label: score.toFixed(2), class: 'neutral', icon: <Minus className="w-3 h-3" /> };
  };

  return (
    <div className="news-list" style={{ padding: '1rem' }}>
      {displayArticles.length === 0 ? (
        <div className="empty-state">
          <Clock className="empty-state-icon" />
          <p className="empty-state-title">Waiting for live news updates...</p>
          <p className="empty-state-text">The system is monitoring news sources in real-time</p>
        </div>
      ) : (
        displayArticles.map((article, index) => {
          const sentiment = getSentimentInfo(article.sentiment_score);
          return (
            <div
              key={article.id}
              className="news-article"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <div className="news-article-header">
                <span className={`news-source ${getSourceClass(article.source)}`}>
                  {article.source}
                </span>
                <span className="news-time">
                  <Clock />
                  {formatTimestamp(article.timestamp)}
                </span>
              </div>
              
              <h3 className="news-title">
                {article.title}
              </h3>
              
              <p className="news-summary">
                {article.summary}
              </p>
              
              <div className="news-footer">
                <a
                  href={article.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="news-link"
                >
                  Read full article
                  <ExternalLink />
                </a>
                
                <span className={`sentiment-badge ${sentiment.class}`}>
                  {sentiment.icon}
                  {sentiment.label}
                </span>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
};

export default NewsTicker;
