"""
Base agent class for all agent types in the ABM simulation.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any


class LLMIntegrationLevel(Enum):
    """Defines how much LLM integration is used in agent behavior"""
    NONE = 0              # Pure rule-based
    INITIALIZATION = 1    # LLM for profile generation only (RECOMMENDED)
    SELECTIVE = 2         # LLM for critical/uncertain decisions
    FULL = 3             # LLM for all decisions


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the simulation.

    All agent types (NEET, Business, UnemploymentService, etc.) inherit from this.
    """

    def __init__(self, agent_id: str, agent_type: str):
        """
        Initialize base agent.

        Args:
            agent_id: Unique identifier for this agent
            agent_type: Type of agent (e.g., 'neet', 'business')
        """
        self.id = agent_id
        self.agent_type = agent_type
        self.created_at_month = 0

        # Tracking
        self.llm_call_count = 0
        self.interaction_history = []

    @abstractmethod
    def step(self, month: int, context: Dict[str, Any]):
        """
        Execute one time step (month) for this agent.

        Args:
            month: Current simulation month
            context: Simulation context (other agents, policies, etc.)
        """
        pass

    def log_interaction(self, month: int, interaction_type: str, target_agent_id: str, details: Dict[str, Any]):
        """
        Record an interaction with another agent.

        Args:
            month: When the interaction occurred
            interaction_type: Type of interaction (e.g., 'job_application', 'hire')
            target_agent_id: ID of the other agent
            details: Additional information about the interaction
        """
        self.interaction_history.append({
            'month': month,
            'type': interaction_type,
            'target': target_agent_id,
            'details': details
        })

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize agent to dictionary for analysis/storage.

        Returns:
            Dictionary representation of agent state
        """
        return {
            'id': self.id,
            'type': self.agent_type,
            'llm_calls': self.llm_call_count,
            'interactions': len(self.interaction_history)
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
