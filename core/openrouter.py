"""
OpenRouter API Client
Handles all communication with Claude Sonnet 4.5 via OpenRouter
"""

import httpx
import json
from typing import Iterator, Union, List, Dict
from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    MODEL,
    MAX_TOKENS,
    TEMPERATURE,
    HTTP_TIMEOUT,
    HTTP_REFERER,
    HTTP_TITLE,
)


class OpenRouterClient:
    """HTTP client for OpenRouter API."""

    def __init__(self):
        self.api_key = OPENROUTER_API_KEY
        self.base_url = OPENROUTER_BASE_URL
        self.model = MODEL
        self.timeout = HTTP_TIMEOUT

        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set. Please set it in .env file.")

    def _get_headers(self) -> Dict[str, str]:
        """Return HTTP headers for OpenRouter requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": HTTP_REFERER,
            "X-Title": HTTP_TITLE,
            "Content-Type": "application/json",
        }

    def chat(
        self,
        messages: List[Dict],
        system: str,
        temperature: float = TEMPERATURE,
        max_tokens: int = MAX_TOKENS,
        stream: bool = False,
    ) -> Union[str, Iterator[str]]:
        """
        Send a chat request to OpenRouter.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system: System prompt
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            stream: Whether to stream the response

        Returns:
            Full response text or iterator of chunks if streaming
        """
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}] + messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload,
                )
                response.raise_for_status()

                if stream:
                    return self._handle_stream(response)
                else:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]

        except httpx.RequestError as e:
            raise RuntimeError(f"OpenRouter API request failed: {e}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse OpenRouter response: {e}")

    def _handle_stream(self, response) -> Iterator[str]:
        """
        Handle streaming response from OpenRouter.

        Yields text chunks as they arrive.
        """
        for line in response.iter_lines():
            if line.startswith("data: "):
                chunk = line[6:]  # Remove "data: " prefix
                if chunk == "[DONE]":
                    break
                try:
                    data = json.loads(chunk)
                    if "choices" in data and len(data["choices"]) > 0:
                        delta = data["choices"][0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]
                except json.JSONDecodeError:
                    continue


# Singleton instance
_client = None


def get_client() -> OpenRouterClient:
    """Get or create the OpenRouter client singleton."""
    global _client
    if _client is None:
        _client = OpenRouterClient()
    return _client


def chat(
    messages: List[Dict],
    system: str,
    temperature: float = TEMPERATURE,
    max_tokens: int = MAX_TOKENS,
) -> str:
    """
    Convenience function to call the chat API.

    Args:
        messages: List of message dicts
        system: System prompt
        temperature: Sampling temperature
        max_tokens: Max tokens in response

    Returns:
        Full response text
    """
    client = get_client()
    return client.chat(
        messages=messages,
        system=system,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False,
    )


def chat_stream(
    messages: List[Dict],
    system: str,
    temperature: float = TEMPERATURE,
    max_tokens: int = MAX_TOKENS,
) -> Iterator[str]:
    """
    Convenience function to call the chat API with streaming.

    Args:
        messages: List of message dicts
        system: System prompt
        temperature: Sampling temperature
        max_tokens: Max tokens in response

    Returns:
        Iterator of response text chunks
    """
    client = get_client()
    return client.chat(
        messages=messages,
        system=system,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
