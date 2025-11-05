# ABM-Based Intervention Effects Simulation Model: Programmer's Guide

## Executive Summary

This guide specifies an agent-based model (ABM) for simulating the effects of social policy interventions on youth employment outcomes. The model focuses on NEETs (Not in Education, Employment, or Training) and businesses, with two primary policy levers: counseling services and wage subsidies.

**Scope:** Month-by-month simulation, starting with 10 NEETs and 5 businesses, extendable to larger populations to test for emergence of population-level dynamics.

---

## 1. Model Architecture Overview

### Core Components

1. **Agent Types:** NEETs and Businesses
2. **System Variables:** Environmental/policy parameters affecting all agents
3. **Simulation Loop:** Monthly cycle processing job matching, counseling effects, attribute updates
4. **Policy Interventions:** Counseling availability and wage subsidy levels (variable over time)
5. **Outcomes:** Employment transitions, placement rates, cost-effectiveness metrics

### Time Horizon

- **Time step:** 1 month
- **Simulation length:** 12–36 months (configurable for testing)
- **Typical runs:** 100 independent simulations per policy scenario to capture outcome distributions

---

## 2. Agent Specifications

### 2.1 NEET Agent

**Core Attributes:**

| Attribute | Type | Range | Description |
|-----------|------|-------|-------------|
| `willingness_to_work` | float | 0–1 | Motivation to seek employment |
| `impeding_factors` | float | 0–1 | Constraints (e.g., transportation barriers, caring responsibilities) |
| `skill_level` | float | 0–1 | Job readiness and technical capability |
| `employment_status` | enum | {NEET, EMPLOYED, TRAINED_OUT} | Current state |
| `months_employed` | int | 0–∞ | Duration in current role |
| `current_employer_id` | int or None | — | Reference to employing business |

**Initialization:**

- Randomly assign attributes from distributions (e.g., uniform, normal) to reflect heterogeneity
- All NEETs start as NEET with `months_employed = 0`
- Store initial values for tracking change over time

**State Transitions:**

1. `NEET → EMPLOYED`: Successful job match (see Section 3.2)
2. `EMPLOYED → TRAINED_OUT`: After 24 months in same role (graduates, frees employer capacity)
3. `EMPLOYED → NEET`: Optional—unemployment if business fails or other shocks (omit in first iteration)

### 2.2 Business Agent

**Core Attributes:**

| Attribute | Type | Range | Description |
|-----------|------|-------|-------------|
| `company_size` | int | 1–∞ | Total number of employees |
| `willingness_to_hire` | float | 0–1 | Propensity to hire youth/NEETs |
| `current_apprentices` | int | 0–capacity_ceiling | Active hired NEETs/youth |
| `apprentice_records` | list | — | Track hire date, NEET_id, expected graduation date |
| `sector` | string | e.g., "manufacturing", "services", "retail" | Affects subsidy eligibility and job types |

**Capacity Ceiling Calculation:**

```
capacity_ceiling = floor(company_size / 5)
```

For example: 10-person company → max 2 apprentices; 50-person company → max 10 apprentices.

**Apprentice Graduation:**

When an apprentice reaches 24 months in role, they are removed from `current_apprentices`, freeing capacity for new hires.

---

## 3. System Variables (Policy & Environment)

### 3.1 Job Market

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| `total_jobs` | int | 1–∞ | Total number of job opportunities in the environment |
| `job_quality_distribution` | list of floats | 0–1 | Distribution of skill requirements for available jobs |

**Implementation note:** Jobs can be represented as a pool with attributes: `skill_requirement`, `sector`, `employer_id`.

### 3.2 Transportation Infrastructure

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| `transportation_accessibility[distance]` | float | 0–1 | Accessibility score as a function of distance (km) |

**Hard Floor Rule:**

- If `transportation_accessibility < 0.6` for any NEET-job pair, that match is blocked.
- Accessibility decreases with distance; can be modeled as: `accessibility = max(0, 1 - distance / max_viable_distance)`

