================================================================================
BIAS ANALYSIS IN AI-POWERED FREELANCER RATE EVALUATION
================================================================================

ACADEMIC RESEARCH CODE FOR NATURE/SCIENCE SUBMISSION

This repository contains the complete code framework for studying bias in AI 
model recommendations for freelancer hourly rates. The research examines age, 
gender, and location bias across multiple large language models using 
freelancer profile data.

================================================================================
OVERVIEW
================================================================================

This study investigates whether AI models exhibit systematic bias when 
recommending hourly rates for freelancers based on demographic characteristics. 

Research Questions:
- Age Bias: Do models recommend different rates based on freelancer age?
- Gender Bias: Do models show bias based on inferred gender from names?
- Location Bias: Do models discriminate based on freelancer location/country?

The framework systematically tests multiple AI models by creating controlled 
variations of freelancer profiles and analyzing rate recommendations.

================================================================================
PROJECT STRUCTURE
================================================================================

upwork_countries/
├── config.py                 # Configuration settings and API keys
├── data/                     # Input freelancer data (CSV files)
│   ├── accounting.csv
│   ├── data_analytics.csv
│   ├── full_stack_engineer.csv
│   ├── general_virtual_assistance.csv
│   ├── graphic_design.csv
│   └── social_media_marketing.csv
├── pipelines/                # Main analysis pipelines
│   ├── age_pipeline.py       # Age bias analysis
│   ├── gender_pipeline.py    # Gender bias analysis
│   ├── location_pipeline.py  # Location bias analysis
│   └── rate_pipeline.py      # Base rate analysis
├── prompts/                  # Prompt generation modules
│   ├── base.py              # Base prompt templates
│   ├── age_bias.py          # Age-specific prompts
│   ├── gender_bias.py       # Gender-specific prompts
│   └── location_bias.py     # Location-specific prompts
├── services/                 # API integration
│   └── openrouter.py        # OpenRouter API client
├── utils/                   # Utility functions
│   ├── data_loader.py       # Data loading and preprocessing
│   ├── file_utils.py        # File operations
│   └── progress.py          # Progress tracking
└── backup/                  # Results and backup files

================================================================================
SETUP INSTRUCTIONS
================================================================================

