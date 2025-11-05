"""
Main simulation engine implementing the monthly loop.

From specification Section 4.1.
"""

import random
from typing import Dict, Any, List, Optional
from ..agents import NEETAgent, BusinessAgent, AgentFactory, EmploymentStatus
from ..matching import filter_viable_matches, match_neets_to_businesses
from ..llm import LLMClient, ProfileGenerator


class SimulationEngine:
    """
    Core simulation engine that runs the ABM.

    Implements the monthly simulation loop from specification Section 4.1.
    """

    def __init__(
        self,
        num_neets: int = 10,
        num_businesses: int = 5,
        duration_months: int = 12,
        random_seed: Optional[int] = None,
        use_llm_profiles: bool = False,
        llm_client: Optional[LLMClient] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize simulation engine.

        Args:
            num_neets: Number of NEET agents
            num_businesses: Number of business agents
            duration_months: Simulation length in months
            random_seed: Random seed for reproducibility
            use_llm_profiles: Whether to use LLM for profile generation
            llm_client: LLM client (required if use_llm_profiles=True)
            config: Additional configuration parameters
        """
        self.num_neets = num_neets
        self.num_businesses = num_businesses
        self.duration_months = duration_months
        self.current_month = 0

        # Set random seed for reproducibility
        if random_seed is not None:
            random.seed(random_seed)

        # Configuration
        self.config = config or self._default_config()

        # Initialize LLM profile generator if needed
        self.use_llm_profiles = use_llm_profiles
        if use_llm_profiles:
            if llm_client is None:
                # Default to mock LLM
                llm_client = LLMClient(provider='mock')
            self.profile_generator = ProfileGenerator(llm_client, use_llm=True)
        else:
            self.profile_generator = ProfileGenerator(LLMClient(provider='mock'), use_llm=False)

        # Initialize agents
        self.neets: List[NEETAgent] = []
        self.businesses: List[BusinessAgent] = []
        self._initialize_agents()

        # Metrics storage
        self.monthly_metrics = []

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration parameters"""
        return {
            # Counseling parameters
            'counseling_budget': 50000,  # Monthly budget
            'counseling_intensity': 0.12,  # Effect intensity

            # Subsidy parameters
            'subsidy_available': True,
            'subsidy_effectiveness': 0.5,  # 0.3-1.0 range

            # Matching parameters
            'skill_threshold': 0.4,
            'transportation_floor': 0.6,
            'min_business_willingness': 0.5,
            'max_attempts_per_neet': 3,

            # Geographic parameters
            'region_size': 50,  # Grid size for locations
        }

    def _initialize_agents(self):
        """Initialize all agents using LLM or random profiles"""
        print(f"Initializing {self.num_neets} NEETs and {self.num_businesses} businesses...")

        # Generate NEET profiles
        neet_profiles = self.profile_generator.generate_batch(
            agent_type='neet',
            count=self.num_neets
        )

        # Create NEET agents
        for i, profile in enumerate(neet_profiles):
            # Random location within region
            location = (
                random.uniform(0, self.config['region_size']),
                random.uniform(0, self.config['region_size'])
            )

            neet = AgentFactory.create(
                agent_type='neet',
                agent_id=f'neet_{i}',
                willingness_to_work=profile['willingness_to_work'],
                impeding_factors=profile['impeding_factors'],
                skill_level=profile['skill_level'],
                age=profile.get('age', 22),
                background=profile.get('background', ''),
                location=location
            )
            self.neets.append(neet)

        # Generate Business profiles
        business_profiles = self.profile_generator.generate_batch(
            agent_type='business',
            count=self.num_businesses
        )

        # Create Business agents
        for i, profile in enumerate(business_profiles):
            # Random location within region
            location = (
                random.uniform(0, self.config['region_size']),
                random.uniform(0, self.config['region_size'])
            )

            business = AgentFactory.create(
                agent_type='business',
                agent_id=f'business_{i}',
                company_size=profile['company_size'],
                willingness_to_hire=profile['willingness_to_hire'],
                sector=profile['sector'],
                description=profile.get('description', ''),
                location=location
            )
            self.businesses.append(business)

        print(f"✓ Initialized {len(self.neets)} NEETs and {len(self.businesses)} businesses")

    def run(self) -> List[Dict[str, Any]]:
        """
        Run the full simulation.

        Returns:
            List of monthly metrics
        """
        print(f"\nRunning simulation for {self.duration_months} months...\n")

        for month in range(self.duration_months):
            self.current_month = month
            metrics = self.step_month(month)
            self.monthly_metrics.append(metrics)

            # Print progress
            if (month + 1) % 3 == 0 or month == 0:
                print(f"Month {month + 1}: Employment rate = {metrics['employment_rate']:.1%}, "
                      f"Placements = {metrics['placements_this_month']}")

        print(f"\n✓ Simulation complete!")
        return self.monthly_metrics

    def step_month(self, month: int) -> Dict[str, Any]:
        """
        Execute one month of simulation.

        Implements the monthly loop from specification Section 4.1.

        Args:
            month: Current month number

        Returns:
            Metrics for this month
        """
        # Phase 1: Counseling allocation and effects
        self._phase_counseling(month)

        # Phase 2: Job matching
        matching_stats = self._phase_job_matching(month)

        # Phase 3: Attribute updates for employed NEETs
        self._phase_attribute_updates(month)

        # Phase 4: Check for graduations
        self._phase_graduations(month)

        # Phase 5: Agent step calls
        self._phase_agent_steps(month)

        # Phase 6: Collect metrics
        metrics = self._collect_metrics(month, matching_stats)

        return metrics

    def _phase_counseling(self, month: int):
        """
        Phase 1: Allocate counseling and apply effects.

        Simplified implementation: provide counseling to NEETs with highest impeding factors.
        """
        counseling_budget = self.config['counseling_budget']
        counseling_intensity = self.config['counseling_intensity']

        # Assume cost per NEET per month
        cost_per_neet = 500
        max_neets_in_counseling = int(counseling_budget / cost_per_neet)

        # Select NEETs for counseling (prioritize high impeding factors)
        available_neets = [n for n in self.neets if n.employment_status == EmploymentStatus.NEET]
        available_neets.sort(key=lambda n: n.impeding_factors, reverse=True)

        neets_to_counsel = available_neets[:max_neets_in_counseling]

        # Apply counseling effects
        for neet in neets_to_counsel:
            if not neet.in_counseling:
                neet.enroll_in_counseling(month, 'general')

            neet.apply_counseling_effects(counseling_intensity)

    def _phase_job_matching(self, month: int) -> Dict[str, Any]:
        """
        Phase 2: Match NEETs to businesses and process hiring.

        Returns:
            Matching statistics
        """
        # Get available NEETs
        available_neets = [n for n in self.neets if n.employment_status == EmploymentStatus.NEET]

        # Get businesses with capacity
        available_businesses = [b for b in self.businesses if b.can_hire()]

        if not available_neets or not available_businesses:
            return {
                'total_attempts': 0,
                'successful_hires': 0,
                'neets_hired': 0,
                'success_rate': 0.0
            }

        # Filter viable matches based on constraints
        viable_matches = filter_viable_matches(
            neets=available_neets,
            businesses=available_businesses,
            skill_threshold=self.config['skill_threshold'],
            transportation_floor=self.config['transportation_floor'],
            min_business_willingness=self.config['min_business_willingness'],
            subsidy_available=self.config['subsidy_available']
        )

        # Attempt matches
        matching_stats = match_neets_to_businesses(
            viable_matches=viable_matches,
            month=month,
            subsidy_available=self.config['subsidy_available'],
            subsidy_effectiveness=self.config['subsidy_effectiveness'],
            max_attempts_per_neet=self.config['max_attempts_per_neet']
        )

        return matching_stats

    def _phase_attribute_updates(self, month: int):
        """
        Phase 3: Update attributes for employed NEETs.

        From specification Section 6.1:
        - skill_level += 0.02
        - willingness_to_work += 0.01
        - impeding_factors -= 0.015
        """
        for neet in self.neets:
            if neet.employment_status == EmploymentStatus.EMPLOYED:
                neet.update_attributes_while_employed()

    def _phase_graduations(self, month: int):
        """
        Phase 4: Check for apprentice graduations (24 months).
        """
        for business in self.businesses:
            business.step(month, {})

        for neet in self.neets:
            neet.step(month, {})

    def _phase_agent_steps(self, month: int):
        """
        Phase 5: Call step() on all agents for any additional logic.
        """
        # Already called in _phase_graduations, but kept as separate phase for clarity
        pass

    def _collect_metrics(self, month: int, matching_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 6: Collect metrics for this month.

        Args:
            month: Current month
            matching_stats: Statistics from job matching phase

        Returns:
            Dictionary of metrics
        """
        total_neets = len(self.neets)
        employed_neets = sum(1 for n in self.neets if n.employment_status == EmploymentStatus.EMPLOYED)
        trained_out_neets = sum(1 for n in self.neets if n.employment_status == EmploymentStatus.TRAINED_OUT)
        unemployed_neets = total_neets - employed_neets - trained_out_neets

        neets_in_counseling = sum(1 for n in self.neets if n.in_counseling)

        # Calculate average attributes
        avg_willingness = sum(n.willingness_to_work for n in self.neets) / total_neets
        avg_skill = sum(n.skill_level for n in self.neets) / total_neets
        avg_impeding_factors = sum(n.impeding_factors for n in self.neets) / total_neets

        # Business metrics
        total_capacity = sum(b.capacity_ceiling for b in self.businesses)
        used_capacity = sum(b.current_apprentices for b in self.businesses)

        return {
            'month': month,
            'employment_rate': employed_neets / total_neets,
            'employed_count': employed_neets,
            'unemployed_count': unemployed_neets,
            'trained_out_count': trained_out_neets,
            'placements_this_month': matching_stats['successful_hires'],
            'job_applications': matching_stats['total_attempts'],
            'neets_in_counseling': neets_in_counseling,
            'avg_willingness': avg_willingness,
            'avg_skill_level': avg_skill,
            'avg_impeding_factors': avg_impeding_factors,
            'business_capacity_used': used_capacity,
            'business_capacity_total': total_capacity,
            'business_capacity_rate': used_capacity / total_capacity if total_capacity > 0 else 0,
        }

    def get_final_report(self) -> Dict[str, Any]:
        """
        Generate final simulation report.

        Returns:
            Summary statistics
        """
        if not self.monthly_metrics:
            return {}

        final_metrics = self.monthly_metrics[-1]
        initial_metrics = self.monthly_metrics[0]

        total_placements = sum(m['placements_this_month'] for m in self.monthly_metrics)
        total_applications = sum(m['job_applications'] for m in self.monthly_metrics)

        return {
            'simulation_length_months': self.duration_months,
            'num_neets': self.num_neets,
            'num_businesses': self.num_businesses,
            'used_llm_profiles': self.use_llm_profiles,

            # Final outcomes
            'final_employment_rate': final_metrics['employment_rate'],
            'final_employed_count': final_metrics['employed_count'],
            'final_trained_out_count': final_metrics['trained_out_count'],

            # Aggregate statistics
            'total_placements': total_placements,
            'total_applications': total_applications,
            'overall_success_rate': total_placements / total_applications if total_applications > 0 else 0,

            # Attribute changes
            'avg_willingness_change': final_metrics['avg_willingness'] - initial_metrics['avg_willingness'],
            'avg_skill_change': final_metrics['avg_skill_level'] - initial_metrics['avg_skill_level'],
            'avg_impeding_factors_change': final_metrics['avg_impeding_factors'] - initial_metrics['avg_impeding_factors'],

            # Configuration
            'config': self.config
        }
