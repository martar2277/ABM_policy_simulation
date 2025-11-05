"""
Factory for creating agents of different types.

This enables easy extensibility - new agent types can be registered dynamically.
"""

from typing import Dict, Type, Any
from .base_agent import BaseAgent


class AgentFactory:
    """
    Factory pattern for creating agents.

    Supports registration of new agent types without modifying existing code.
    """

    # Registry of agent types
    _agent_types: Dict[str, Type[BaseAgent]] = {}

    @classmethod
    def register_agent_type(cls, type_name: str, agent_class: Type[BaseAgent]):
        """
        Register a new agent type.

        Args:
            type_name: Name to identify this agent type (e.g., 'neet', 'business')
            agent_class: Class that implements this agent type
        """
        if type_name in cls._agent_types:
            raise ValueError(f"Agent type '{type_name}' is already registered")

        if not issubclass(agent_class, BaseAgent):
            raise TypeError(f"Agent class must inherit from BaseAgent")

        cls._agent_types[type_name] = agent_class

    @classmethod
    def create(cls, agent_type: str, agent_id: str, **kwargs) -> BaseAgent:
        """
        Create an agent of the specified type.

        Args:
            agent_type: Type of agent to create
            agent_id: Unique ID for the new agent
            **kwargs: Additional parameters passed to agent constructor

        Returns:
            New agent instance

        Raises:
            ValueError: If agent_type is not registered
        """
        if agent_type not in cls._agent_types:
            raise ValueError(
                f"Unknown agent type: '{agent_type}'. "
                f"Registered types: {list(cls._agent_types.keys())}"
            )

        agent_class = cls._agent_types[agent_type]
        return agent_class(agent_id=agent_id, **kwargs)

    @classmethod
    def get_registered_types(cls) -> list:
        """
        Get list of all registered agent types.

        Returns:
            List of registered type names
        """
        return list(cls._agent_types.keys())

    @classmethod
    def clear_registry(cls):
        """Clear all registered agent types (mainly for testing)"""
        cls._agent_types.clear()
