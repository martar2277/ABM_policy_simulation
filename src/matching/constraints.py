"""
Matching constraints - hard floor rules for job matching.

From specification Section 4.2.
"""

import math
from typing import Tuple


def compute_distance(loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
    """
    Compute Euclidean distance between two locations.

    Args:
        loc1: First location (x, y)
        loc2: Second location (x, y)

    Returns:
        Distance in kilometers
    """
    x1, y1 = loc1
    x2, y2 = loc2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def compute_transportation_accessibility(
    distance: float,
    max_viable_distance: float = 50.0
) -> float:
    """
    Calculate transportation accessibility score based on distance.

    From specification Section 3.2:
    accessibility = max(0, 1 - distance / max_viable_distance)

    Args:
        distance: Distance in kilometers
        max_viable_distance: Maximum distance considered viable

    Returns:
        Accessibility score (0-1)
    """
    if distance <= 0:
        return 1.0

    accessibility = max(0.0, 1.0 - distance / max_viable_distance)
    return accessibility


def compute_skill_match(
    neet_skill: float,
    job_skill_requirement: float
) -> float:
    """
    Calculate how well NEET skills match job requirements.

    Returns a score from 0 (no match) to 1 (perfect match).

    Args:
        neet_skill: NEET's skill level (0-1)
        job_skill_requirement: Job's skill requirement (0-1)

    Returns:
        Match quality (0-1)
    """
    # Skills within 0.2 are considered a good match
    # Skills further apart reduce match quality
    diff = abs(neet_skill - job_skill_requirement)

    if diff <= 0.2:
        return 1.0
    elif diff >= 0.6:
        return 0.0
    else:
        # Linear decay between 0.2 and 0.6
        return 1.0 - ((diff - 0.2) / 0.4)


def can_attempt_match(
    neet,
    business,
    skill_threshold: float = 0.4,
    transportation_floor: float = 0.6,
    min_business_willingness: float = 0.5,
    subsidy_available: bool = False,
    subsidy_required: bool = False
) -> bool:
    """
    Check if NEET-Business match can be attempted.

    Implements hard constraints from specification Section 4.2.

    Args:
        neet: NEET agent
        business: Business agent
        skill_threshold: Minimum skill match required
        transportation_floor: Minimum transportation accessibility
        min_business_willingness: Minimum business willingness to hire
        subsidy_available: Whether subsidy is available
        subsidy_required: Whether subsidy is required for this match

    Returns:
        True if all hard constraints pass
    """
    # Hard floor: NEET must be available (not already employed)
    if neet.employment_status.value != 'NEET':
        return False

    # Hard floor: Business must have capacity
    if not business.can_hire():
        return False

    # Hard floor: Business willingness must be sufficient
    if business.willingness_to_hire < min_business_willingness:
        return False

    # Hard floor: Skill match threshold
    skill_match = compute_skill_match(neet.skill_level, 0.5)  # Default job requirement
    if skill_match < skill_threshold:
        return False

    # Hard floor: Transportation must be viable (>= 0.6)
    distance = compute_distance(neet.location, business.location)
    transportation_score = compute_transportation_accessibility(distance)
    if transportation_score < transportation_floor:
        return False

    # Subsidy constraint
    if subsidy_required and not subsidy_available:
        return False

    # All hard constraints passed
    return True


def filter_viable_matches(neets, businesses, **constraint_params):
    """
    Filter NEET-Business pairs to only viable matches.

    Args:
        neets: List of NEET agents
        businesses: List of Business agents
        **constraint_params: Parameters for can_attempt_match

    Returns:
        List of (neet, business) tuples that pass constraints
    """
    viable_matches = []

    for neet in neets:
        for business in businesses:
            if can_attempt_match(neet, business, **constraint_params):
                viable_matches.append((neet, business))

    return viable_matches
