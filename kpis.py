"""Compute KPIs for a model from simulation results.

Keep this module synced with kpis.py in `hpath-sim`.
"""
from dataclasses import dataclass, field
from typing import TypedDict

from chart_datatypes import ChartData, MultiChartData


Progress = TypedDict('Progress', {
    '7': float,
    '10': float,
    '12': float,
    '21': float
})
"""Returns the proportion of specimens completed within 7, 10, 12, and 21 days."""

LabProgress = TypedDict('LabProgress', {
    '3': float
})
"""Returns the proportion of specimens with lab component completed within three days."""


@dataclass(kw_only=True)
class Report:
    """Dataclass for reporting a set of KPIs for passing to a frontend visualisation server.
    In the current implementation, this is https://github.com/lakeesiv/digital-twin"""
    overall_tat: float
    lab_tat: float
    progress: Progress
    lab_progress: LabProgress
    tat_by_stage: ChartData
    resource_allocation: dict[str, ChartData]  # ChartData for each resource
    wip_by_stage: MultiChartData
    utilization_by_resource: ChartData
    q_length_by_resource: ChartData
    hourly_utilization_by_resource: MultiChartData

    overall_tat_min: float | None = field(default=None)
    overall_tat_max: float | None = field(default=None)
    lab_tat_min: float | None = field(default=None)
    lab_tat_max: float | None = field(default=None)
    progress_min: Progress | None = field(default=None)
    progress_max: Progress | None = field(default=None)
    lab_progress_min: LabProgress | None = field(default=None)
    lab_progress_max: LabProgress | None = field(default=None)
