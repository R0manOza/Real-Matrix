"""Configuration settings for the debate system."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Model selection - using GPT-4 variants
MODELS = {
    "solver_1": "gpt-4",
    "solver_2": "gpt-4-turbo-preview",
    "solver_3": "gpt-4",
    "judge": "gpt-4-turbo-preview"
}

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROBLEMS_FILE = os.path.join(DATA_DIR, "problems.json")
RAW_OUTPUTS_DIR = os.path.join(DATA_DIR, "raw_outputs")
RESULTS_DIR = os.path.join(DATA_DIR, "results")

# API settings
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
REQUEST_TIMEOUT = 60  # seconds

# Temperature settings for different roles
TEMPERATURES = {
    "solver": 0.7,  # Creative but focused
    "reviewer": 0.5,  # More analytical
    "judge": 0.3  # Very deterministic
}