"""
Metrics module - Collection and reporting.
"""

from .metric_collector import (
    MetricCollector,
    aggregate_multiple_runs,
    print_aggregated_summary
)

__all__ = [
    'MetricCollector',
    'aggregate_multiple_runs',
    'print_aggregated_summary',
]
