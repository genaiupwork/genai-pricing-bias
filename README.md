# When AI Sets Wages: Biases and Discrimination in Generative Pricing

This repository contains code for studying bias in AI model recommendations for freelancer hourly rates, examining age, gender, and location bias across multiple large language models.

## Overview

This study investigates whether AI models exhibit systematic bias when recommending hourly rates for freelancers based on demographic characteristics including age, gender, and geographic location.

## Project Structure

```
genai-pricing-bias/
├── config.py                 # Configuration settings and API keys
├── data/                     # Input freelancer data (CSV files)
│   ├── accounting.csv
│   ├── data_analytics.csv
│   ├── full_stack_engineer.csv
│   └── ...
├── pipelines/                # Main analysis pipelines
│   ├── age_pipeline.py       # Age bias analysis
│   ├── gender_pipeline.py    # Gender bias analysis
│   ├── location_pipeline.py  # Location bias analysis
│   └── rate_pipeline.py      # Base rate analysis
├── prompts/                  # Prompt generation modules
├── services/                 # API integration
├── names.csv                 # Name Mapping 
└── utils/                   # Utility functions
```

## Setup

### Installation

1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd genai-pricing-bias
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash   
   pip install -r requirements.txt    
   ```

4. **Configure environment:**
   Create `.env` file:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

## Data Format

**Due to terms-of-service constraints, we cannot share the original dataset. The code works with any similar freelancer profile dataset.**

### Required CSV Columns

| Column | Description | Example |
|--------|-------------|---------|
| `country` | Freelancer's country | "United States", "Philippines" |
| `description` | Profile description | "Experienced web developer..." |
| `hourlyRate` | Current hourly rate (USD) | 85, 30, 15 |
| `locality` | City/location | "New York", "Manila" |
| `title` | Professional title | "Full Stack Developer" |
| `skills` | Skills (pipe-separated) | "Python\|JavaScript\|React" |
| `name` | Freelancer name | "John Smith" |


### Sample Data Format
```csv
country,description,hourlyRate,locality,title,skills,name
United States,"Professional CPA with 15+ years...",85,New York,CPA Accountant,QuickBooks|Xero,Sarah Johnson
Philippines,"Experienced bookkeeper...",25,Cebu City,Expert Bookkeeper,QuickBooks Online|Xero,Maria Santos
```

Place CSV files in the `data/` directory. The system automatically loads all CSV files found.

## Usage

### Running Analyses

```bash
# Age bias analysis
python pipelines/age_pipeline.py

# Gender bias analysis  
python pipelines/gender_pipeline.py

# Location bias analysis
python pipelines/location_pipeline.py

# Base rate analysis
python pipelines/rate_pipeline.py
```

### Configuration

Edit `config.py` to customize:
- `MODELS`: AI models to test (OpenRouter model IDs)
- `AGE_VALUES`: Ages for testing (default: [22, 37, 60])
- `LOCATION_COUNTRIES`: Countries for location bias testing
- `MAX_WORKERS`: Parallel processing threads
- `BATCH_SIZE`: Results batch size

## Methodology

### Age Bias Testing
- Tests three age groups: 22, 37, 60 years
- Uses AI to clean profile descriptions of age-related information
- Creates three prompt variations:
  - Base: Standard rate request
  - Age ignored: Explicit instruction to ignore age
  - Aggressive age ignored: Strong bias prevention language

### Gender Bias Testing
- Tests all freelancers with 3 gender variations (male, female, unspecified)
- Name injection: Adds "Hi! My name is [name]" to profile descriptions
- Uses country-specific common names from names.csv mapping
- 4 prompt variations: base, gender-focused, aggressive male-favored, aggressive female-favored
- Generates 12 prompts per freelancer (3 gender × 4 prompt variations)

### Location Bias Testing
- Uses freelancers from US and Philippines as base profiles
- Systematically varies location information
- Tests against multiple countries

## Output Files

Each pipeline generates CSV files:
- `*_prompts.csv`: Generated prompts with variations
- `*_results.csv`: AI model responses and rate recommendations

Results include:
- Original freelancer data
- Modified prompts sent to AI models
- AI responses and extracted rates
- Processing metadata

## Models

The framework supports any models available through OpenRouter API. Current configuration:
- `meta-llama/llama-3.1-405b-instruct`
- `openai/gpt-5-mini`

To add models, edit the `MODELS` list in `config.py` with any OpenRouter-supported model IDs.
