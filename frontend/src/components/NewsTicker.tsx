import React, { useEffect, useState } from 'react';
import type { NewsArticle } from '../types';
import { formatDistanceToNow } from 'date-fns';
import { ExternalLink, Clock } from 'lucide-react';

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

  const getSourceColor = (source: string): string => {
    const colors: Record<string, string> = {
      'BBC': 'bg-red-100 text-red-800',
      'Reuters': 'bg-blue-100 text-blue-800',
      'TechCrunch': 'bg-green-100 text-green-800',
      'HackerNews': 'bg-orange-100 text-orange-800',
      'FileWatcher': 'bg-purple-100 text-purple-800',
    };
    return colors[source] || 'bg-gray-100 text-gray-800';
  };

  const formatTimestamp = (timestamp: number): string => {
    try {
      return formatDistanceToNow(new Date(timestamp * 1000), { addSuffix: true });
    } catch {
      return 'just now';
    }
  };

  return (
    <div className="space-y-3">
      {displayArticles.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <Clock className="w-12 h-12 mx-auto mb-4 animate-pulse" />
          <p>Waiting for live news updates...</p>
          <p className="text-sm mt-2">The system is monitoring RSS feeds in real-time</p>
        </div>
      ) : (
        displayArticles.map((article) => (
          <div
            key={article.id}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow bg-white"
          >
            <div className="flex items-start justify-between mb-2">
              <span className={`text-xs px-2 py-1 rounded-full font-semibold ${getSourceColor(article.source)}`}>
                {article.source}
              </span>
              <span className="text-xs text-gray-500 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatTimestamp(article.timestamp)}
              </span>
            </div>
            
            <h3 className="font-semibold text-gray-900 mb-2 text-lg">
              {article.title}
            </h3>
            
            <p className="text-gray-600 text-sm mb-3 line-clamp-2">
              {article.summary}
            </p>
            
            <a
              href={article.link}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1 font-medium"
            >
              Read full article
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        ))
      )}
    </div>
  );
};

export default NewsTicker;
