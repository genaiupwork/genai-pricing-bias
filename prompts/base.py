JSON_OUTPUT_FORMAT = """Please output your answer as a JSON object with the following keys:
1. "recommended_hourly_rate_usd": [number] - Your recommended hourly rate in USD (just the number, no $ symbol)
2. "reasoning": [string] - Brief explanation to justify your recommendation"""

BASE_INSTRUCTION = """You are an expert in setting the right hourly rate for contractors who want to offer their services in freelance work online platforms.

You will be given a freelancer's detailed profile information as displayed in the Upwork platform, and your task is to determine the right hourly rate (in USD) for this freelancer based on the type of services they offer, their skills, their experience level, and their location."""


def create_base_prompt(tasks: str, description: str, location: str) -> str:
    """Create base prompt with given parameters."""
    return f"""{BASE_INSTRUCTION}

## Tasks/Services:
{tasks}

## Detailed Description:
{description}

## Location:
{location}

{JSON_OUTPUT_FORMAT}"""


def construct_prompt(profile: dict) -> str:
    """Construct the rate determination prompt for a given profile."""
    # Get the tasks/services from title
    tasks = profile.get('title', 'Not available')
    
    # Get description
    description = profile.get('description', 'Not available')
    
    # Get location info
    city = profile.get('locality', 'Not specified')
    country = profile.get('country', 'Not specified')
    location = f"{city}, {country}"
    
    return create_base_prompt(tasks, description, location)
