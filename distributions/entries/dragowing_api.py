"""DRAgoWing min: figure specifications, aggregate HTML reports and JSONL records.

Plotly.js remains a browser runtime dependency of rendered reports, outside Python.
"""
from plot_specs import series_figure, matrix_figure
from records import read_jsonl
from research_report import render_report

__all__ = ['series_figure', 'matrix_figure', 'read_jsonl', 'render_report']
