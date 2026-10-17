"""Small domain-neutral Plotly specifications; preserve order and missing points."""
from copy import deepcopy
import json


def series_figure(x, y, *, name='', title='', x_title='', y_title='', mode='lines+markers'):
    x, y = list(x), list(y)
    if len(x) != len(y):
        raise ValueError('aligned x and y required')
    if mode not in ('lines', 'markers', 'lines+markers'):
        raise ValueError('unsupported mode')
    spec = {'data': [{'type': 'scatter', 'x': deepcopy(x), 'y': deepcopy(y),
                      'name': name, 'mode': mode, 'connectgaps': False}],
            'layout': {'template': {}, 'title': {'text': title},
                       'xaxis': {'title': {'text': x_title}},
                       'yaxis': {'title': {'text': y_title}}}}
    json.dumps(spec, allow_nan=False)
    return spec


def matrix_figure(x, y, z, *, title='', x_title='', y_title=''):
    x, y, z = list(x), list(y), [list(row) for row in z]
    if len(z) != len(y) or any(len(row) != len(x) for row in z):
        raise ValueError('matrix shape must match axis labels')
    spec = {'data': [{'type': 'heatmap', 'x': deepcopy(x), 'y': deepcopy(y),
                      'z': deepcopy(z), 'zsmooth': False, 'hoverongaps': False}],
            'layout': {'template': {}, 'title': {'text': title},
                       'xaxis': {'type': 'category', 'title': {'text': x_title}},
                       'yaxis': {'type': 'category', 'categoryorder': 'array',
                                 'categoryarray': deepcopy(y), 'title': {'text': y_title}}}}
    json.dumps(spec, allow_nan=False)
    return spec
