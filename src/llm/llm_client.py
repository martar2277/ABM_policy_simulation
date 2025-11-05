"""
LLM client for calling various LLM APIs (OpenAI, Anthropic, or mock).
"""

import os
import json
import random
from typing import Dict, Any, Optional
from enum import Enum


class LLMProvider(Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOCK = "mock"  # For testing without API calls


class LLMClient:
    """
    Client for interacting with LLM APIs.

    Supports multiple providers and tracks usage/costs.
    """

    def __init__(
        self,
        provider: str = "mock",
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize LLM client.

        Args:
            provider: LLM provider ('openai', 'anthropic', 'mock')
            model: Model name to use
            api_key: API key (or None to read from environment)
            timeout: Request timeout in seconds
        """
        self.provider = LLMProvider(provider)
        self.model = model
        self.timeout = timeout

        # Cost tracking
        self.total_calls = 0
        self.total_tokens = 0
        self.estimated_cost = 0.0

        # Initialize provider-specific client
        if self.provider == LLMProvider.OPENAI:
            self._init_openai(api_key)
        elif self.provider == LLMProvider.ANTHROPIC:
            self._init_anthropic(api_key)
        elif self.provider == LLMProvider.MOCK:
            self._init_mock()

    def _init_openai(self, api_key: Optional[str]):
        """Initialize OpenAI client"""
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=api_key or os.getenv('OPENAI_API_KEY')
            )
        except ImportError:
            raise ImportError(
                "OpenAI package not installed. Run: pip install openai"
            )

    def _init_anthropic(self, api_key: Optional[str]):
        """Initialize Anthropic client"""
        try:
            import anthropic
            self.client = anthropic.Anthropic(
                api_key=api_key or os.getenv('ANTHROPIC_API_KEY')
            )
        except ImportError:
            raise ImportError(
                "Anthropic package not installed. Run: pip install anthropic"
            )

    def _init_mock(self):
        """Initialize mock client (no API calls)"""
        self.client = None

    def call(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call LLM API with a prompt.

        Args:
            prompt: User prompt
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            system_prompt: Optional system prompt

        Returns:
            Dictionary with 'content' and metadata
        """
        self.total_calls += 1

        if self.provider == LLMProvider.OPENAI:
            return self._call_openai(prompt, temperature, max_tokens, system_prompt)
        elif self.provider == LLMProvider.ANTHROPIC:
            return self._call_anthropic(prompt, temperature, max_tokens, system_prompt)
        elif self.provider == LLMProvider.MOCK:
            return self._call_mock(prompt, temperature, max_tokens)

    def _call_openai(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Call OpenAI API"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=self.timeout
        )

        content = response.choices[0].message.content
        tokens = response.usage.total_tokens

        self.total_tokens += tokens
        self.estimated_cost += self._estimate_cost(tokens)

        return {
            'content': content,
            'tokens': tokens,
            'model': self.model,
            'provider': 'openai'
        }

    def _call_anthropic(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> Dict[str, Any]:
        """Call Anthropic API"""
        kwargs = {
            'model': self.model,
            'max_tokens': max_tokens,
            'temperature': temperature,
            'messages': [{'role': 'user', 'content': prompt}]
        }

        if system_prompt:
            kwargs['system'] = system_prompt

        response = self.client.messages.create(**kwargs)

        content = response.content[0].text
        tokens = response.usage.input_tokens + response.usage.output_tokens

        self.total_tokens += tokens
        self.estimated_cost += self._estimate_cost(tokens)

        return {
            'content': content,
            'tokens': tokens,
            'model': self.model,
            'provider': 'anthropic'
        }

    def _call_mock(self, prompt: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
        """
        Mock LLM call that returns realistic-looking JSON without API call.

        This is useful for testing and development.
        """
        # Simple mock that returns random but realistic values
        mock_tokens = random.randint(200, 400)
        self.total_tokens += mock_tokens

        # Parse what kind of profile is being requested
        if "NEET" in prompt or "youth" in prompt.lower():
            content = self._generate_mock_neet_profile()
        elif "business" in prompt.lower() or "company" in prompt.lower():
            content = self._generate_mock_business_profile()
        else:
            content = '{"mock": true, "note": "Mock LLM response"}'

        return {
            'content': content,
            'tokens': mock_tokens,
            'model': 'mock',
            'provider': 'mock'
        }

    def _generate_mock_neet_profile(self) -> str:
        """Generate a realistic mock NEET profile"""
        profile = {
            "willingness_to_work": round(random.uniform(0.2, 0.9), 2),
            "impeding_factors": round(random.uniform(0.1, 0.8), 2),
            "skill_level": round(random.uniform(0.1, 0.7), 2),
            "age": random.randint(18, 29),
            "background": random.choice([
                "Dropped out of high school, interested in manual work",
                "College graduate, struggling with mental health issues",
                "Single parent, limited by childcare responsibilities",
                "Recent immigrant, language barriers and credential recognition issues",
                "Tech-interested but lacks formal training",
                "Experienced worker, laid off during recession"
            ])
        }
        return json.dumps(profile, indent=2)

    def _generate_mock_business_profile(self) -> str:
        """Generate a realistic mock business profile"""
        profile = {
            "company_size": random.randint(5, 100),
            "willingness_to_hire": round(random.uniform(0.3, 0.9), 2),
            "sector": random.choice(["manufacturing", "services", "retail", "hospitality", "construction"]),
            "description": random.choice([
                "Small family business looking to expand",
                "Growing startup in need of entry-level talent",
                "Established company with training programs",
                "Seasonal business with variable hiring needs"
            ])
        }
        return json.dumps(profile, indent=2)

    def _estimate_cost(self, tokens: int) -> float:
        """
        Estimate cost in USD for token usage.

        Args:
            tokens: Number of tokens used

        Returns:
            Estimated cost in USD
        """
        # Rough cost estimates (as of 2024)
        cost_per_1k = {
            'gpt-4': 0.045,  # Average of input/output
            'gpt-3.5-turbo': 0.0015,
            'claude-3-opus': 0.045,
            'claude-3-sonnet': 0.006,
            'mock': 0.0
        }

        rate = cost_per_1k.get(self.model, 0.03)
        return (tokens / 1000) * rate

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics.

        Returns:
            Dictionary with call count, tokens, estimated cost
        """
        return {
            'total_calls': self.total_calls,
            'total_tokens': self.total_tokens,
            'estimated_cost_usd': round(self.estimated_cost, 2),
            'provider': self.provider.value,
            'model': self.model
        }

    def reset_stats(self):
        """Reset usage statistics"""
        self.total_calls = 0
        self.total_tokens = 0
        self.estimated_cost = 0.0
