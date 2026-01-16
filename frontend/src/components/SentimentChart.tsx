import React from 'react';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, Area, AreaChart, Line } from 'recharts';
import type { SentimentDataPoint } from '../types';
import { TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';

interface SentimentChartProps {
  data: SentimentDataPoint[];
}

const SentimentChart: React.FC<SentimentChartProps> = ({ data }) => {
  const currentSentiment = data.length > 0 ? data[data.length - 1].sentiment_score : 0;

  const getSentimentLabel = (score: number): { label: string; className: string; icon: React.ReactElement } => {
    if (score > 0.2) return { label: 'Positive', className: 'positive', icon: <TrendingUp className="w-5 h-5" /> };
    if (score < -0.2) return { label: 'Negative', className: 'negative', icon: <TrendingDown className="w-5 h-5" /> };
    return { label: 'Neutral', className: 'neutral', icon: <Minus className="w-5 h-5" /> };
  };

  const sentiment = getSentimentLabel(currentSentiment);

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const value = payload[0].value;
      return (
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-md)',
          padding: '0.75rem 1rem',
          boxShadow: 'var(--shadow-lg)',
        }}>
          <p style={{ color: 'var(--text-tertiary)', fontSize: '0.75rem', marginBottom: '0.25rem' }}>
            {label}
          </p>
          <p style={{ 
            color: value > 0.2 ? 'var(--success)' : value < -0.2 ? 'var(--error)' : 'var(--text-secondary)',
            fontWeight: 600,
            fontSize: '0.875rem'
          }}>
            Sentiment: {value?.toFixed(3) || 'N/A'}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card sentiment-panel">
      <div className="card-header">
        <h3 className="card-title">
          <Activity />
          Market Sentiment
        </h3>
        <div className={`sentiment-current ${sentiment.className}`}>
          {sentiment.icon}
          <span>{sentiment.label}</span>
          <span style={{ fontSize: '0.75rem', opacity: 0.8 }}>({currentSentiment.toFixed(2)})</span>
        </div>
      </div>

      <div className="card-body">
        {data.length === 0 ? (
          <div className="empty-state" style={{ padding: '2rem 1rem' }}>
            <Activity className="empty-state-icon" style={{ width: '48px', height: '48px' }} />
            <p className="empty-state-title">Collecting sentiment data...</p>
            <p className="empty-state-text">Real-time sentiment will appear here</p>
          </div>
        ) : (
          <>
            <div className="sentiment-chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                  <defs>
                    <linearGradient id="sentimentGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--accent-primary)" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="var(--accent-primary)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                  <XAxis 
                    dataKey="window_label" 
                    tick={{ fontSize: 11, fill: 'var(--text-tertiary)' }}
                    axisLine={{ stroke: 'var(--border-color)' }}
                    tickLine={{ stroke: 'var(--border-color)' }}
                    interval="preserveStartEnd"
                  />
                  <YAxis 
                    domain={[-1, 1]}
                    ticks={[-1, -0.5, 0, 0.5, 1]}
                    tick={{ fontSize: 11, fill: 'var(--text-tertiary)' }}
                    axisLine={{ stroke: 'var(--border-color)' }}
                    tickLine={{ stroke: 'var(--border-color)' }}
                    width={35}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <ReferenceLine y={0} stroke="var(--text-tertiary)" strokeDasharray="3 3" />
                  <Area 
                    type="monotone" 
                    dataKey="sentiment_score" 
                    stroke="var(--accent-primary)" 
                    strokeWidth={2}
                    fill="url(#sentimentGradient)"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="sentiment_score" 
                    stroke="var(--accent-primary)" 
                    strokeWidth={2}
                    dot={{ fill: 'var(--accent-primary)', r: 4, strokeWidth: 0 }}
                    activeDot={{ r: 6, stroke: 'var(--bg-card)', strokeWidth: 2 }}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="sentiment-legend">
              <span>📈 +1 Very Positive</span>
              <span>📊 0 Neutral</span>
              <span>📉 -1 Very Negative</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default SentimentChart;
