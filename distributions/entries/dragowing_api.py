"""DRAgoWing min: figure specifications, aggregate HTML reports and JSONL records.

Plotly.js remains a browser runtime dependency of rendered reports, outside Python.
"""
from figures import class_mark, heatmap_figure, trajectory_figure
from records import read_jsonl, select_items
from research_report import render_report

__all__ = ['class_mark', 'heatmap_figure', 'trajectory_figure', 'read_jsonl', 'select_items', 'render_report']
