"""LLM package for Gemini integration and RAG queries."""

from .embedder import GeminiLLM, get_gemini_sentiment
from .rag_query import RAGQueryService, get_rag_service, init_rag_service
from .prompts import (
    SYSTEM_PROMPT,
    RAG_QUERY_TEMPLATE,
    build_rag_prompt,
    format_context_chunk,
    build_sentiment_prompt
)

__all__ = [
    'GeminiLLM',
    'get_gemini_sentiment',
    'RAGQueryService',
    'get_rag_service',
    'init_rag_service',
    'SYSTEM_PROMPT',
    'RAG_QUERY_TEMPLATE',
    'build_rag_prompt',
    'format_context_chunk',
    'build_sentiment_prompt'
]
