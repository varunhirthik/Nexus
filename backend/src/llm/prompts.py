"""System prompts and templates for the Live News Analyst."""

from datetime import datetime

SYSTEM_PROMPT = """You are an expert financial and general news analyst with access to real-time news feeds. Your primary responsibilities are:

1. **Synthesize Information**: Combine multiple news snippets to provide comprehensive answers
2. **Prioritize Recency**: When snippets contain conflicting information (e.g., updated numbers, changing events), always prioritize the most recent data
3. **Cite Sources**: Reference which news sources support your answer
4. **Acknowledge Gaps**: If information is missing or insufficient, clearly state "I do not have real-time data on that topic yet"
5. **Be Concise**: Provide clear, actionable insights without unnecessary verbosity
6. **Financial Context**: When discussing markets, provide relevant context (e.g., "This represents a 5% drop from yesterday's close")

**Important Guidelines**:
- Do NOT make up information or speculate beyond what's in the provided context
- Do NOT reference outdated knowledge from your training data - only use the provided news snippets
- Always include timestamps or relative time indicators (e.g., "According to Reuters 5 minutes ago...")
- If multiple sources conflict, mention the discrepancy

Current Date/Time: {current_time}
"""

RAG_QUERY_TEMPLATE = """Context from recent news articles:

{context}

---

User Question: {query}

Instructions: Based ONLY on the above context, provide a concise answer. If the context doesn't contain relevant information, say "I don't have recent news about that topic." Always mention which sources you're referencing.

Answer:"""


SENTIMENT_ANALYSIS_PROMPT = """Analyze the sentiment of the following news headline and summary. 
Provide a score from -1.0 (very negative) to 1.0 (very positive).

Consider:
- Market impact (crashes, rallies, uncertainty)
- Economic indicators (growth, recession, inflation)
- Geopolitical events (conflicts, agreements, tensions)
- Corporate news (earnings, layoffs, innovations)

Headline: {title}
Summary: {summary}

Return ONLY a number between -1.0 and 1.0. No explanation."""


def format_context_chunk(
    title: str,
    summary: str,
    source: str,
    published: str,
    link: str
) -> str:
    """Format a single retrieved chunk for inclusion in the context."""
    return f"""
[{source} | {published}]
Title: {title}
Summary: {summary}
Link: {link}
""".strip()


def build_rag_prompt(query: str, context_chunks: list) -> str:
    """
    Build the complete RAG prompt with context and query.
    
    Args:
        query: User's question
        context_chunks: List of dicts with keys: title, summary, source, published, link
    
    Returns:
        Formatted prompt string
    """
    # Format each context chunk
    formatted_context = "\n\n---\n\n".join([
        format_context_chunk(**chunk) for chunk in context_chunks
    ])
    
    # If no context, use a special message
    if not formatted_context:
        formatted_context = "[No recent news articles found matching this query]"
    
    # Build system prompt with current time
    system = SYSTEM_PROMPT.format(current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Build query template
    user_prompt = RAG_QUERY_TEMPLATE.format(
        context=formatted_context,
        query=query
    )
    
    return f"{system}\n\n{user_prompt}"


def build_sentiment_prompt(title: str, summary: str) -> str:
    """Build prompt for sentiment analysis."""
    return SENTIMENT_ANALYSIS_PROMPT.format(title=title, summary=summary)
