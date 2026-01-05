import React from 'react';
import type { Alert } from '../types';
import { AlertTriangle, ExternalLink } from 'lucide-react';
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
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle className="w-5 h-5 text-yellow-600" />
        <h3 className="text-lg font-semibold text-gray-900">Keyword Alerts</h3>
      </div>

      {alerts.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No alerts triggered yet</p>
          <p className="text-sm mt-2">System monitors for trending keywords in real-time</p>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className="border-l-4 border-yellow-500 bg-yellow-50 p-4 rounded-r-lg"
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <p className="font-semibold text-gray-900">
                    "{alert.keyword}" mentioned {alert.count}x in {alert.window}
                  </p>
                  <p className="text-xs text-gray-600 mt-1">
                    {formatTimestamp(alert.timestamp)}
                  </p>
                </div>
              </div>
              
              {alert.articles.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs text-gray-600 mb-2">Related articles:</p>
                  <ul className="space-y-1">
                    {alert.articles.slice(0, 3).map((link, idx) => (
                      <li key={idx}>
                        <a
                          href={link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 text-xs flex items-center gap-1"
                        >
                          <ExternalLink className="w-3 h-3" />
                          {link.substring(0, 50)}...
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="mt-4 text-xs text-gray-500">
        <p>📊 Monitored keywords: Tesla, Bitcoin, Fed, Inflation, Crash, Merger</p>
      </div>
    </div>
  );
};

export default AlertPanel;
