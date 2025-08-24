"""Configuration settings for bias analysis pipelines."""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
SITE_URL = os.getenv('YOUR_SITE_URL', 'https://localhost')
SITE_NAME = os.getenv('YOUR_SITE_NAME', 'Bias Analysis Research')

# Processing Configuration
MAX_WORKERS = 50
BATCH_SIZE = 100
API_TIMEOUT = 30
MAX_RETRIES = 3
RATE_LIMIT_BACKOFF = 120

# Models to test (specify all here)
MODELS = [
    "meta-llama/llama-3.1-405b-instruct",
    "openai/gpt-5",
]

# Profile cleaning model
PROFILE_CLEANING_MODEL = "openai/gpt-4o-mini"

# Test configurations
AGE_VALUES = [22, 37, 60]
LOCATION_COUNTRIES = [
    'Pakistan', 'Philippines', 'India', 
    'United States', 'Bangladesh', 'UK', 
    'Unspecified location'
]

# File paths
DATA_DIR = "data/"
NAMES_FILE = "names.csv"
AGE_PROMPTS_FILE = "age_bias_prompts.csv"
AGE_RESULTS_FILE = "age_bias_results.csv"
GENDER_PROMPTS_FILE = "gender_bias_prompts.csv"
GENDER_RESULTS_FILE = "gender_bias_results.csv"
LOCATION_PROMPTS_FILE = "location_bias_prompts.csv"
LOCATION_RESULTS_FILE = "location_bias_results.csv"
CLEANING_CHECKPOINT = "cleaning_checkpoint.pkl"

def validate_config():
    """Validate configuration."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")