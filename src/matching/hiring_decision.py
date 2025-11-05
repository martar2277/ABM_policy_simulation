"""
Hiring decision probability calculation.

From specification Section 4.3.
"""

import random
from .constraints import compute_skill_match, compute_distance, compute_transportation_accessibility


def compute_hiring_probability(
    neet,
    business,
    job_skill_requirement: float = 0.5,
    subsidy_available: bool = False,
    subsidy_effectiveness: float = 1.0,
    base_probability_threshold: float = 0.5,
    high_probability_range: tuple = (0.8, 1.0)
) -> float:
    """
    Calculate probability that business will hire NEET.

    Implements specification Section 4.3.

    All hard constraints must already be passed before calling this function.
    This computes the SOFT probability based on multiple factors.

    Args:
        neet: NEET agent
        business: Business agent
        job_skill_requirement: Required skill level for job (0-1)
        subsidy_available: Whether wage subsidy is available
        subsidy_effectiveness: Subsidy multiplier effect (0.3-1.0)
        base_probability_threshold: Threshold for high probability band
        high_probability_range: Range for high probability (min, max)

    Returns:
        Hiring probability (0-1)
    """
    # Component 1: Skill match quality (0-1)
    skill_match = compute_skill_match(neet.skill_level, job_skill_requirement)

    # Component 2: Transportation accessibility (0-1)
    distance = compute_distance(neet.location, business.location)
    transportation_accessibility = compute_transportation_accessibility(distance)

    # Component 3: Business willingness (0-1)
    business_willingness = business.willingness_to_hire

    # Component 4: Subsidy boost
    if subsidy_available:
        subsidy_multiplier = 1.0 + (subsidy_effectiveness * 0.3)  # Up to 30% boost
    else:
        subsidy_multiplier = 1.0

    # Component 5: Capacity cushion (soft factor)
    capacity_cushion = business.get_capacity_cushion()

    # Component 6: NEET willingness to work
    neet_willingness = neet.willingness_to_work

    # Composite base probability (multiply all factors)
    base_probability = (
        skill_match *
        transportation_accessibility *
        business_willingness *
        capacity_cushion *
        neet_willingness *
        subsidy_multiplier
    )

    # Apply threshold logic from specification
    if base_probability >= base_probability_threshold:
        # High confidence match - use high probability band
        hiring_probability = random.uniform(*high_probability_range)
    else:
        # Lower confidence - use base probability with some randomness
        hiring_probability = base_probability * random.uniform(0.8, 1.2)
        hiring_probability = max(0.0, min(1.0, hiring_probability))

    return hiring_probability


def attempt_hire(
    neet,
    business,
    month: int,
    job_skill_requirement: float = 0.5,
    subsidy_available: bool = False,
    subsidy_effectiveness: float = 1.0
) -> bool:
    """
    Attempt to hire NEET by business.

    Calculates probability and makes random decision.

    Args:
        neet: NEET agent
        business: Business agent
        month: Current simulation month
        job_skill_requirement: Job skill requirement
        subsidy_available: Whether subsidy is available
        subsidy_effectiveness: Subsidy effectiveness multiplier

    Returns:
        True if hire successful, False otherwise
    """
    probability = compute_hiring_probability(
        neet=neet,
        business=business,
        job_skill_requirement=job_skill_requirement,
        subsidy_available=subsidy_available,
        subsidy_effectiveness=subsidy_effectiveness
    )

    # Make random decision based on probability
    if random.random() < probability:
        # Hire successful
        neet.get_hired(business.id, month)
        business.hire_apprentice(neet.id, month)
        return True

    return False


def match_neets_to_businesses(
    viable_matches,
    month: int,
    subsidy_available: bool = False,
    subsidy_effectiveness: float = 1.0,
    max_attempts_per_neet: int = 3
):
    """
    Match NEETs to businesses from list of viable matches.

    Each NEET attempts to match with businesses until hired or max attempts reached.

    Args:
        viable_matches: List of (neet, business) tuples that passed constraints
        month: Current simulation month
        subsidy_available: Whether subsidy is available
        subsidy_effectiveness: Subsidy effectiveness
        max_attempts_per_neet: Max job applications per NEET per month

    Returns:
        Dictionary with matching statistics
    """
    # Group matches by NEET
    neet_matches = {}
    for neet, business in viable_matches:
        if neet.id not in neet_matches:
            neet_matches[neet.id] = []
        neet_matches[neet.id].append((neet, business))

    total_attempts = 0
    successful_hires = 0
    neets_hired = set()

    # Process each NEET
    for neet_id, matches in neet_matches.items():
        if len(matches) == 0:
            continue

        # Shuffle to randomize which businesses are tried
        random.shuffle(matches)

        # Try up to max_attempts_per_neet businesses
        attempts = 0
        for neet, business in matches:
            if attempts >= max_attempts_per_neet:
                break

            # Skip if already hired
            if neet_id in neets_hired:
                break

            # Skip if business no longer has capacity
            if not business.can_hire():
                continue

            # Record application
            neet.apply_for_job(
                job_id=f"job_{business.id}",
                business_id=business.id,
                month=month
            )

            # Attempt hire
            total_attempts += 1
            attempts += 1

            success = attempt_hire(
                neet=neet,
                business=business,
                month=month,
                subsidy_available=subsidy_available,
                subsidy_effectiveness=subsidy_effectiveness
            )

            if success:
                successful_hires += 1
                neets_hired.add(neet_id)
                break  # NEET is hired, stop trying other businesses

    return {
        'total_attempts': total_attempts,
        'successful_hires': successful_hires,
        'neets_hired': len(neets_hired),
        'success_rate': successful_hires / total_attempts if total_attempts > 0 else 0.0
    }