**Example:** 35 km distance with public transport running 2x/day might yield `accessibility = 0.2` (hard-blocked). 0.5 km might yield `accessibility = 0.95` (passes threshold).

### 3.3 Counseling Services

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| `counseling_availability_budget` | float | 0–∞ | Total resource available for counseling (varies monthly) |
| `counseling_types` | dict | — | Types and parameters: `mental_health`, `job_matching`, `disability_support`, `educational`, `other` |
| `counseling_intensity[type]` | float | 0–1 | Intensity/quality level for each counseling type |
| `neets_in_counseling` | set or list | — | NEETs currently receiving counseling |

**Counseling Effects:**

For each NEET in counseling targeting their needs:
- **Reduces impeding_factors:** `impeding_factors -= effect_intensity × 0.1` (per month, example)
- **Increases willingness:** `willingness_to_work += effect_intensity × 0.1` (per month)

**Allocation Rule:** At the start of each month, counseling budget determines how many NEETs can receive services and at what intensity. This is a **policy input** that varies over simulation runs.

### 3.4 Wage Subsidy

| Variable | Type | Range | Description |
|----------|------|-------|-------------|
| `subsidy_available` | bool | True/False | Whether subsidy program is active |
| `subsidy_amount` | float | 0–∞ | Subsidy value (varies by sector and apprenticeship type) |
| `subsidy_minimum` | float | 0–1 | Minimum subsidy effectiveness (floor) |
| `subsidy_maximum` | float | 0.3–1.0 | Maximum subsidy effectiveness (cap, typically 1.0) |
| `subsidy_by_sector` | dict | sector → subsidy_amount | Subsidy can vary by economic sector |

**Subsidy Effect in Hiring Decision (see Section 3.2 for details):**

Subsidy acts as a multiplier on business hiring probability if `subsidy_available = True` and the NEET-job pair qualifies.

---

## 4. Core Simulation Loop (Monthly)

### 4.1 Step-by-Step Pseudocode

```
FOR each month in simulation:
    
    # Step 1: Counseling Allocation
    allocate_counseling_services(
        available_budget = counseling_availability_budget[month],
        target_neets = available_neets,
        counseling_types = active_interventions
    )
    
    # Step 2: Update Counseling Effects
    FOR each neet in neets_in_counseling:
        if neet.impeding_factors > 0:
            neet.impeding_factors -= counseling_intensity × effect_per_type
        if neet.willingness_to_work < 1.0:
            neet.willingness_to_work += counseling_intensity × effect_per_type
    
    # Step 3: Refresh Job Pool
    available_jobs = generate_or_refresh_job_pool(total_jobs, job_quality_distribution)
    
    # Step 4: Job Matching and Hiring Decisions
    FOR each (neet, job) in available_matches:
        if can_attempt_match(neet, job):
            hiring_probability = compute_hiring_decision(neet, job)
            if random() < hiring_probability:
                hire(neet, job)
                neet.employment_status = EMPLOYED
                neet.current_employer_id = job.employer_id
                neet.months_employed = 0
                employer.current_apprentices += 1
                employer.apprentice_records.append({neet_id, start_month})
    
    # Step 5: Check for Apprentice Graduations
    FOR each employer in businesses:
        FOR each apprentice_record in employer.apprentice_records:
            if current_month - apprentice_record.start_month >= 24:
                graduate_apprentice(apprentice_record.neet_id)
                employer.current_apprentices -= 1
                employer.apprentice_records.remove(apprentice_record)
    
    # Step 6: Update Employed NEET Attributes (Gradual Improvement)
    FOR each neet with employment_status == EMPLOYED:
        neet.months_employed += 1
        # Gradual skill improvement
        neet.skill_level = min(1.0, neet.skill_level + 0.02)
        # Willingness increase
        neet.willingness_to_work = min(1.0, neet.willingness_to_work + 0.01)
        # Barriers reduction (especially transportation through income)
        neet.impeding_factors = max(0, neet.impeding_factors - 0.015)
    
    # Step 7: Compute Month-End Metrics
    employment_rate = count(neets.employment_status == EMPLOYED) / total_neets
    record_metrics(month, employment_rate, counseling_cost, subsidy_cost, ...)

END FOR
```

