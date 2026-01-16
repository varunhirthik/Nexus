import React from 'react';
import type { Alert } from '../types';
import { AlertTriangle, ExternalLink, Bell } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface AlertPanelProps {
  alerts: Alert[];
}

const AlertPanel: React.FC<AlertPanelProps> = ({ alerts }) => {
  const formatTimestamp = (timestamp: number): string => {
    try {
      return formatDistanceToNow(new Date(timestamp * 1000), { addSuffix: true });
    } catch {
      return 'just now';
    }
  };

  return (
    <div className="card alerts-panel">
      <div className="card-header">
        <h3 className="card-title">
          <Bell />
          Keyword Alerts
        </h3>
        {alerts.length > 0 && (
          <span className="sentiment-badge positive">
            {alerts.length} active
          </span>
        )}
      </div>

      <div className="card-body">
        {alerts.length === 0 ? (
          <div className="empty-state" style={{ padding: '2rem 1rem' }}>
            <AlertTriangle className="empty-state-icon" style={{ width: '48px', height: '48px' }} />
            <p className="empty-state-title">No alerts triggered</p>
            <p className="empty-state-text">System monitors for trending keywords in real-time</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {alerts.map((alert, index) => (
              <div
                key={alert.id}
                className="alert-item"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="alert-header">
                  <div>
                    <p className="alert-keyword">
                      "{alert.keyword}" mentioned <strong>{alert.count}x</strong> in {alert.window}
                    </p>
                  </div>
                  <span className="alert-time">
                    {formatTimestamp(alert.timestamp)}
                  </span>
                </div>
                
                {alert.articles.length > 0 && (
                  <div className="alert-articles">
                    <p className="alert-articles-title">Related articles:</p>
                    {alert.articles.slice(0, 3).map((link, idx) => (
                      <a
                        key={idx}
                        href={link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="alert-article-link"
                      >
                        <ExternalLink className="w-3 h-3" />
                        {link.length > 40 ? `${link.substring(0, 40)}...` : link}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="alerts-footer">
          📊 Monitored: Tesla, Bitcoin, Fed, Inflation, Crash, Merger
        </div>
      </div>
    </div>
  );
};

export default AlertPanel;
