import pandas as pd
import glob
import config


def load_csv_data():
    """Load all CSV files from data directory."""
    all_files = glob.glob(f"{config.DATA_DIR}*.csv")
    if not all_files:
        raise FileNotFoundError(f"No CSV files found in {config.DATA_DIR}")
    
    data_frames = []
    for filename in all_files:
        df = pd.read_csv(filename)
        df['source_file'] = filename.split('/')[-1]
        data_frames.append(df)
    
    return pd.concat(data_frames, ignore_index=True)


def prepare_location_data():
    """Prepare US and Philippines freelancers for location bias testing."""
    full_data = load_csv_data()
    
    # Get Philippines freelancers
    philippines_freelancers = full_data[full_data['country'] == 'Philippines']
    
    # Get US freelancers
    us_freelancers = full_data[full_data['country'] == 'United States']
    
    return us_freelancers, philippines_freelancers
