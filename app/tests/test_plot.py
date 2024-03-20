import matplotlib.pyplot as plt
import numpy as np


def build_slices_plot(points_data):
    fig = plt.figure(figsize=(20, 16))
    ax = fig.add_subplot(111, projection='3d')
    for points in points_data:
        x_coords = [point[0] for point in points]
        y_coords = [point[1] for point in points]
        z_coords = [point[2] for point in points]

        colors = np.linspace(0, 1, len(z_coords))

        ax.scatter(x_coords, y_coords, z_coords, s=1, c=colors, cmap='RdYlGn', marker='o')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()
