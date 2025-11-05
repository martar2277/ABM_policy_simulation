#!/usr/bin/env python3
"""
Run multiple simulations for a scenario to gather statistics.

Usage:
    python scripts/run_scenario_batch.py --scenario low_counseling_low_subsidy --num-runs 30
"""

import sys
import os
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.simulation import SimulationEngine
from src.llm import LLMClient
from src.utils import load_scenario_config, config_to_simulation_params
from src.metrics import MetricCollector, aggregate_multiple_runs, print_aggregated_summary


def main():
    parser = argparse.ArgumentParser(description='Run multiple ABM simulations for statistical analysis')
    parser.add_argument(
        '--scenario',
        type=str,
        required=True,
        help='Scenario name (without .yaml extension)'
    )
    parser.add_argument(
        '--num-runs',
        type=int,
        default=30,
        help='Number of simulation runs'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/output',
        help='Output directory for results'
    )
    parser.add_argument(
        '--llm-provider',
        type=str,
        default='mock',
        choices=['mock', 'openai', 'anthropic'],
        help='LLM provider to use'
    )
    parser.add_argument(
        '--start-seed',
        type=int,
        default=0,
        help='Starting random seed'
    )

    args = parser.parse_args()

    # Load configuration
    print(f"Loading scenario: {args.scenario}")
    config = load_scenario_config(args.scenario)
    scenario_name = config.get('scenario_name', args.scenario)

    # Convert config to simulation parameters
    sim_params = config_to_simulation_params(config)

    # Override with command line args
    if args.llm_provider != 'mock':
        sim_params['use_llm_profiles'] = True

    print(f"\n{'='*60}")
    print(f"Batch Runner: {scenario_name}")
    print(f"Running {args.num_runs} simulations")
    print(f"{'='*60}\n")

    # Initialize collector
    collector = MetricCollector(output_dir=args.output_dir)

    # Store all reports
    all_reports = []

    # Run simulations
    start_time = datetime.now()

    for run_id in range(args.num_runs):
        seed = args.start_seed + run_id

        print(f"\n--- Run {run_id + 1}/{args.num_runs} (seed={seed}) ---")

        # Create LLM client for this run
        llm_client = LLMClient(provider=args.llm_provider)

        # Create simulation
        sim = SimulationEngine(
            **sim_params,
            llm_client=llm_client,
            random_seed=seed
        )

        # Run
        monthly_metrics = sim.run()
        final_report = sim.get_final_report()
        final_report['scenario_name'] = scenario_name
        final_report['run_id'] = run_id
        final_report['random_seed'] = seed

        # Save
        collector.save_monthly_metrics(
            metrics=monthly_metrics,
            scenario_name=scenario_name.replace(' ', '_'),
            run_id=run_id
        )

        collector.save_final_report(
            report=final_report,
            scenario_name=scenario_name.replace(' ', '_'),
            run_id=run_id
        )

        all_reports.append(final_report)

        # Quick summary
        print(f"  Final employment rate: {final_report['final_employment_rate']:.1%}")
        print(f"  Total placements: {final_report['total_placements']}")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Aggregate results
    print(f"\n{'='*60}")
    print(f"All {args.num_runs} runs completed in {duration:.1f} seconds")
    print(f"{'='*60}")

    aggregated = aggregate_multiple_runs(all_reports)
    print_aggregated_summary(aggregated)

    # Save aggregated results
    import json
    agg_filename = f"{scenario_name.replace(' ', '_')}_aggregated.json"
    agg_filepath = os.path.join(args.output_dir, agg_filename)

    with open(agg_filepath, 'w') as f:
        json.dump(aggregated, f, indent=2)

    print(f"Aggregated results saved to: {agg_filepath}")

    # Print LLM usage if applicable
    if sim_params.get('use_llm_profiles') and args.llm_provider != 'mock':
        # Approximate total cost
        estimated_total_cost = all_reports[0].get('llm_cost', 0) * args.num_runs
        print(f"\nEstimated total LLM cost: ${estimated_total_cost:.2f}")


if __name__ == '__main__':
    main()
