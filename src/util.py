from pathlib import Path


def get_project_directory():
    test_py_path = Path(__file__)

    project_directory = None
    for parent in test_py_path.parents:
        if (parent / 'modelling-assistant').exists():
            project_directory = parent / 'modelling-assistant'
            break

    return project_directory
