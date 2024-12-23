import sys
import os
from matplotlib.ticker import MaxNLocator
from matplotlib.pyplot import Axes


# Add the project root to the path so that we can import the modules
def add_project_root_to_path():
    sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))


def fix_x_axis_labels(ax: Axes):
    ax.xaxis.set_major_locator(
        MaxNLocator(nbins=10)
    )  # Set to show a maximum of 10 ticks
