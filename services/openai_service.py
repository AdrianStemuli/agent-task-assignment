"""
OpenAI service for interacting with the OpenAI API
"""

from openai import AsyncOpenAI
from typing import Optional, Dict, Any
from config import settings
import json


class OpenAIService:
    """Service for interacting with OpenAI API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI service
        
        Args:
            api_key: OpenAI API key. If not provided, uses settings.openai_api_key
        """
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it to the constructor."
            )
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens
    
    async def generate_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a completion using OpenAI API
        
        Args:
            system_prompt: System message to set context
            user_prompt: User message with the actual prompt
            temperature: Temperature for generation (overrides default)
            max_tokens: Max tokens for generation (overrides default)
            response_format: Optional response format specification
            
        Returns:
            Generated text response
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
           
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        try:
            response = await self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def generate_json_completion(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate a JSON completion using OpenAI API
        
        Args:
            system_prompt: System message to set context
            user_prompt: User message with the actual prompt
            temperature: Temperature for generation (overrides default)
            max_tokens: Max tokens for generation (overrides default)
            
        Returns:
            Parsed JSON response as dictionary
        """
        response_text = await self.generate_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON response: {str(e)}")
    
    async def validate_api_key(self) -> bool:
        """
        Validate that the API key is set and working
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False