### 4.2 Job Matching: `can_attempt_match(neet, job)`

**Hard Constraints (all must pass):**

```python
def can_attempt_match(neet, job):
    # Hard floor: skill match threshold (experimental: 0 to 1)
    if abs(neet.skill_level - job.skill_requirement) > skill_threshold:
        return False
    
    # Hard floor: transportation must be viable (>= 0.6)
    transportation_score = compute_accessibility(neet.location, job.location)
    if transportation_score < 0.6:
        return False
    
    # Hard floor: business must have willingness to hire
    if job.employer.willingness_to_hire < 0.5:
        return False
    
    # Hard floor: business must have capacity
    if job.employer.current_apprentices >= job.employer.capacity_ceiling:
        return False
    
    # Subsidy constraint: if subsidy is required, check eligibility
    if subsidy_required and subsidy_available == False:
        return False
    
    return True
```

### 4.3 Hiring Decision: `compute_hiring_decision(neet, job)`

**Probability Calculation:**

```python
def compute_hiring_decision(neet, job):
    # All hard constraints already passed; now compute soft probability
    
    # Components (all 0–1)
    skill_match = compute_match_quality(neet.skill_level, job.skill_requirement)
    # skill_match ranges from 0 (no match) to 1 (perfect match)
    
    transportation_accessibility = compute_accessibility(neet.location, job.location)
    # Already verified >= 0.6
    
    business_willingness = job.employer.willingness_to_hire
    # Already verified >= 0.5
    
    # Subsidy boost (if applicable)
    if subsidy_available:
        subsidy_effectiveness = subsidy_amount  # ranges 0.3–1.0
    else:
        subsidy_effectiveness = 1.0  # neutral
    
    # Company capacity score (soft): how much headroom does company have?
    capacity_ratio = job.employer.current_apprentices / job.employer.capacity_ceiling
    capacity_cushion = 1.0 - capacity_ratio  # 1.0 = empty, 0.0 = full
    
    # Composite probability (all factors multiply)
    base_probability = (skill_match * transportation_accessibility * 
                        business_willingness * subsidy_effectiveness * 
                        capacity_cushion)
    
    # If all conditions sufficient, constrain to 0.8–1.0 band
    if base_probability >= 0.5:  # arbitrary sufficient threshold
        hiring_probability = random.uniform(0.8, 1.0)
    else:
        # Attempt with lower probability proportional to base_probability
        hiring_probability = base_probability
    
    return hiring_probability
```

---

## 5. Policy Interventions

### 5.1 Counseling Intervention

**Parameters to vary:**

- `counseling_availability_budget[month]`: Total monthly budget
- `allocation_strategy`: How budget is distributed across NEETs and counseling types
  - Example: Target NEETs with highest impeding_factors first
  - Example: Rotate through all NEETs equitably
  - Example: Concentrate on subset for intensive intervention
- `effect_per_type[counseling_type]`: Magnitude of effect on impeding_factors and willingness

**Example Monthly Allocation:**

```
Month 1–6: counseling_budget = €50,000
Month 7–12: counseling_budget = €100,000

effect_mental_health = 0.15 (reduces impeding_factors 15% per month if active)
effect_job_matching = 0.12
effect_educational = 0.10
...
```

### 5.2 Wage Subsidy Intervention

**Parameters to vary:**

- `subsidy_available`: Binary (on/off)
- `subsidy_amount`: Euro amount (e.g., €500/month per apprentice)
- `subsidy_by_sector`: Differentiated amounts (e.g., manufacturing gets €600, retail gets €400)
- `subsidy_duration`: How long subsidy lasts per apprentice (e.g., first 6 months only)

**Example Subsidy Schedule:**

```
Scenario A (Low subsidy): €300/month, all sectors
Scenario B (High subsidy): €800/month, all sectors
Scenario C (Targeted): €500/month manufacturing, €300/month services
```

