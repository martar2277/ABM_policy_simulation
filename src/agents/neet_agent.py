"""
NEET (Not in Education, Employment, or Training) agent implementation.
"""

from typing import Dict, Any, Optional
from enum import Enum
from .base_agent import BaseAgent


class EmploymentStatus(Enum):
    """Employment status for NEET agents"""
    NEET = "NEET"                    # Not employed, not in training
    EMPLOYED = "EMPLOYED"            # Currently employed
    TRAINED_OUT = "TRAINED_OUT"      # Graduated from apprenticeship


class NEETAgent(BaseAgent):
    """
    NEET agent representing a youth not in education, employment, or training.

    Attributes match the specification in the ABM guide (Section 2.1).
    """

    def __init__(
        self,
        agent_id: str,
        willingness_to_work: float = 0.5,
        impeding_factors: float = 0.5,
        skill_level: float = 0.5,
        age: int = 22,
        background: str = "",
        location: tuple = (0, 0)
    ):
        """
        Initialize NEET agent.

        Args:
            agent_id: Unique identifier
            willingness_to_work: Motivation to seek employment (0-1)
            impeding_factors: Constraints/barriers to employment (0-1)
            skill_level: Job readiness and technical capability (0-1)
            age: Age in years
            background: Background story/description
            location: Geographic location (x, y coordinates)
        """
        super().__init__(agent_id=agent_id, agent_type='neet')

        # Core attributes (from specification Section 2.1)
        self.willingness_to_work = max(0.0, min(1.0, willingness_to_work))
        self.impeding_factors = max(0.0, min(1.0, impeding_factors))
        self.skill_level = max(0.0, min(1.0, skill_level))

        # Additional attributes
        self.age = age
        self.background = background
        self.location = location

        # State tracking
        self.employment_status = EmploymentStatus.NEET
        self.months_employed = 0
        self.current_employer_id: Optional[str] = None

        # Store initial values for tracking change
        self.initial_willingness = willingness_to_work
        self.initial_impeding_factors = impeding_factors
        self.initial_skill_level = skill_level

        # Intervention tracking
        self.in_counseling = False
        self.counseling_history = []
        self.job_applications = []

    def step(self, month: int, context: Dict[str, Any]):
        """
        Execute monthly step for NEET agent.

        This is called by the simulation engine each month.

        Args:
            month: Current simulation month
            context: Simulation context
        """
        # Update employment duration if employed
        if self.employment_status == EmploymentStatus.EMPLOYED:
            self.months_employed += 1

        # Check for graduation (24 months)
        if self.months_employed >= 24:
            self.graduate_from_apprenticeship(month)

    def apply_for_job(self, job_id: str, business_id: str, month: int):
        """
        Record a job application.

        Args:
            job_id: Job identifier
            business_id: Business identifier
            month: Month of application
        """
        self.job_applications.append({
            'month': month,
            'job_id': job_id,
            'business_id': business_id
        })

    def get_hired(self, employer_id: str, month: int):
        """
        Transition to employed status.

        Args:
            employer_id: ID of hiring business
            month: Month of hire
        """
        self.employment_status = EmploymentStatus.EMPLOYED
        self.current_employer_id = employer_id
        self.months_employed = 0

        self.log_interaction(
            month=month,
            interaction_type='hired',
            target_agent_id=employer_id,
            details={'status': 'EMPLOYED'}
        )

    def graduate_from_apprenticeship(self, month: int):
        """
        Graduate from apprenticeship after 24 months.

        Frees up employer capacity.

        Args:
            month: Month of graduation
        """
        previous_employer = self.current_employer_id

        self.employment_status = EmploymentStatus.TRAINED_OUT
        self.current_employer_id = None

        if previous_employer:
            self.log_interaction(
                month=month,
                interaction_type='graduated',
                target_agent_id=previous_employer,
                details={'months_employed': self.months_employed}
            )

    def update_attributes_while_employed(self):
        """
        Monthly attribute updates for employed NEETs.

        From specification Section 6.1:
        - skill_level += 0.02
        - willingness_to_work += 0.01
        - impeding_factors -= 0.015
        """
        if self.employment_status == EmploymentStatus.EMPLOYED:
            self.skill_level = min(1.0, self.skill_level + 0.02)
            self.willingness_to_work = min(1.0, self.willingness_to_work + 0.01)
            self.impeding_factors = max(0.0, self.impeding_factors - 0.015)

    def apply_counseling_effects(self, counseling_intensity: float):
        """
        Apply counseling effects for this month.

        From specification Section 6.1:
        - impeding_factors -= counseling_intensity × 0.10
        - willingness_to_work += counseling_intensity × 0.10

        Args:
            counseling_intensity: Intensity of counseling (0-1)
        """
        self.impeding_factors = max(0.0, self.impeding_factors - (counseling_intensity * 0.10))
        self.willingness_to_work = min(1.0, self.willingness_to_work + (counseling_intensity * 0.10))

    def enroll_in_counseling(self, month: int, counseling_type: str):
        """
        Enroll NEET in counseling service.

        Args:
            month: Current month
            counseling_type: Type of counseling (e.g., 'mental_health', 'job_matching')
        """
        self.in_counseling = True
        self.counseling_history.append({
            'month': month,
            'type': counseling_type,
            'status': 'enrolled'
        })

    def exit_counseling(self, month: int):
        """
        Exit counseling service.

        Args:
            month: Current month
        """
        self.in_counseling = False
        if self.counseling_history:
            self.counseling_history[-1]['exit_month'] = month

    def get_attribute_changes(self) -> Dict[str, float]:
        """
        Calculate how much attributes have changed since initialization.

        Returns:
            Dictionary with attribute changes
        """
        return {
            'willingness_change': self.willingness_to_work - self.initial_willingness,
            'impeding_factors_change': self.impeding_factors - self.initial_impeding_factors,
            'skill_change': self.skill_level - self.initial_skill_level
        }

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize NEET agent to dictionary.

        Returns:
            Complete agent state
        """
        base_dict = super().to_dict()

        neet_dict = {
            'willingness_to_work': round(self.willingness_to_work, 3),
            'impeding_factors': round(self.impeding_factors, 3),
            'skill_level': round(self.skill_level, 3),
            'age': self.age,
            'background': self.background,
            'location': self.location,
            'employment_status': self.employment_status.value,
            'months_employed': self.months_employed,
            'current_employer_id': self.current_employer_id,
            'in_counseling': self.in_counseling,
            'total_applications': len(self.job_applications),
            'attribute_changes': self.get_attribute_changes()
        }

        return {**base_dict, **neet_dict}

    def __repr__(self) -> str:
        return (
            f"NEETAgent(id={self.id}, status={self.employment_status.value}, "
            f"willingness={self.willingness_to_work:.2f}, "
            f"skill={self.skill_level:.2f})"
        )
