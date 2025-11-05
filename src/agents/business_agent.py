"""
Business agent implementation.
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent


class BusinessAgent(BaseAgent):
    """
    Business/employer agent that can hire NEET apprentices.

    Attributes match the specification in the ABM guide (Section 2.2).
    """

    def __init__(
        self,
        agent_id: str,
        company_size: int = 20,
        willingness_to_hire: float = 0.6,
        sector: str = "services",
        description: str = "",
        location: tuple = (0, 0)
    ):
        """
        Initialize Business agent.

        Args:
            agent_id: Unique identifier
            company_size: Total number of employees
            willingness_to_hire: Propensity to hire youth/NEETs (0-1)
            sector: Business sector (manufacturing, services, retail, etc.)
            description: Business description
            location: Geographic location (x, y coordinates)
        """
        super().__init__(agent_id=agent_id, agent_type='business')

        # Core attributes (from specification Section 2.2)
        self.company_size = max(1, company_size)
        self.willingness_to_hire = max(0.0, min(1.0, willingness_to_hire))
        self.sector = sector.lower()
        self.description = description
        self.location = location

        # Capacity calculation (from spec: floor(company_size / 5))
        self.capacity_ceiling = self.company_size // 5

        # Apprentice tracking
        self.current_apprentices = 0
        self.apprentice_records: List[Dict[str, Any]] = []

        # Hiring history
        self.total_hires = 0
        self.total_graduations = 0

    def step(self, month: int, context: Dict[str, Any]):
        """
        Execute monthly step for Business agent.

        Args:
            month: Current simulation month
            context: Simulation context
        """
        # Check for apprentice graduations (24 months)
        self._check_graduations(month)

    def can_hire(self) -> bool:
        """
        Check if business has capacity to hire another apprentice.

        Returns:
            True if under capacity ceiling
        """
        return self.current_apprentices < self.capacity_ceiling

    def get_available_capacity(self) -> int:
        """
        Get number of additional apprentices that can be hired.

        Returns:
            Available capacity
        """
        return max(0, self.capacity_ceiling - self.current_apprentices)

    def hire_apprentice(self, neet_id: str, month: int) -> bool:
        """
        Hire a NEET as an apprentice.

        Args:
            neet_id: ID of NEET to hire
            month: Current month

        Returns:
            True if hire successful, False if at capacity
        """
        if not self.can_hire():
            return False

        # Add to apprentice records
        self.apprentice_records.append({
            'neet_id': neet_id,
            'start_month': month,
            'expected_graduation_month': month + 24,
            'graduated': False
        })

        self.current_apprentices += 1
        self.total_hires += 1

        self.log_interaction(
            month=month,
            interaction_type='hired',
            target_agent_id=neet_id,
            details={'current_apprentices': self.current_apprentices}
        )

        return True

    def graduate_apprentice(self, neet_id: str, month: int) -> bool:
        """
        Graduate an apprentice after 24 months.

        Frees up capacity for new hires.

        Args:
            neet_id: ID of NEET graduating
            month: Current month

        Returns:
            True if graduation successful
        """
        # Find the apprentice record
        for record in self.apprentice_records:
            if record['neet_id'] == neet_id and not record['graduated']:
                record['graduated'] = True
                record['graduation_month'] = month

                self.current_apprentices -= 1
                self.total_graduations += 1

                self.log_interaction(
                    month=month,
                    interaction_type='graduated',
                    target_agent_id=neet_id,
                    details={
                        'months_employed': month - record['start_month'],
                        'current_apprentices': self.current_apprentices
                    }
                )

                return True

        return False

    def _check_graduations(self, month: int):
        """
        Check if any apprentices should graduate this month.

        Args:
            month: Current month
        """
        for record in self.apprentice_records:
            if not record['graduated'] and month >= record['expected_graduation_month']:
                self.graduate_apprentice(record['neet_id'], month)

    def get_capacity_ratio(self) -> float:
        """
        Get ratio of current apprentices to capacity.

        Returns:
            Ratio from 0 (empty) to 1 (full)
        """
        if self.capacity_ceiling == 0:
            return 1.0
        return self.current_apprentices / self.capacity_ceiling

    def get_capacity_cushion(self) -> float:
        """
        Get capacity cushion (inverse of ratio).

        Used in hiring probability calculation.

        Returns:
            Cushion from 0 (full) to 1 (empty)
        """
        return 1.0 - self.get_capacity_ratio()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize Business agent to dictionary.

        Returns:
            Complete agent state
        """
        base_dict = super().to_dict()

        business_dict = {
            'company_size': self.company_size,
            'willingness_to_hire': round(self.willingness_to_hire, 3),
            'sector': self.sector,
            'description': self.description,
            'location': self.location,
            'capacity_ceiling': self.capacity_ceiling,
            'current_apprentices': self.current_apprentices,
            'available_capacity': self.get_available_capacity(),
            'capacity_ratio': round(self.get_capacity_ratio(), 3),
            'total_hires': self.total_hires,
            'total_graduations': self.total_graduations,
            'active_apprentice_records': len([r for r in self.apprentice_records if not r['graduated']])
        }

        return {**base_dict, **business_dict}

    def __repr__(self) -> str:
        return (
            f"BusinessAgent(id={self.id}, sector={self.sector}, "
            f"size={self.company_size}, apprentices={self.current_apprentices}/{self.capacity_ceiling})"
        )
