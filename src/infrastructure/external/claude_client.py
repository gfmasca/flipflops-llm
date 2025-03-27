"""
Client for interacting with the Anthropic Claude API.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
import requests
from requests.exceptions import RequestException, Timeout

# Configure logger
logger = logging.getLogger(__name__)


class ClaudeClient:
    """Client for interacting with the Anthropic Claude API."""

    # Default Claude API endpoints
    BASE_URL = "https://api.anthropic.com"
    MESSAGES_ENDPOINT = "/v1/messages"
    
    # Model options
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = CLAUDE_3_SONNET,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize the Claude API client.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env variable)
            model: Claude model to use
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation (0-1)
            system_prompt: System prompt to set context for Claude
        """
        # Get API key from environment variable if not provided
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable."
            )
        
        # Set up parameters
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.system_prompt = system_prompt
        
        # Set up headers with API key
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        logger.info(f"Initialized Claude client with model {self.model}")

    def generate_response(
        self, 
        prompt: str, 
        context: Optional[List[str]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from Claude using the messages API.
        
        Args:
            prompt: The user message to send to Claude
            context: List of context passages to include in the prompt
            max_tokens: Override the default max_tokens if provided
            temperature: Override the default temperature if provided
            system_prompt: Override the default system_prompt if provided
            
        Returns:
            The parsed API response as a dictionary
            
        Raises:
            ValueError: If the prompt is empty
            RequestException: If the API request fails
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # Prepare the context if provided
        formatted_context = ""
        if context and len(context) > 0:
            formatted_context = "\n\n".join([f"CONTEXT: {ctx}" for ctx in context])
        
        # Construct the messages payload
        payload = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature or self.temperature,
            "messages": [
                {
                    "role": "user",
                    "content": f"{formatted_context}\n\n{prompt}" if formatted_context else prompt
                }
            ]
        }
        
        # Add system prompt if provided
        if system_prompt or self.system_prompt:
            payload["system"] = system_prompt or self.system_prompt
        
        try:
            logger.debug(f"Sending request to Claude API with model {self.model}")
            response = requests.post(
                f"{self.BASE_URL}{self.MESSAGES_ENDPOINT}",
                headers=self.headers,
                json=payload,
                timeout=60  # 60 second timeout
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            logger.debug("Received successful response from Claude API")
            return result
            
        except Timeout:
            logger.error("Timeout while connecting to Claude API")
            raise RequestException("Request to Claude API timed out")
        except RequestException as e:
            logger.error(f"Error connecting to Claude API: {str(e)}")
            
            # Try to extract error details if available
            error_details = "Unknown error"
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_details = error_data.get("error", {}).get("message", str(e))
                except:
                    error_details = e.response.text or str(e)
            
            raise RequestException(f"Failed to connect to Claude API: {error_details}")
        except Exception as e:
            logger.error(f"Unexpected error while generating response: {str(e)}")
            raise

    def extract_response_text(self, response: Dict[str, Any]) -> str:
        """
        Extract the text content from Claude's response.
        
        Args:
            response: The full API response from Claude
            
        Returns:
            The extracted text content
            
        Raises:
            ValueError: If the response format is invalid
        """
        try:
            content = response.get("content", [])
            if not content or not isinstance(content, list):
                raise ValueError("Invalid response format: missing or invalid content field")
            
            # Extract text from all content blocks with type 'text'
            text_parts = []
            for block in content:
                if block.get("type") == "text":
                    text_parts.append(block.get("text", ""))
            
            return "".join(text_parts)
        except Exception as e:
            logger.error(f"Error parsing Claude response: {str(e)}")
            raise ValueError(f"Failed to parse Claude response: {str(e)}")

    def generate_text(
        self, 
        prompt: str, 
        context: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate text from Claude and return just the text response.
        
        A convenience wrapper that handles the full flow and returns just the text.
        
        Args:
            prompt: The user message to send to Claude
            context: List of context passages to include in the prompt
            **kwargs: Additional arguments to pass to generate_response
            
        Returns:
            The generated text response
            
        Raises:
            RequestException: If the API request fails
            ValueError: If the response cannot be parsed
        """
        response = self.generate_response(prompt, context, **kwargs)
        return self.extract_response_text(response) 
