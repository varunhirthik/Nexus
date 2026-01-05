import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import type { SentimentDataPoint } from '../types';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface SentimentChartProps {
  data: SentimentDataPoint[];
}

const SentimentChart: React.FC<SentimentChartProps> = ({ data }) => {
  const currentSentiment = data.length > 0 ? data[data.length - 1].sentiment_score : 0;

  const getSentimentLabel = (score: number): { label: string; color: string; icon: React.ReactElement } => {
    if (score > 0.2) return { label: 'Positive', color: 'text-green-600', icon: <TrendingUp className="w-5 h-5" /> };
    if (score < -0.2) return { label: 'Negative', color: 'text-red-600', icon: <TrendingDown className="w-5 h-5" /> };
    return { label: 'Neutral', color: 'text-gray-600', icon: <Minus className="w-5 h-5" /> };
  };

  const sentiment = getSentimentLabel(currentSentiment);

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Market Sentiment (10-min rolling)</h3>
        <div className={`flex items-center gap-2 ${sentiment.color} font-semibold`}>
          {sentiment.icon}
          <span>{sentiment.label}</span>
          <span className="text-sm">({currentSentiment.toFixed(2)})</span>
        </div>
      </div>

      {data.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-gray-500">
          <p>Collecting sentiment data...</p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="window_label" 
              tick={{ fontSize: 12 }}
              interval="preserveStartEnd"
            />
            <YAxis 
              domain={[-1, 1]}
              ticks={[-1, -0.5, 0, 0.5, 1]}
              tick={{ fontSize: 12 }}
            />
            <Tooltip 
              formatter={(value: any) => value !== undefined && value !== null ? [Number(value).toFixed(3), 'Sentiment'] : ['N/A', 'Sentiment']}
              labelFormatter={(label: any) => `Time: ${label}`}
            />
            <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
            <Line 
              type="monotone" 
              dataKey="sentiment_score" 
              stroke="#3b82f6" 
              strokeWidth={2}
              dot={{ fill: '#3b82f6', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}

      <div className="mt-4 text-xs text-gray-500 text-center">
        <p>Sentiment calculated from news headlines using keyword analysis</p>
        <p>Range: -1 (Very Negative) to +1 (Very Positive)</p>
      </div>
    </div>
  );
};

export default SentimentChart;
