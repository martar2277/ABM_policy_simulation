"""
LLM-based profile generator for creating realistic agent attributes.
"""

import json
import random
from typing import Dict, Any, Optional
from .llm_client import LLMClient


class ProfileGenerator:
    """
    Generates realistic agent profiles using LLM.

    This is used for Level 1 (Initialization) LLM integration.
    """

    def __init__(self, llm_client: LLMClient, use_llm: bool = True):
        """
        Initialize profile generator.

        Args:
            llm_client: LLM client to use for generation
            use_llm: If False, use random generation instead
        """
        self.llm_client = llm_client
        self.use_llm = use_llm

    def generate_neet_profile(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a NEET agent profile.

        Args:
            context: Optional context (age range, region, etc.)

        Returns:
            Dictionary with NEET attributes
        """
        if not self.use_llm:
            return self._generate_neet_random(context)

        context = context or {}

        prompt = f"""Generate a realistic profile for a NEET (Not in Education, Employment, or Training) individual.

Context:
- Age range: {context.get('age_range', '18-29')}
- Region: {context.get('region', 'urban/rural mixed')}
- Economic context: {context.get('economic_context', 'moderate unemployment')}

Create a diverse, realistic profile that reflects real-world NEETs. Consider various backgrounds:
- Educational outcomes (dropout, graduate, vocational training)
- Barriers to employment (mental health, childcare, transportation, disabilities, language)
- Motivation levels (from very low to eager but blocked)
- Skill levels (from minimal to underutilized)

Return ONLY a JSON object with these fields:
{{
  "willingness_to_work": <float 0-1, where 0=no motivation, 1=very motivated>,
  "impeding_factors": <float 0-1, where 0=no barriers, 1=severe barriers>,
  "skill_level": <float 0-1, where 0=minimal skills, 1=highly skilled>,
  "age": <int 18-29>,
  "background": "<brief description of their situation>"
}}

Ensure diversity - not all NEETs are the same. Some are highly motivated but face barriers, others have low skills, etc.
"""

        try:
            response = self.llm_client.call(
                prompt=prompt,
                temperature=0.8,  # Higher temperature for diversity
                max_tokens=300
            )

            profile = self._parse_json_response(response['content'])

            # Validate and constrain values
            profile = self._validate_neet_profile(profile)

            return profile

        except Exception as e:
            print(f"Warning: LLM profile generation failed ({e}), using random fallback")
            return self._generate_neet_random(context)

    def generate_business_profile(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a Business agent profile.

        Args:
            context: Optional context (sector preferences, size range, etc.)

        Returns:
            Dictionary with Business attributes
        """
        if not self.use_llm:
            return self._generate_business_random(context)

        context = context or {}

        prompt = f"""Generate a realistic profile for a business/employer.

Context:
- Preferred sectors: {context.get('sectors', 'mixed')}
- Size range: {context.get('size_range', '5-100 employees')}
- Region: {context.get('region', 'urban/rural mixed')}

Create a diverse business that might hire youth apprentices. Consider:
- Company size (affects hiring capacity)
- Sector (manufacturing, services, retail, hospitality, construction, etc.)
- Willingness to hire youth/NEETs (varies by company culture, past experience, capacity)
- Training capacity and culture

Return ONLY a JSON object with these fields:
{{
  "company_size": <int 5-100, number of total employees>,
  "willingness_to_hire": <float 0-1, where 0=unwilling, 1=very willing to hire NEETs>,
  "sector": "<one of: manufacturing, services, retail, hospitality, construction, technology, other>",
  "description": "<brief description of the company>"
}}

Create diversity - some companies are eager to hire youth, others are cautious. Some are small, others larger.
"""

        try:
            response = self.llm_client.call(
                prompt=prompt,
                temperature=0.8,
                max_tokens=300
            )

            profile = self._parse_json_response(response['content'])

            # Validate and constrain values
            profile = self._validate_business_profile(profile)

            return profile

        except Exception as e:
            print(f"Warning: LLM profile generation failed ({e}), using random fallback")
            return self._generate_business_random(context)

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response.

        LLMs sometimes wrap JSON in markdown code blocks.
        """
        # Remove markdown code blocks if present
        content = content.strip()
        if content.startswith('```'):
            # Find JSON between code blocks
            lines = content.split('\n')
            content = '\n'.join(lines[1:-1]) if len(lines) > 2 else content

        # Try to parse JSON
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON object in text
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
            raise

    def _validate_neet_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and constrain NEET profile values"""
        return {
            'willingness_to_work': max(0.0, min(1.0, float(profile.get('willingness_to_work', 0.5)))),
            'impeding_factors': max(0.0, min(1.0, float(profile.get('impeding_factors', 0.5)))),
            'skill_level': max(0.0, min(1.0, float(profile.get('skill_level', 0.5)))),
            'age': max(16, min(35, int(profile.get('age', 22)))),
            'background': str(profile.get('background', 'No background provided'))[:200]
        }

    def _validate_business_profile(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and constrain Business profile values"""
        valid_sectors = ['manufacturing', 'services', 'retail', 'hospitality', 'construction', 'technology', 'other']
        sector = profile.get('sector', 'other').lower()
        if sector not in valid_sectors:
            sector = 'other'

        return {
            'company_size': max(1, min(500, int(profile.get('company_size', 20)))),
            'willingness_to_hire': max(0.0, min(1.0, float(profile.get('willingness_to_hire', 0.5)))),
            'sector': sector,
            'description': str(profile.get('description', 'No description provided'))[:200]
        }

    def _generate_neet_random(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fallback: Generate NEET profile with random values"""
        backgrounds = [
            "Dropped out of high school, interested in manual work",
            "College graduate, struggling with mental health issues",
            "Single parent, limited by childcare responsibilities",
            "Recent immigrant, language barriers and credential recognition issues",
            "Tech-interested but lacks formal training",
            "Experienced worker, laid off during recession",
            "Young person with learning disability seeking supported employment",
            "Recent high school graduate, uncertain about career path"
        ]

        return {
            'willingness_to_work': round(random.uniform(0.2, 0.9), 2),
            'impeding_factors': round(random.uniform(0.1, 0.8), 2),
            'skill_level': round(random.uniform(0.1, 0.7), 2),
            'age': random.randint(18, 29),
            'background': random.choice(backgrounds)
        }

    def _generate_business_random(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fallback: Generate Business profile with random values"""
        sectors = ['manufacturing', 'services', 'retail', 'hospitality', 'construction', 'technology']
        descriptions = [
            "Small family business looking to expand",
            "Growing startup in need of entry-level talent",
            "Established company with training programs",
            "Seasonal business with variable hiring needs",
            "Large corporation with structured apprenticeship program",
            "Local business committed to community employment"
        ]

        return {
            'company_size': random.randint(5, 100),
            'willingness_to_hire': round(random.uniform(0.3, 0.9), 2),
            'sector': random.choice(sectors),
            'description': random.choice(descriptions)
        }

    def generate_batch(
        self,
        agent_type: str,
        count: int,
        context: Optional[Dict[str, Any]] = None
    ) -> list:
        """
        Generate multiple profiles in batch.

        Args:
            agent_type: 'neet' or 'business'
            count: Number of profiles to generate
            context: Optional context for generation

        Returns:
            List of profile dictionaries
        """
        profiles = []

        generator = {
            'neet': self.generate_neet_profile,
            'business': self.generate_business_profile
        }.get(agent_type)

        if not generator:
            raise ValueError(f"Unknown agent type: {agent_type}")

        for i in range(count):
            profile = generator(context)
            profiles.append(profile)

            # Progress indication for large batches
            if (i + 1) % 10 == 0:
                print(f"Generated {i + 1}/{count} {agent_type} profiles...")

        return profiles
