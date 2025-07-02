import os
import tempfile
import shutil


def cleanup_tmp_node(state):
    """
    Removes temporary files and folders created during the pipeline run.
    """
    temp_dir = tempfile.gettempdir()
    files_to_remove = [
        os.path.join(temp_dir, "output.csv"),
        os.path.join(temp_dir, "output_geolocated.csv"),
    ]

    # Also remove any remaining.csv created by to_json.py in the uk_map/src/data directory
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../..")
    )
    data_dir = os.path.join(project_root, "uk_map/src/data")
    remaining_csv_path = os.path.join(data_dir, "remaining.csv")
    if os.path.exists(remaining_csv_path):
        files_to_remove.append(remaining_csv_path)

    dirs_to_remove = [
        os.path.join(temp_dir, "ufo_pdfs"),
    ]

    # Remove files
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Removed temp file: {file_path}")
            except Exception as e:
                print(f"Error removing file {file_path}: {e}")

    # Remove directories
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"Removed temp directory: {dir_path}")
            except Exception as e:
                print(f"Error removing directory {dir_path}: {e}")

    return state
