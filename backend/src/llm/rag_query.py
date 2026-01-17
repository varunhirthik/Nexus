"""
RAG Query Service - Retrieval-Augmented Generation for News Analysis

This module handles:
1. Retrieving relevant articles based on user query
2. Building context for the LLM
3. Generating AI responses using Gemini
4. Fallback to general knowledge when no articles match
"""

import logging
import re
import time
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from .embedder import GeminiLLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# System prompt for conversational news analyst
NEWS_ANALYST_SYSTEM_PROMPT = """You are Nexus, a friendly and knowledgeable AI News Analyst. You have access to real-time news data and can help users understand current events, market trends, and breaking news.

**Your Personality:**
- Conversational and approachable, but professional
- You explain complex topics in simple terms
- You're honest about what you know and don't know
- You provide balanced perspectives on news events

**Response Guidelines:**
1. Be conversational - write like you're talking to a friend who's curious about the news
2. Structure longer responses with clear paragraphs, not bullet points
3. When citing sources, mention them naturally (e.g., "According to Reuters..." or "BBC is reporting that...")
4. Provide context and explain why news matters
5. If asked for opinions, clarify you're providing analysis based on available data

**Important Rules:**
- Base your answers primarily on the provided news context
- If the context doesn't cover the topic, you may use general knowledge BUT clearly indicate this
- Never make up specific facts, numbers, or quotes
- If you're uncertain, say so

Current Date/Time: {current_time}
"""

RAG_PROMPT_WITH_CONTEXT = """Here are the relevant news articles I found:

{context}

---

User's Question: {query}

Please provide a helpful, conversational response based on the news articles above. Mention sources naturally in your response. If the articles don't fully answer the question, supplement with general knowledge but clearly indicate when you're doing so."""

RAG_PROMPT_NO_CONTEXT = """User's Question: {query}

I don't have any recent news articles specifically about this topic in my current data. However, I can share what I know from general knowledge.

Please provide a helpful response, but clearly indicate that this information is from general knowledge and not from recent news articles. Suggest the user check reliable news sources for the latest updates."""


@dataclass
class SearchResult:
    """A single search result with relevance score."""
    article: Dict
    score: float
    match_type: str  # 'title', 'content', 'keyword'