PREREQUISITES:
- Python 3.8 or higher
- OpenRouter API key (sign up at https://openrouter.ai/)

STEP 1: CLONE AND SETUP ENVIRONMENT
```
git clone <repository-url>
cd upwork_countries
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

STEP 2: INSTALL DEPENDENCIES
```
pip install pandas>=2.0.0
pip install numpy>=1.24.0
pip install requests>=2.31.0
pip install tenacity>=9.0.0
pip install python-dotenv>=1.0.0
pip install openpyxl>=3.1.0
pip install psutil>=5.9.0
pip install python-dateutil>=2.8.0
pip install pytz>=2023.3
pip install scipy>=1.10.0
```

STEP 3: CONFIGURE API ACCESS
Create a .env file in the root directory:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
YOUR_SITE_URL=https://your-research-site.edu
YOUR_SITE_NAME=Bias Analysis Research
```

Get your API key from https://openrouter.ai/ (requires account creation)

STEP 4: PREPARE DATA
Due to terms-of-service constraints, we cannot share our original dataset. 
Replace the existing CSV files in data/ with your freelancer data.

================================================================================
DATA FORMAT REQUIREMENTS
================================================================================

Required CSV columns for input data:

ESSENTIAL COLUMNS:
- country: Freelancer's country (e.g., "United States", "Philippines", "India")
- description: Profile description text
- hourlyRate: Current hourly rate in USD (numeric)
- locality: City/location (e.g., "New York", "Manila")  
- title: Professional title/services offered
- skills: Skills (pipe-separated, e.g., "Python|JavaScript|React")
- name: Freelancer name (for gender inference)

OPTIONAL COLUMNS (enhance analysis):
- jobSuccess: Success score percentage
- totalJobs: Number of completed jobs
- totalHours: Total hours worked
- profileUrl: Profile URL

SAMPLE DATA FORMAT:
```
country,description,hourlyRate,locality,title,skills,name
United States,"Professional CPA with 15+ years of experience...",85,New York,CPA Accountant,QuickBooks|Xero|Tax Preparation,Sarah Johnson
Philippines,"Experienced bookkeeper specializing in QuickBooks...",25,Cebu City,Expert Bookkeeper,QuickBooks Online|Xero|Bookkeeping,Maria Santos
India,"Qualified chartered accountant with expertise...",18,Mumbai,Chartered Accountant,IFRS|US GAAP|QuickBooks,Rajesh Patel
```

Create multiple CSV files in data/ directory, one per job category. The code
will automatically load and combine all CSV files found in data/.

================================================================================
RUNNING THE ANALYSIS
================================================================================

INDIVIDUAL BIAS ANALYSES:

1. Age Bias Analysis:
   ```
   python pipelines/age_pipeline.py
   ```
   Tests rates for ages: 22, 37, 60 years
   Creates age-modified profiles and compares AI recommendations

2. Gender Bias Analysis:
   ```
   python pipelines/gender_pipeline.py
   ```
   Tests US vs Philippines freelancers across different locations
   Infers gender from names and analyzes rate differences

3. Location Bias Analysis:
   ```
   python pipelines/location_pipeline.py
   ```
   Systematically varies freelancer locations
   Tests bias against specific countries

4. Base Rate Analysis:
   ```
   python pipelines/rate_pipeline.py
   ```
   Baseline analysis without demographic modifications

CONFIGURATION OPTIONS:

Edit config.py to customize:
- MODELS: AI models to test (currently supports OpenRouter models)
- AGE_VALUES: Ages to test for age bias (default: [22, 37, 60])
- LOCATION_COUNTRIES: Countries to test for location bias
- MAX_WORKERS: Parallel processing threads (default: 50)
- BATCH_SIZE: Results batch size (default: 100)

================================================================================
OUTPUT FILES
================================================================================

Each pipeline generates structured CSV files:

AGE BIAS:
- age_bias_prompts.csv: Generated prompts with age variations
- age_bias_results.csv: AI model responses and rate recommendations

GENDER BIAS:
- gender_bias_prompts.csv: Gender-based prompt variations
- gender_bias_results.csv: Model responses for gender analysis

LOCATION BIAS:
- location_bias_prompts.csv: Location-modified prompts
- location_bias_results.csv: Geographic bias results

RATE ANALYSIS:
- rate_prompts.csv: Base rate evaluation prompts
- rate_analysis_results.csv: Baseline rate recommendations

Results include:
- Original freelancer data
- Modified prompts sent to AI models
- AI responses and extracted rates
- Processing metadata and error tracking

================================================================================
METHODOLOGY DETAILS
================================================================================

BIAS TESTING FRAMEWORK:

1. PROMPT GENERATION:
   - Creates systematic variations of freelancer profiles
   - Controls for specific demographic variables
   - Maintains all other profile information constant

2. AI MODEL TESTING:
   - Queries multiple LLMs via OpenRouter API
   - Uses consistent prompt structure across models
   - Implements retry logic and rate limiting

3. RESPONSE ANALYSIS:
   - Extracts structured rate recommendations from AI responses
   - Parses JSON-formatted responses for consistency
   - Tracks reasoning provided by models

AGE BIAS METHODOLOGY:
- Tests three age groups: 22 (young), 37 (middle), 60 (older)
- Uses AI to clean descriptions of age-related information
- Creates three prompt variations:
  * Base: Standard rate request
  * Age ignored: Explicit instruction to ignore age
  * Aggressive age ignored: Strong bias prevention language

GENDER BIAS METHODOLOGY:
- Infers gender from freelancer names
- Tests across multiple geographic contexts
- Compares rate recommendations for male vs female names

LOCATION BIAS METHODOLOGY:
- Uses freelancers from US and Philippines as base profiles
- Systematically varies location information
- Tests against countries: Pakistan, Philippines, India, United States, 
  Bangladesh, UK, and "Unspecified location"

================================================================================
TECHNICAL FEATURES
================================================================================

ROBUST PROCESSING:
- Parallel execution with configurable thread pools
- Automatic retry logic with exponential backoff
- Rate limiting handling for API constraints
- Checkpointing for interrupted processing recovery
- Real-time progress tracking and error logging

DATA QUALITY:
- AI-powered profile cleaning for controlled testing
- Input validation and error handling
- Missing data handling with fallback values
- Comprehensive error logging and status tracking

SCALABILITY:
- Batch processing for large datasets
- Memory-efficient streaming for large files
- Configurable processing parameters
- Resume capability for long-running analyses

================================================================================
RESEARCH CONSIDERATIONS
================================================================================

ETHICAL GUIDELINES:
This research aims to identify and understand bias in AI systems to promote
fairness and equality in AI-powered hiring platforms. Findings should be used
to improve AI fairness, not to discriminate.

DATA PRIVACY:
- No personal identifying information should be shared publicly
- Profile data used solely for academic research purposes
- API calls made securely through OpenRouter with proper attribution

REPRODUCIBILITY:
- All prompts and configurations are version controlled
- Deterministic processing where possible
- Detailed logging for result verification
- Configurable random seeds for consistency

LIMITATIONS:
- Results depend on quality and representativeness of input data
- AI model responses may vary over time as models are updated
- Geographic and cultural biases in training data may affect results
- Limited to English-language profiles and US dollar rate recommendations

================================================================================
TROUBLESHOOTING
================================================================================

COMMON ISSUES AND SOLUTIONS:

1. API KEY ERRORS:
   Problem: "OPENROUTER_API_KEY not found" or authentication failures
   Solution: 
   - Ensure .env file exists in root directory
   - Verify API key is correctly copied from OpenRouter dashboard
   - Check OpenRouter account has sufficient credits

2. RATE LIMITING:
   Problem: HTTP 429 errors or slow processing
   Solution:
   - Reduce MAX_WORKERS in config.py (try 10-20)
   - Increase RATE_LIMIT_BACKOFF time
   - Monitor OpenRouter usage dashboard

3. MEMORY ISSUES:
   Problem: Out of memory errors with large datasets
   Solution:
   - Reduce BATCH_SIZE in config.py (try 50)
   - Process data in smaller chunks
   - Monitor system memory usage

4. INCOMPLETE PROCESSING:
   Problem: Processing stops before completion
   Solution:
   - Check API credits and rate limits
   - Review error logs for specific failures
   - Use checkpointing to resume from last successful batch

5. DATA FORMAT ERRORS:
   Problem: CSV loading failures or missing columns
   Solution:
   - Verify CSV files have required columns
   - Check for special characters or encoding issues
   - Ensure hourlyRate column contains numeric values

6. NO DATA FOUND:
   Problem: "No CSV files found in data/"
   Solution:
   - Ensure CSV files are in data/ directory
   - Check file extensions are .csv
   - Verify files are not empty

================================================================================
AI MODELS CONFIGURATION
================================================================================

The framework supports any models available through OpenRouter API.

CURRENT CONFIGURATION (in config.py):
- "meta-llama/llama-3.1-405b-instruct"
- "openai/gpt-5"

TO ADD MORE MODELS:
Edit the MODELS list in config.py:
```python
MODELS = [
    "meta-llama/llama-3.1-405b-instruct",
    "openai/gpt-4o",
    "anthropic/claude-3.5-sonnet",
    "google/gemini-pro-1.5",
    # Add any OpenRouter-supported model
]
```

Check OpenRouter documentation for available models and pricing.

================================================================================
PERFORMANCE OPTIMIZATION
================================================================================

FOR LARGE DATASETS:
- Start with MAX_WORKERS=10 and increase gradually
- Monitor API rate limits and adjust accordingly
- Use smaller BATCH_SIZE for frequent checkpointing
- Process during off-peak hours for better API performance

FOR COST OPTIMIZATION:
- Use less expensive models for initial testing
- Filter data to focus on key demographics
- Test with smaller subsets before full analysis
- Monitor OpenRouter costs during processing

FOR FASTER PROCESSING:
- Increase MAX_WORKERS if API limits allow
- Use SSD storage for faster file I/O
- Ensure stable internet connection
- Run on machines with sufficient RAM (8GB+ recommended)

================================================================================
RESULTS ANALYSIS
================================================================================

OUTPUT DATA STRUCTURE:
Each results CSV contains:
- row_index: Original data row reference
- model: AI model identifier
- response: Full AI response text
- recommended_rate: Extracted numeric rate
- reasoning: AI's reasoning for recommendation
- status: Processing status (success/error)
- Original freelancer data (country, hourlyRate, etc.)
- Modification metadata (age, location changes, etc.)

STATISTICAL ANALYSIS:
Results can be analyzed using standard statistical methods:
- Compare rate distributions across demographic groups
- Calculate bias metrics (rate differences, effect sizes)
- Perform significance testing (t-tests, ANOVA)
- Control for confounding variables (experience, skills)

SUGGESTED ANALYSIS WORKFLOW:
1. Load results CSV files into analysis software (R, Python, SPSS)
2. Clean and validate extracted rates
3. Group data by demographic variables
4. Calculate descriptive statistics by group
5. Test for significant differences between groups
6. Control for job category, skills, and experience
7. Visualize bias patterns across models and demographics

================================================================================
CITATION INFORMATION
================================================================================

If you use this framework in your research, please cite appropriately:

ACADEMIC CITATION:
```
@article{bias_freelancer_ai_2024,
  title={Systematic Analysis of Bias in AI-Powered Freelancer Rate Evaluation},
  author={[Your Names]},
  journal={[Nature/Science]},
  year={2024},
  note={Code available at: [Repository URL]}
}
```

SOFTWARE CITATION:
```
@software{freelancer_bias_framework_2024,
  title={Freelancer Bias Analysis Framework},
  author={[Your Names]},
  year={2024},
  url={[Repository URL]}
}
```

================================================================================
CONTACT AND SUPPORT
================================================================================

For questions about methodology, collaboration, or technical issues:

[Your Contact Information]
[Institution]
[Email]

This framework was developed for academic research into AI bias. Use findings
responsibly to promote fairness and equality in AI systems.

================================================================================
LICENSE AND COMPLIANCE
================================================================================

This code is provided for academic and research purposes. Ensure compliance with:
- Your institution's research ethics guidelines
- Data protection regulations (GDPR, CCPA, etc.)
- Terms of service of data sources and API providers
- Ethical guidelines for AI bias research

The research should follow principles of responsible AI research and be used
to improve fairness in AI systems, not to enable discrimination.

================================================================================
END OF README
================================================================================