### 5.3 Policy Combinations to Simulate

Run the model with these factor combinations:

| Counseling Budget | Subsidy Level | Runs |
|------------------|---------------|------|
| Low (€30k/mo)    | Low (€300/mo) | 30   |
| Low              | High (€800/mo)| 30   |
| High (€100k/mo)  | Low           | 30   |
| High             | High          | 30   |

Output for each: distribution of outcomes (employment rate, cost per placement, NEET transitions).

---

## 6. Attribute Dynamics (Time Evolution)

### 6.1 NEET Attribute Changes

**While Employed (each month):**

```
skill_level += 0.02  (min capped at 1.0)
willingness_to_work += 0.01  (min capped at 1.0)
impeding_factors -= 0.015  (income enables solving barriers like transport, childcare)
```

**While in Counseling (each month, in addition to above):**

```
impeding_factors -= counseling_intensity_for_type × 0.10
willingness_to_work += counseling_intensity_for_type × 0.10
```

**Note:** Attributes drift gradually, capturing realistic behavioral change. Calibrate these rates based on domain expertise or empirical evidence.

### 6.2 Business Attribute Changes

**Willingness_to_hire:** Can be fixed or gradually updated based on satisfaction with previous hires (omit in first iteration for simplicity).

---

## 7. Output & Metrics

### 7.1 Primary Metrics (computed monthly)

| Metric | Definition | Use |
|--------|-----------|-----|
| `employment_rate` | % of NEETs employed | Primary outcome |
| `placements_this_month` | Count of new hires | Flow indicator |
| `avg_tenure` | Mean months employed (for employed NEETs) | Retention signal |
| `cost_per_placement` | Total intervention cost / placements | Cost-effectiveness |
| `neets_in_counseling` | Count receiving counseling | Intervention uptake |

### 7.2 Outcome Scenarios (across runs)

Aggregate results from 30–100 runs per policy scenario and classify into bins:

- **Very Poor:** Employment rate < 15%
- **Poor:** Employment rate 15–30%
- **Base:** Employment rate 30–45%
- **Good:** Employment rate 45–60%
- **Very Good:** Employment rate > 60%

Report distribution: "Of 30 runs with [policy X], 8 were Very Poor, 12 were Poor, 7 were Base, 3 were Good, 0 were Very Good."

### 7.3 Comparison Across Policies

Use Monte Carlo distributions to compare scenarios and identify:
- Which policy lever (counseling vs. subsidy) has stronger effect?
- Interaction effects: Does high subsidy + high counseling exceed additive effects?
- Cost-effectiveness: Which combination yields best employment rate per euro spent?

---

## 8. Implementation Notes: LLM-Based Agent Behavior

You mentioned using an LLM via API to simulate agent behavior. This is non-standard but feasible. Here's how to approach it:

### 8.1 Current ABM Frameworks & LLM Integration

**Standard ABM Platforms:**
- **NetLogo**: Rule-based, deterministic. No native LLM integration.
- **Mesa (Python)**: Agent-based framework. You can call external APIs within agent logic.
- **Repast (Java/Python)**: Scalable ABM framework. API calls possible but may be slow.

**None have out-of-the-box LLM integration.**

### 8.2 Using LLM for Agent Behavior

**Two possible approaches:**

**Approach A: LLM for One-Off Decision Making**

Call an LLM to determine hiring decisions or counseling allocation:

```python
def compute_hiring_decision_with_llm(neet, job, employer):
    prompt = f"""
    A business manager must decide whether to hire a NEET apprentice.
    
    NEET profile:
    - Skill level: {neet.skill_level}
    - Willingness: {neet.willingness_to_work}
    - Barriers: {neet.impeding_factors}
    
    Job details:
    - Skill requirement: {job.skill_requirement}
    - Sector: {job.sector}
    
    Business context:
    - Manager willingness: {employer.willingness_to_hire}
    - Current apprentices: {employer.current_apprentices} / {employer.capacity_ceiling}
    - Subsidy available: {subsidy_amount}
    
    Should the manager hire this apprentice? Respond with YES or NO and a confidence score (0–1).
    """
    
    response = llm_api_call(prompt, model="gpt-4", temperature=0.7)
    decision = parse_decision(response)  # extract YES/NO and confidence
    
    return decision
```

