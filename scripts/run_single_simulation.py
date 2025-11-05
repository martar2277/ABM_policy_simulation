#!/usr/bin/env python3
"""
Run a single simulation with specified configuration.

Usage:
    python scripts/run_single_simulation.py
    python scripts/run_single_simulation.py --scenario low_counseling_low_subsidy
    python scripts/run_single_simulation.py --random-seed 42
"""

import sys
import os
import argparse

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.simulation import SimulationEngine
from src.llm import LLMClient
from src.utils import load_scenario_config, config_to_simulation_params
from src.metrics import MetricCollector


def main():
    parser = argparse.ArgumentParser(description='Run a single ABM simulation')
    parser.add_argument(
        '--scenario',
        type=str,
        default=None,
        help='Scenario name (without .yaml extension)'
    )
    parser.add_argument(
        '--random-seed',
        type=int,
        default=None,
        help='Random seed for reproducibility'
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

    args = parser.parse_args()

    # Load configuration
    if args.scenario:
        print(f"Loading scenario: {args.scenario}")
        config = load_scenario_config(args.scenario)
        scenario_name = config.get('scenario_name', args.scenario)
    else:
        print("Using base configuration (no scenario)")
        from src.utils.config_loader import load_yaml
        config = load_yaml('config/base_config.yaml')
        scenario_name = 'base'

    # Convert config to simulation parameters
    sim_params = config_to_simulation_params(config)

    # Override LLM provider if specified
    if args.llm_provider != 'mock':
        sim_params['use_llm_profiles'] = True

    # Create LLM client if needed
    llm_client = None
    if sim_params.get('use_llm_profiles'):
        llm_client = LLMClient(provider=args.llm_provider)
        print(f"Using LLM provider: {args.llm_provider}")
    else:
        llm_client = LLMClient(provider='mock')
        print("Using mock LLM (random profiles)")

    # Add random seed
    if args.random_seed is not None:
        sim_params['random_seed'] = args.random_seed
        print(f"Random seed: {args.random_seed}")

    # Create and run simulation
    print(f"\n{'='*60}")
    print(f"Running simulation: {scenario_name}")
    print(f"{'='*60}\n")

    sim = SimulationEngine(
        **sim_params,
        llm_client=llm_client
    )

    # Run simulation
    monthly_metrics = sim.run()

    # Get final report
    final_report = sim.get_final_report()
    final_report['scenario_name'] = scenario_name

    # Save results
    collector = MetricCollector(output_dir=args.output_dir)

    monthly_file = collector.save_monthly_metrics(
        metrics=monthly_metrics,
        scenario_name=scenario_name.replace(' ', '_'),
        run_id=args.random_seed or 0
    )

    report_file = collector.save_final_report(
        report=final_report,
        scenario_name=scenario_name.replace(' ', '_'),
        run_id=args.random_seed or 0
    )

    # Print summary
    collector.print_summary(final_report)

    print(f"Results saved:")
    print(f"  Monthly metrics: {monthly_file}")
    print(f"  Final report: {report_file}")

    # Print LLM usage stats if applicable
    if sim_params.get('use_llm_profiles'):
        llm_stats = llm_client.get_usage_stats()
        print(f"\nLLM Usage:")
        print(f"  Total calls: {llm_stats['total_calls']}")
        print(f"  Total tokens: {llm_stats['total_tokens']}")
        print(f"  Estimated cost: ${llm_stats['estimated_cost_usd']:.2f}")


if __name__ == '__main__':
    main()
