"""Gemini embedder and LLM wrapper for Pathway integration."""

import logging
from typing import List, Optional
import time

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerateContentResponse
except ImportError:
    genai = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiLLM:
    """
    Wrapper for Google Gemini LLM with retry logic and error handling.
    
    Features:
    - Automatic retry with exponential backoff
    - Rate limit handling
    - Context window management
    - Streaming support (future enhancement)
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "models/gemini-2.5-flash",
        temperature: float = 0.3,
        max_retries: int = 3
    ):
        """
        Initialize Gemini LLM.
        
        Args:
            api_key: Google AI Studio API key
            model: Full model path (e.g., models/gemini-2.5-flash)
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            max_retries: Maximum retry attempts on failure
        """
        if genai is None:
            raise ImportError(
                "google-generativeai not installed. "
                "Run: pip install google-generativeai"
            )
        
        self.api_key = api_key
        self.model_name = model
        self.temperature = temperature
        self.max_retries = max_retries
        
        # Configure API
        genai.configure(api_key=api_key)
        
        # List available models for debugging
        try:
            available_models = []
            for m in genai.list_models():
                if hasattr(m, 'supported_generation_methods') and 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            logger.info(f"Available models for generateContent: {available_models}")
        except Exception as e:
            logger.warning(f"Could not list models: {e}")
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=model,
            generation_config={
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        
        logger.info(f"Initialized Gemini LLM: {model}")
    
    def generate(self, prompt: str) -> str:
        """
        Generate response from Gemini with retry logic.
        
        Args:
            prompt: Input prompt string
        
        Returns:
            Generated text response
        
        Raises:
            Exception: If all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                response = self.model.generate_content(prompt)
                
                # Extract text from response
                if hasattr(response, 'text'):
                    return response.text
                elif hasattr(response, 'parts'):
                    return ''.join([part.text for part in response.parts])
                else:
                    raise ValueError("Unexpected response format")
            
            except Exception as e:
                error_msg = str(e)
                
                # Handle rate limits
                if "429" in error_msg or "quota" in error_msg.lower():
                    wait_time = (2 ** attempt) * 5  # 5s, 10s, 20s
                    logger.warning(
                        f"Rate limit hit (attempt {attempt + 1}/{self.max_retries}). "
                        f"Waiting {wait_time}s..."
                    )
                    time.sleep(wait_time)
                    continue
                
                # Handle other errors
                logger.error(f"Gemini error (attempt {attempt + 1}/{self.max_retries}): {e}")
                
                if attempt == self.max_retries - 1:
                    logger.error(f"Final error details: {type(e).__name__}: {str(e)}")
                    raise
                
                time.sleep(2 ** attempt)  # Exponential backoff
        
        raise Exception(f"Failed after {self.max_retries} attempts")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embeddings for text using Gemini embeddings API.
        
        Args:
            text: Input text to embed
        
        Returns:
            Embedding vector (768-dimensional for text-embedding-004)
        """
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            # Return zero vector as fallback (not ideal but prevents crash)
            return [0.0] * 768


def get_gemini_sentiment(llm: GeminiLLM, title: str, summary: str) -> float:
    """
    Use Gemini to analyze sentiment of a news article.
    
    Args:
        llm: Initialized GeminiLLM instance
        title: Article title
        summary: Article summary
    
    Returns:
        Sentiment score from -1.0 to 1.0
    """
    from llm.prompts import build_sentiment_prompt
    
    prompt = build_sentiment_prompt(title, summary)
    
    try:
        response = llm.generate(prompt)
        # Parse float from response
        score = float(response.strip())
        # Clamp to valid range
        return max(-1.0, min(1.0, score))
    
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        # Return neutral sentiment on error
        return 0.0