**Pros:** More realistic nuance, captures context-dependent reasoning.
**Cons:** 
- Slow (API latency ~1–5 seconds per call)
- Expensive at scale (1000 agents × 12 months × 3 decisions/month = 36,000 calls)
- Non-deterministic (same inputs may yield different outputs)
- Hard to debug why outcomes differ across runs

**Approach B: LLM for Initialization / Calibration Only**

Use LLM to generate realistic starting values for agent attributes:

```python
def generate_neet_profile_with_llm():
    prompt = """
    Generate a realistic profile for a NEET (Not in Education, Employment, or Training):
    - Willingness to work (0–1): ?
    - Impeding factors (0–1): ?
    - Skill level (0–1): ?
    
    Return as JSON.
    """
    
    profile = llm_api_call(prompt)
    return parse_profile(profile)
```

**Pros:** Generates realistic diversity in initial conditions; runs deterministically afterward.
**Cons:** Limited scope; deterministic simulation afterward may feel less "intelligent."

### 8.3 Recommendation

**For this project, I recommend Approach B (LLM for initialization) combined with explicit rules for decisions.**

Reasoning:
1. You want reproducible, debuggable results. Deterministic decision rules (Section 4.3) are more reliable.
2. The rule-based hiring model is already quite sophisticated (combines skill, transportation, subsidy, etc.).
3. Use LLM to generate realistic starting conditions (e.g., "what does a typical NEET profile look like?"), but let the rules drive simulation.
4. This keeps computational cost low and enables large-scale runs (100+ agents, multi-year simulations).

### 8.4 Implementation Stack Recommendation

**Technology choices:**

- **Language:** Python (rich ABM libraries, easy API integration)
- **Framework:** Mesa or custom (Mesa is lightweight, or write custom loop for full control)
- **LLM API:** OpenAI API (GPT-4 or GPT-3.5), Anthropic API (Claude), or open-source via Hugging Face
- **Data storage:** Pandas/CSV for results, or PostgreSQL if you want to store individual runs
- **Visualization:** Matplotlib, Plotly for outcome distributions

**Rough pseudocode structure:**

```python
import random
import json
from datetime import datetime

class NEET:
    def __init__(self, agent_id):
        self.id = agent_id
        self.willingness_to_work = random.uniform(0, 1)
        self.impeding_factors = random.uniform(0, 1)
        self.skill_level = random.uniform(0, 1)
        self.employment_status = 'NEET'
        self.months_employed = 0

class Business:
    def __init__(self, agent_id, size):
        self.id = agent_id
        self.company_size = size
        self.willingness_to_hire = random.uniform(0, 1)
        self.current_apprentices = 0
        self.capacity_ceiling = size // 5

class Simulation:
    def __init__(self, n_neets, n_businesses, months):
        self.neets = [NEET(i) for i in range(n_neets)]
        self.businesses = [Business(i, random.randint(5, 100)) for i in range(n_businesses)]
        self.months = months
        self.monthly_metrics = []
    
    def run(self, counseling_budget_fn, subsidy_fn):
        for month in range(self.months):
            self.step_counseling(counseling_budget_fn(month))
            self.step_job_matching(subsidy_fn(month))
            self.step_attribute_update()
            self.step_graduation()
            self.record_metrics(month)
        return self.monthly_metrics
    
    def step_counseling(self, budget):
        # Allocate counseling
        pass
    
    def step_job_matching(self, subsidy_level):
        # Try matches between neets and job pool
        pass
    
    def step_attribute_update(self):
        # Update attributes for employed neets
        pass
    
    def step_graduation(self):
        # Check 24-month graduations
        pass
    
    def record_metrics(self, month):
        employment_rate = sum(1 for n in self.neets if n.employment_status == 'EMPLOYED') / len(self.neets)
        self.monthly_metrics.append({'month': month, 'employment_rate': employment_rate})

# Run scenarios
scenarios = [
    {'name': 'Low-Low', 'counseling_budget': 30000, 'subsidy': 300},
    {'name': 'High-High', 'counseling_budget': 100000, 'subsidy': 800},
]

results = {}
for scenario in scenarios:
    runs = []
    for run_id in range(30):
        sim = Simulation(n_neets=10, n_businesses=5, months=12)
        metrics = sim.run(
            counseling_budget_fn=lambda m: scenario['counseling_budget'],
            subsidy_fn=lambda m: scenario['subsidy']
        )
        runs.append(metrics)
    results[scenario['name']] = runs

# Aggregate and report
for scenario_name, runs in results.items():
    final_rates = [r[-1]['employment_rate'] for r in runs]
    print(f"{scenario_name}: mean={np.mean(final_rates):.2f}, std={np.std(final_rates):.2f}")
```

