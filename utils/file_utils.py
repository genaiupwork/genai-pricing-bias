import pandas as pd
import os


def file_exists(filepath: str) -> bool:
    """Check if file exists."""
    return os.path.exists(filepath)


def save_to_csv(data: list, filepath: str, append: bool = False):
    """Save data to CSV file."""
    df = pd.DataFrame(data)
    mode = 'a' if append else 'w'
    header = not (append and file_exists(filepath))
    df.to_csv(filepath, mode=mode, header=header, index=False)


def load_completed_tasks(filepath: str) -> set:
    """Load completed (row_index, model) combinations from results file."""
    if not file_exists(filepath):
        return set()
    
    try:
        df = pd.read_csv(filepath)
        return {(row['row_index'], row['model']) for _, row in df.iterrows()}
    except Exception:
        return set()
