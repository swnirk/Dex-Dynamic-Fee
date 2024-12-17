import sys
import os
from matplotlib.ticker import MaxNLocator
from matplotlib.pyplot import Axes


# Add the project root to the path so that we can import the modules
def add_project_root_to_path():
    sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))


def get_initial_pool_sizes(price_A: float, price_B: float, total_pool: float) -> tuple:
    """
    Returns the initial pool sizes for the two assets given the prices of the two assets
    """
    r = price_A / price_B
    q_A = total_pool / (r + 1)
    q_B = total_pool - q_A
    return q_A, q_B


def fix_x_axis_labels(ax: Axes):
    ax.xaxis.set_major_locator(
        MaxNLocator(nbins=10)
    )  # Set to show a maximum of 10 ticks