class RAGQueryService:
    """
    Service for handling RAG queries with Gemini AI.
    
    Features:
    - Keyword-based article retrieval
    - Context building with source attribution
    - Conversational AI response generation
    - General knowledge fallback
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "models/gemini-2.5-flash",
        temperature: float = 0.7,  # Slightly higher for conversational tone
        max_context_articles: int = 5
    ):
        """
        Initialize RAG Query Service.
        
        Args:
            api_key: Gemini API key
            model: Model name
            temperature: Response creativity (0.7 for conversational)
            max_context_articles: Max articles to include in context
        """
        self.llm = GeminiLLM(
            api_key=api_key,
            model=model,
            temperature=temperature
        )
        self.max_context_articles = max_context_articles
        
        logger.info(f"RAGQueryService initialized with {model}")
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract important keywords from user query.
        
        Args:
            query: User's question
            
        Returns:
            List of keywords to search for
        """
        # Remove common stop words and question words
        stop_words = {
            'what', 'is', 'are', 'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'about', 'how', 'why', 'when', 'where',
            'who', 'which', 'that', 'this', 'it', 'can', 'could', 'would', 'should',
            'do', 'does', 'did', 'has', 'have', 'had', 'be', 'been', 'being',
            'will', 'was', 'were', 'am', 'tell', 'me', 'please', 'happening',
            'going', 'latest', 'recent', 'news', 'update', 'updates', 'any'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]+\b', query.lower())
        
        # Filter and return meaningful keywords
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Also check for known entities (case-insensitive matching)
        known_entities = [
            'tesla', 'bitcoin', 'btc', 'crypto', 'ai', 'openai', 'google', 'apple',
            'microsoft', 'amazon', 'meta', 'facebook', 'nvidia', 'fed', 'federal reserve',
            'inflation', 'recession', 'stock', 'market', 'nasdaq', 'dow', 's&p',
            'china', 'russia', 'ukraine', 'israel', 'gaza', 'trump', 'biden'
        ]
        
        query_lower = query.lower()
        for entity in known_entities:
            if entity in query_lower and entity not in keywords:
                keywords.append(entity)
        
        return keywords
    
    def _calculate_relevance(self, article: Dict, keywords: List[str]) -> Tuple[float, str]:
        """
        Calculate relevance score for an article.
        
        Args:
            article: Article dict with title, summary, content
            keywords: Search keywords
            
        Returns:
            Tuple of (score, match_type)
        """
        title = (article.get('title') or '').lower()
        summary = (article.get('summary') or '').lower()
        content = (article.get('content') or '').lower()
        
        score = 0.0
        match_type = 'none'
        
        for keyword in keywords:
            kw = keyword.lower()
            
            # Title match (highest weight)
            if kw in title:
                score += 10.0
                match_type = 'title'
            
            # Summary match (medium weight)
            if kw in summary:
                score += 5.0
                if match_type == 'none':
                    match_type = 'summary'
            
            # Content match (lower weight)
            if kw in content:
                score += 2.0
                if match_type == 'none':
                    match_type = 'content'
        
        # Boost recent articles
        timestamp = article.get('timestamp', 0)
        if timestamp:
            age_hours = (time.time() - timestamp) / 3600
            if age_hours < 1:
                score *= 1.5  # Very recent
            elif age_hours < 6:
                score *= 1.2  # Recent
            elif age_hours > 48:
                score *= 0.8  # Old
        
        return score, match_type
    
    def search_articles(self, query: str, articles: List[Dict]) -> List[SearchResult]:
        """
        Search articles for relevance to query.
        
        Args:
            query: User's question
            articles: List of article dicts
            
        Returns:
            List of SearchResult sorted by relevance
        """
        keywords = self._extract_keywords(query)
        logger.info(f"Searching with keywords: {keywords}")
        
        if not keywords:
            # If no keywords extracted, return empty
            return []
        
        results = []
        for article in articles:
            score, match_type = self._calculate_relevance(article, keywords)
            
            if score > 0:
                results.append(SearchResult(
                    article=article,
                    score=score,
                    match_type=match_type
                ))
        
        # Sort by score descending
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Return top results
        return results[:self.max_context_articles]
    
    def _format_article_for_context(self, article: Dict) -> str:
        """Format a single article for inclusion in LLM context."""
        title = article.get('title', 'Untitled')
        summary = article.get('summary', '')
        source = article.get('source', 'Unknown Source')
        published = article.get('published', '')
        link = article.get('link', '')
        
        # Parse published date for display
        if published:
            try:
                # Try to make it more readable
                if 'T' in published:
                    published = published.split('T')[0]
            except:
                pass
        
        return f"""**{title}**
Source: {source} | {published}
{summary}
Link: {link}"""
    
    def _build_context(self, search_results: List[SearchResult]) -> str:
        """Build context string from search results."""
        if not search_results:
            return ""
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            formatted = self._format_article_for_context(result.article)
            context_parts.append(f"[Article {i}]\n{formatted}")
        
        return "\n\n---\n\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Build the complete prompt for Gemini."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        system = NEWS_ANALYST_SYSTEM_PROMPT.format(current_time=current_time)
        
        if context:
            user_prompt = RAG_PROMPT_WITH_CONTEXT.format(
                context=context,
                query=query
            )
        else:
            user_prompt = RAG_PROMPT_NO_CONTEXT.format(query=query)
        
        return f"{system}\n\n{user_prompt}"
    
    def query(
        self,
        query: str,
        articles: List[Dict]
    ) -> Dict:
        """
        Process a user query and generate AI response.
        
        Args:
            query: User's question
            articles: Available news articles
            
        Returns:
            Dict with:
                - answer: AI-generated response
                - context: List of source articles used
                - used_general_knowledge: Whether fallback was used
                - latency_ms: Response time
        """
        start_time = time.time()
        
        # Search for relevant articles
        search_results = self.search_articles(query, articles)
        
        # Build context
        context = self._build_context(search_results)
        used_general_knowledge = len(search_results) == 0
        
        logger.info(f"Found {len(search_results)} relevant articles for query: {query[:50]}...")
        
        # Build prompt
        prompt = self._build_prompt(query, context)
        
        # Generate response
        try:
            answer = self.llm.generate(prompt)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            answer = "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        
        # Format context for response
        context_for_response = [
            {
                "text": r.article.get('summary', '')[:200],
                "title": r.article.get('title', ''),
                "link": r.article.get('link', ''),
                "source": r.article.get('source', ''),
                "timestamp": r.article.get('timestamp', 0),
                "relevance_score": r.score
            }
            for r in search_results
        ]
        
        return {
            "answer": answer,
            "context": context_for_response,
            "used_general_knowledge": used_general_knowledge,
            "keywords_matched": self._extract_keywords(query),
            "latency_ms": latency_ms
        }


# Singleton instance
_rag_service: Optional[RAGQueryService] = None


def get_rag_service() -> Optional[RAGQueryService]:
    """Get the global RAG service instance."""
    return _rag_service


def init_rag_service(
    api_key: str,
    model: str = "gemini-1.5-flash",
    temperature: float = 0.7
) -> RAGQueryService:
    """
    Initialize the global RAG service.
    
    Args:
        api_key: Gemini API key
        model: Model name
        temperature: Response creativity
        
    Returns:
        Initialized RAGQueryService
    """
    global _rag_service
    
    _rag_service = RAGQueryService(
        api_key=api_key,
        model=model,
        temperature=temperature
    )
    
    return _rag_service