---

## 9. Model Validation & Calibration

Before running policy scenarios, validate the model against known patterns:

1. **Sanity checks:**
   - Does employment rate increase if you double subsidy? (Should be yes.)
   - Does employment rate fall if you remove all businesses' willingness_to_hire? (Should drop to ~0.)
   - Does skill increase over time for employed NEETs? (Should be yes, monotonic.)

2. **Sensitivity analysis:**
   - Vary skill_threshold from 0 to 1. Employment rate should decrease as threshold increases.
   - Vary transportation hard floor from 0.5 to 0.8. Rate should decrease.

3. **Calibration:**
   - If domain expertise suggests a realistic employment rate of ~35% under baseline conditions, tune initial attribute distributions, thresholds, and dynamics to match.

---

## 10. Scaling to Test for Emergence

**First phase:** 10 NEETs, 5 businesses, 12 months → verify mechanics work.

**Expansion phases:**
- Phase 2: 50 NEETs, 20 businesses, 24 months
- Phase 3: 200 NEETs, 50 businesses, 36 months
- Phase 4: 400+ NEETs, 100+ businesses → observe if population-level dynamics change

**Question to answer:** Does doubling population yield proportional scaling of outcomes, or do new patterns emerge (e.g., job market saturation, competition effects)?

---

## 11. Key Parameter Table: Quick Reference

| Component | Parameter | Initial Value | Experimental Range |
|-----------|-----------|----------------|-------------------|
| NEET | skill_threshold | — | 0–1 |
| NEET | willingness (avg) | 0.5 | 0.3–0.8 |
| NEET | impeding_factors (avg) | 0.6 | 0.4–0.8 |
| Business | company_size (avg) | 25 | 5–100 |
| Business | willingness_to_hire (avg) | 0.6 | 0.3–0.8 |
| Transport | accessibility threshold | 0.6 | 0.5–0.8 |
| Counseling | effect per type | 0.10–0.15 | 0.05–0.25 |
| Subsidy | minimum effectiveness | 0.3 | 0.2–0.5 |
| Subsidy | max effectiveness | 1.0 | 0.8–1.0 |
| Time | apprentice duration | 24 months | 12–36 |
| Time | skill improvement rate | 0.02/month | 0.01–0.05 |

---

## 12. Next Steps

1. **Code the core simulation loop** (Section 4.1–4.3) with deterministic hiring decisions.
2. **Test with 10 NEETs, 5 businesses, 12 months** to verify mechanics.
3. **Run sensitivity analysis** on key thresholds (skill, transport, subsidy).
4. **Validate** against domain expectations (employment rates, cost-effectiveness).
5. **Run policy scenarios** (Section 5.3) with 30–100 independent runs per scenario.
6. **Analyze outcome distributions** and compare across scenarios.
7. **Scale** to larger populations and observe for emergence.

---

## Appendix: Sample Pseudocode for Complete Monthly Step

