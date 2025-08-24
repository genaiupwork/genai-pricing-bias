# Bias Analysis in AI-Powered Freelancer Rate Evaluation

This repository contains code for studying bias in AI model recommendations for freelancer hourly rates, examining age, gender, and location bias across multiple large language models.

## Overview

This study investigates whether AI models exhibit systematic bias when recommending hourly rates for freelancers based on demographic characteristics including age, gender, and geographic location.

## Project Structure

```
upwork_countries/
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
└── utils/                   # Utility functions
```

## Setup

### Prerequisites
- Python 3.8+
- OpenRouter API key (sign up at https://openrouter.ai/)

### Installation

1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd upwork_countries
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install pandas>=2.0.0 numpy>=1.24.0 requests>=2.31.0 tenacity>=9.0.0
   pip install python-dotenv>=1.0.0 openpyxl>=3.1.0 psutil>=5.9.0
   pip install python-dateutil>=2.8.0 pytz>=2023.3 scipy>=1.10.0
   ```

4. **Configure environment:**
   Create `.env` file:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   YOUR_SITE_URL=https://your-research-site.edu
   YOUR_SITE_NAME=Bias Analysis Research
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

### Optional Columns
- `jobSuccess`: Success percentage
- `totalJobs`: Number of completed jobs
- `totalHours`: Total hours worked
- `profileUrl`: Profile URL

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
- Infers gender from freelancer names
- Tests across multiple geographic contexts
- Compares recommendations for different genders

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

## Troubleshooting

### Common Issues

**API Key Errors:**
- Ensure `.env` file exists with valid `OPENROUTER_API_KEY`
- Check OpenRouter account has sufficient credits

**Rate Limiting:**
- Reduce `MAX_WORKERS` in config.py (try 10-20)
- Increase `RATE_LIMIT_BACKOFF` time

**Memory Issues:**
- Reduce `BATCH_SIZE` in config.py
- Process data in smaller chunks

**Data Format Errors:**
- Verify CSV files have required columns
- Ensure `hourlyRate` column contains numeric values
- Check for special characters or encoding issues

## Models

The framework supports any models available through OpenRouter API. Current configuration:
- `meta-llama/llama-3.1-405b-instruct`
- `openai/gpt-5`

To add models, edit the `MODELS` list in `config.py` with any OpenRouter-supported model IDs.

## License

This code is provided for academic and research purposes. Ensure compliance with your institution's research ethics guidelines and the terms of service of data sources and API providers.
