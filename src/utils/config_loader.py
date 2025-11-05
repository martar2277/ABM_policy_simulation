"""
Configuration loader for YAML config files.
"""

import yaml
import os
from typing import Dict, Any


def load_yaml(file_path: str) -> Dict[str, Any]:
    """
    Load a YAML configuration file.

    Args:
        file_path: Path to YAML file

    Returns:
        Configuration dictionary
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Config file not found: {file_path}")

    with open(file_path, 'r') as f:
        config = yaml.safe_load(f)

    return config or {}


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two configuration dictionaries.

    Override values take precedence over base values.

    Args:
        base: Base configuration
        override: Override configuration

    Returns:
        Merged configuration
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def load_scenario_config(scenario_name: str, base_config_path: str = None) -> Dict[str, Any]:
    """
    Load a scenario configuration, merging with base config.

    Args:
        scenario_name: Name of scenario file (without .yaml)
        base_config_path: Path to base config (optional)

    Returns:
        Merged configuration
    """
    # Determine paths
    script_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    if base_config_path is None:
        base_config_path = os.path.join(script_dir, 'config', 'base_config.yaml')

    scenario_path = os.path.join(script_dir, 'config', 'scenarios', f'{scenario_name}.yaml')

    # Load configurations
    base_config = load_yaml(base_config_path)
    scenario_config = load_yaml(scenario_path)

    # Merge
    merged = merge_configs(base_config, scenario_config)

    return merged


def config_to_simulation_params(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert config dictionary to simulation engine parameters.

    Args:
        config: Configuration dictionary

    Returns:
        Parameters for SimulationEngine
    """
    return {
        'num_neets': config.get('agents', {}).get('neets', {}).get('count', 10),
        'num_businesses': config.get('agents', {}).get('businesses', {}).get('count', 5),
        'duration_months': config.get('simulation', {}).get('duration_months', 12),
        'use_llm_profiles': config.get('llm', {}).get('enabled', False),
        'config': {
            'counseling_budget': config.get('policies', {}).get('counseling', {}).get('budget_monthly', 50000),
            'counseling_intensity': config.get('policies', {}).get('counseling', {}).get('intensity', 0.12),
            'subsidy_available': config.get('policies', {}).get('subsidy', {}).get('available', True),
            'subsidy_effectiveness': config.get('policies', {}).get('subsidy', {}).get('effectiveness', 0.5),
            'skill_threshold': config.get('matching', {}).get('skill_threshold', 0.4),
            'transportation_floor': config.get('matching', {}).get('transportation_floor', 0.6),
            'min_business_willingness': config.get('matching', {}).get('min_business_willingness', 0.5),
            'max_attempts_per_neet': config.get('matching', {}).get('max_attempts_per_neet', 3),
            'region_size': config.get('environment', {}).get('region_size', 50),
        }
    }
