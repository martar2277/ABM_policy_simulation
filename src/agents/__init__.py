"""
Agents module - Contains all agent types and factory.
"""

from .base_agent import BaseAgent, LLMIntegrationLevel
from .agent_factory import AgentFactory
from .neet_agent import NEETAgent, EmploymentStatus
from .business_agent import BusinessAgent

# Auto-register agent types with factory
AgentFactory.register_agent_type('neet', NEETAgent)
AgentFactory.register_agent_type('business', BusinessAgent)

__all__ = [
    'BaseAgent',
    'LLMIntegrationLevel',
    'AgentFactory',
    'NEETAgent',
    'EmploymentStatus',
    'BusinessAgent',
]
