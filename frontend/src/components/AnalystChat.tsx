import React, { useState, useRef, useEffect } from 'react';
import type { QueryResponse, RetrievedContext } from '../types';
import APIService from '../services/api';
import { Send, Loader2, ExternalLink, Clock, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';

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
      content: 'Hello! I\'m your AI News Analyst powered by real-time data from Pathway. Ask me anything about recent news events, market trends, or current headlines.',
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

  const suggestedQuestions = [
    "What's happening with Tesla?",
    "Latest tech news",
    "Bitcoin price updates",
    "Market crash news"
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Messages Area */}
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`chat-message ${message.role}`}
          >
            <div className="chat-bubble">
              {message.role === 'assistant' && (
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: '0.5rem', 
                  marginBottom: '0.75rem',
                  paddingBottom: '0.75rem',
                  borderBottom: '1px solid var(--border-color)'
                }}>
                  <Sparkles style={{ width: '16px', height: '16px', color: 'var(--accent-primary)' }} />
                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--accent-primary)' }}>
                    AI Analyst
                  </span>
                </div>
              )}
              
              <div className="chat-content">{message.content}</div>
              
              {/* Show latency and context for assistant messages */}
              {message.role === 'assistant' && message.latency && (
                <div className="chat-meta">
                  <Clock style={{ width: '12px', height: '12px' }} />
                  <span>Response time: {message.latency.toFixed(0)}ms</span>
                </div>
              )}

              {message.role === 'assistant' && message.context && message.context.length > 0 && (
                <div style={{ marginTop: '0.75rem' }}>
                  <button
                    onClick={() => setShowContext(showContext === index ? null : index)}
                    className="chat-sources-toggle"
                    style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '0.375rem',
                      background: 'none',
                      border: 'none',
                      padding: 0,
                      cursor: 'pointer',
                      color: 'var(--accent-primary)'
                    }}
                  >
                    {showContext === index ? <ChevronUp style={{ width: '14px', height: '14px' }} /> : <ChevronDown style={{ width: '14px', height: '14px' }} />}
                    {showContext === index ? 'Hide' : 'Show'} {message.context.length} source(s)
                  </button>
                  
                  {showContext === index && (
                    <div className="chat-sources">
                      {message.context.map((ctx, ctxIndex) => (
                        <div
                          key={ctxIndex}
                          className="chat-source-item"
                          style={{ 
                            background: 'var(--bg-primary)',
                            padding: '0.75rem',
                            borderRadius: 'var(--radius-md)',
                            marginBottom: ctxIndex < message.context!.length - 1 ? '0.5rem' : 0
                          }}
                        >
                          <p style={{ 
                            color: 'var(--text-secondary)', 
                            marginBottom: '0.5rem',
                            lineHeight: 1.5
                          }}>
                            {ctx.text.substring(0, 200)}...
                          </p>
                          <div style={{ 
                            display: 'flex', 
                            alignItems: 'center', 
                            justifyContent: 'space-between',
                            color: 'var(--text-tertiary)'
                          }}>
                            <span>{ctx.source}</span>
                            <a
                              href={ctx.link}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{ 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: '0.25rem',
                                color: 'var(--accent-primary)'
                              }}
                            >
                              <ExternalLink style={{ width: '12px', height: '12px' }} />
                              Open
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
          <div className="chat-message assistant">
            <div className="chat-loading">
              <Loader2 style={{ width: '16px', height: '16px' }} />
              <span>Analyzing news data...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Questions (only show when few messages) */}
      {messages.length <= 2 && !isLoading && (
        <div style={{ 
          padding: '1rem 1.5rem',
          borderTop: '1px solid var(--border-color)',
          background: 'var(--bg-tertiary)'
        }}>
          <p style={{ 
            fontSize: '0.75rem', 
            color: 'var(--text-tertiary)', 
            marginBottom: '0.75rem' 
          }}>
            Try asking:
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {suggestedQuestions.map((q, i) => (
              <button
                key={i}
                onClick={() => setInput(q)}
                style={{
                  padding: '0.5rem 0.875rem',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '0.8125rem',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                  transition: 'all var(--transition-fast)'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.borderColor = 'var(--accent-primary)';
                  e.currentTarget.style.color = 'var(--accent-primary)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-color)';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }}
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="chat-input-area">
        <form onSubmit={handleSubmit} className="chat-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about recent news events..."
            className="chat-input"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="chat-submit"
          >
            <Send style={{ width: '16px', height: '16px' }} />
            Send
          </button>
        </form>
        <p className="chat-hint">
          💡 Powered by Pathway's real-time RAG architecture with <span>Gemini AI</span>
        </p>
      </div>
    </div>
  );
};

export default AnalystChat;