```python
def simulate_month(month, sim_state):
    """
    Complete monthly simulation step.
    
    sim_state: {neets, businesses, parameters, random_seed}
    """
    
    # 1. Allocate counseling based on budget
    counseling_recipients = allocate_counseling(
        budget=parameters['counseling_budget'][month],
        candidate_neets=[n for n in neets if n.employment_status == 'NEET'],
        types=parameters['counseling_types'],
        intensities=parameters['counseling_intensity']
    )
    
    # 2. Apply counseling effects
    for neet_id in counseling_recipients:
        neet = find_neet(neet_id)
        for counseling_type, intensity in counseling_recipients[neet_id].items():
            neet.impeding_factors -= intensity * 0.10
            neet.willingness_to_work += intensity * 0.10
    
    # 3. Generate job pool
    jobs = generate_job_pool(
        count=parameters['total_jobs'],
        distribution=parameters['job_quality_distribution'],
        businesses=businesses
    )
    
    # 4. Job matching
    matches_attempted = 0
    matches_successful = 0
    for neet in neets:
        if neet.employment_status == 'NEET' and neet.willingness_to_work > 0.3:  # must want to work
            for job in jobs:
                if can_attempt_match(neet, job, parameters):
                    subsidy_level = parameters['subsidy_amount'] if parameters['subsidy_available'] else 0
                    prob = compute_hiring_decision(neet, job, subsidy_level)
                    if random.random() < prob:
                        hire(neet, job)
                        matches_successful += 1
                    matches_attempted += 1
                    break  # each neet tries one job per month
    
    # 5. Apprentice graduation (24 months)
    for business in businesses:
        for record in business.apprentice_records[:]:
            if current_month - record['start_month'] >= 24:
                neet = find_neet(record['neet_id'])
                neet.employment_status = 'TRAINED_OUT'
                neet.months_employed = 0
                business.current_apprentices -= 1
                business.apprentice_records.remove(record)
    
    # 6. Attribute updates for employed NEETs
    for neet in neets:
        if neet.employment_status == 'EMPLOYED':
            neet.months_employed += 1
            neet.skill_level = min(1.0, neet.skill_level + 0.02)
            neet.willingness_to_work = min(1.0, neet.willingness_to_work + 0.01)
            neet.impeding_factors = max(0, neet.impeding_factors - 0.015)
    
    # 7. Record metrics
    employment_rate = sum(1 for n in neets if n.employment_status == 'EMPLOYED') / len(neets)
    counseling_cost = len(counseling_recipients) * parameters['cost_per_counseling']
    subsidy_cost = sum(parameters['subsidy_amount'] for business in businesses for _ in range(business.current_apprentices))
    
    metrics = {
        'month': month,
        'employment_rate': employment_rate,
        'placements': matches_successful,
        'counseling_cost': counseling_cost,
        'subsidy_cost': subsidy_cost,
        'neets_in_counseling': len(counseling_recipients),
        'total_apprentices': sum(b.current_apprentices for b in businesses)
    }
    
    return metrics
```

---

## Appendix: Example Scenario Output

```
Scenario: Low Counseling + Low Subsidy
Runs: 30

Month 12 Employment Rates:
  Mean: 28.3%
  Std Dev: 8.2%
  Min: 12%
  Max: 45%
  
Outcome Distribution:
  Very Poor (< 15%): 3 runs
  Poor (15–30%): 15 runs
  Base (30–45%): 10 runs
  Good (45–60%): 2 runs
  Very Good (> 60%): 0 runs

Cost per Placement: €2,500
---

Scenario: High Counseling + High Subsidy
Runs: 30

Month 12 Employment Rates:
  Mean: 52.1%
  Std Dev: 9.7%
  Min: 28%
  Max: 68%
  
Outcome Distribution:
  Very Poor (< 15%): 0 runs
  Poor (15–30%): 2 runs
  Base (30–45%): 5 runs
  Good (45–60%): 18 runs
  Very Good (> 60%): 5 runs

Cost per Placement: €4,200

---

Comparison:
High-High scenario improves employment rate by 23.8 percentage points (p-value < 0.01)
Cost per placement increases by €1,700, suggesting scale economies exist.
Recommend piloting High Counseling + High Subsidy scenario.
```

