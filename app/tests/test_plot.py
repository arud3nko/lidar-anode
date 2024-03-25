import plotly.graph_objects as go
import numpy as np

def build_slices_plot(points_data):
    x, y, z = [], [], []
    for points in points_data:
        x.extend([point[0] for point in points])
        y.extend([point[1] for point in points])
        z.extend([point[2] for point in points])

    fig = go.Figure(data=[go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(
            size=0.7,
            color=z,  # set color to an array/list of desired values
            colorscale='Viridis'
        )
    )])

    fig.update_layout(scene=dict(
        xaxis_title='X',
        yaxis_title='Y',
        zaxis_title='Z',
        aspectratio=dict(x=1, y=1, z=1),
    ))

    fig.show()