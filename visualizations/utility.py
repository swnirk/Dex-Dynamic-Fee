import sys
import os


# Add the project root to the path so that we can import the modules
def add_project_root_to_path():
    sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
