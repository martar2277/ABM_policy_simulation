"""
Metrics collection and reporting.
"""

import json
import csv
import os
from typing import Dict, Any, List
from datetime import datetime


class MetricCollector:
    """
    Collects and saves simulation metrics.
    """

    def __init__(self, output_dir: str = "data/output"):
        """
        Initialize metric collector.

        Args:
            output_dir: Directory to save metrics
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def save_monthly_metrics(
        self,
        metrics: List[Dict[str, Any]],
        scenario_name: str,
        run_id: int = 0
    ):
        """
        Save monthly metrics to CSV.

        Args:
            metrics: List of monthly metric dictionaries
            scenario_name: Name of scenario
            run_id: Run identifier
        """
        filename = f"{scenario_name}_run{run_id}_monthly.csv"
        filepath = os.path.join(self.output_dir, filename)

        if not metrics:
            return

        # Write to CSV
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=metrics[0].keys())
            writer.writeheader()
            writer.writerows(metrics)

        return filepath

    def save_final_report(
        self,
        report: Dict[str, Any],
        scenario_name: str,
        run_id: int = 0
    ):
        """
        Save final simulation report to JSON.

        Args:
            report: Final report dictionary
            scenario_name: Name of scenario
            run_id: Run identifier
        """
        filename = f"{scenario_name}_run{run_id}_report.json"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        return filepath

    def print_summary(self, report: Dict[str, Any]):
        """
        Print a human-readable summary of the simulation.

        Args:
            report: Final report dictionary
        """
        print("\n" + "="*60)
        print("SIMULATION SUMMARY")
        print("="*60)

        print(f"\nConfiguration:")
        print(f"  Duration: {report['simulation_length_months']} months")
        print(f"  NEETs: {report['num_neets']}")
        print(f"  Businesses: {report['num_businesses']}")
        print(f"  LLM Profiles: {report['used_llm_profiles']}")

        print(f"\nFinal Outcomes:")
        print(f"  Employment Rate: {report['final_employment_rate']:.1%}")
        print(f"  Employed: {report['final_employed_count']}")
        print(f"  Trained Out: {report['final_trained_out_count']}")

        print(f"\nAggregate Statistics:")
        print(f"  Total Placements: {report['total_placements']}")
        print(f"  Total Applications: {report['total_applications']}")
        print(f"  Success Rate: {report['overall_success_rate']:.1%}")

        print(f"\nAttribute Changes:")
        print(f"  Avg Willingness: {report['avg_willingness_change']:+.3f}")
        print(f"  Avg Skill: {report['avg_skill_change']:+.3f}")
        print(f"  Avg Barriers: {report['avg_impeding_factors_change']:+.3f}")

        print(f"\nPolicy Parameters:")
        config = report['config']
        print(f"  Counseling Budget: €{config['counseling_budget']:,}/month")
        print(f"  Subsidy Available: {config['subsidy_available']}")
        print(f"  Subsidy Effectiveness: {config['subsidy_effectiveness']}")

        print("\n" + "="*60 + "\n")


def aggregate_multiple_runs(reports: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate statistics from multiple simulation runs.

    Args:
        reports: List of final report dictionaries

    Returns:
        Aggregated statistics
    """
    if not reports:
        return {}

    import statistics

    employment_rates = [r['final_employment_rate'] for r in reports]
    total_placements = [r['total_placements'] for r in reports]

    # Classify outcomes (from specification Section 7.2)
    def classify_outcome(rate):
        if rate < 0.15:
            return 'Very Poor'
        elif rate < 0.30:
            return 'Poor'
        elif rate < 0.45:
            return 'Base'
        elif rate < 0.60:
            return 'Good'
        else:
            return 'Very Good'

    outcome_counts = {}
    for rate in employment_rates:
        category = classify_outcome(rate)
        outcome_counts[category] = outcome_counts.get(category, 0) + 1

    return {
        'num_runs': len(reports),
        'employment_rate': {
            'mean': statistics.mean(employment_rates),
            'stdev': statistics.stdev(employment_rates) if len(employment_rates) > 1 else 0,
            'min': min(employment_rates),
            'max': max(employment_rates),
        },
        'total_placements': {
            'mean': statistics.mean(total_placements),
            'stdev': statistics.stdev(total_placements) if len(total_placements) > 1 else 0,
            'min': min(total_placements),
            'max': max(total_placements),
        },
        'outcome_distribution': outcome_counts,
        'scenario_name': reports[0].get('config', {}).get('scenario_name', 'Unknown')
    }


def print_aggregated_summary(aggregated: Dict[str, Any]):
    """
    Print summary of aggregated results from multiple runs.

    Args:
        aggregated: Aggregated statistics dictionary
    """
    print("\n" + "="*60)
    print(f"AGGREGATED RESULTS - {aggregated['scenario_name']}")
    print(f"Based on {aggregated['num_runs']} runs")
    print("="*60)

    emp_rate = aggregated['employment_rate']
    print(f"\nMonth 12 Employment Rates:")
    print(f"  Mean: {emp_rate['mean']:.1%}")
    print(f"  Std Dev: {emp_rate['stdev']:.1%}")
    print(f"  Min: {emp_rate['min']:.1%}")
    print(f"  Max: {emp_rate['max']:.1%}")

    print(f"\nOutcome Distribution:")
    dist = aggregated['outcome_distribution']
    for category in ['Very Poor', 'Poor', 'Base', 'Good', 'Very Good']:
        count = dist.get(category, 0)
        print(f"  {category} (<{category.lower()}>): {count} runs")

    placements = aggregated['total_placements']
    print(f"\nTotal Placements:")
    print(f"  Mean: {placements['mean']:.1f}")
    print(f"  Std Dev: {placements['stdev']:.1f}")

    print("\n" + "="*60 + "\n")
