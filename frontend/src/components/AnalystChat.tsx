import React, { useState, useRef, useEffect } from 'react';
import type { QueryResponse, RetrievedContext } from '../types';
import APIService from '../services/api';
import { Send, Loader2, ExternalLink, Clock } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  context?: RetrievedContext[];
  latency?: number;
  timestamp: number;
}

const AnalystChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your Live News Analyst powered by real-time data. Ask me anything about recent news events.',
      timestamp: Date.now(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showContext, setShowContext] = useState<number | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response: QueryResponse = await APIService.query({
        query: userMessage.content,
        user: 'web-user',
        top_k: 5,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        context: response.context,
        latency: response.latency_ms,
        timestamp: response.timestamp * 1000,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your question. Please ensure the backend is running and try again.',
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-3xl rounded-lg p-4 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              <div className="whitespace-pre-wrap">{message.content}</div>
              
              {/* Show latency and context for assistant messages */}
              {message.role === 'assistant' && message.latency && (
                <div className="mt-2 text-xs opacity-75 flex items-center gap-2">
                  <Clock className="w-3 h-3" />
                  <span>Response time: {message.latency.toFixed(0)}ms</span>
                </div>
              )}

              {message.role === 'assistant' && message.context && message.context.length > 0 && (
                <div className="mt-3">
                  <button
                    onClick={() => setShowContext(showContext === index ? null : index)}
                    className="text-xs underline opacity-75 hover:opacity-100"
                  >
                    {showContext === index ? 'Hide' : 'Show'} {message.context.length} source(s)
                  </button>
                  
                  {showContext === index && (
                    <div className="mt-2 space-y-2">
                      {message.context.map((ctx, ctxIndex) => (
                        <div
                          key={ctxIndex}
                          className="bg-white bg-opacity-50 rounded p-2 text-xs"
                        >
                          <p className="text-gray-700 mb-1">{ctx.text.substring(0, 150)}...</p>
                          <div className="flex items-center justify-between text-gray-600">
                            <span>{ctx.source}</span>
                            <a
                              href={ctx.link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-1 hover:underline"
                            >
                              <ExternalLink className="w-3 h-3" />
                              Link
                            </a>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-4 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm text-gray-600">Analyzing news...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-200 p-4 bg-white">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about recent news events..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-blue-600 text-white rounded-lg px-6 py-2 flex items-center gap-2 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
            Send
          </button>
        </form>
        <p className="text-xs text-gray-500 mt-2">
          💡 Try: "What's happening with Tesla?" or "Latest tech news"
        </p>
      </div>
    </div>
  );
};

export default AnalystChat;
