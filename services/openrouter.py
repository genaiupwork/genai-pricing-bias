import json
import time
import random
import threading
import requests
from typing import Optional, Dict, Any
import re

import config


def create_session():
    """Create a new requests session with headers."""
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": config.SITE_URL,
        "X-Title": config.SITE_NAME
    })
    return session


def parse_response(content: str) -> tuple[Optional[float], Optional[str]]:
    """Parse AI response to extract recommended rate and reasoning."""
    try:
        json_match = re.search(r'\{[^}]+\}', content, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            return parsed.get('recommended_hourly_rate_usd'), parsed.get('reasoning')
    except (json.JSONDecodeError, AttributeError):
        pass
    return None, None


def call_api(prompt: str, model: str, row_index: int) -> Optional[Dict[str, Any]]:
    """Make API call with retry logic."""
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 1000
    }
    
    for attempt in range(config.MAX_RETRIES):
        try:
            session = create_session()
            time.sleep(0.05 * random.random())  
            
            response = session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                data=json.dumps(data),
                timeout=config.API_TIMEOUT
            )
            
            session.close()
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                recommended_rate, reasoning = parse_response(content)
                
                return {
                    'row_index': row_index,
                    'model': model,
                    'response': content,
                    'recommended_rate': recommended_rate,
                    'reasoning': reasoning,
                    'status': 'success'
                }
            
            elif response.status_code == 429:
                wait_time = min(30 * (2 ** attempt), config.RATE_LIMIT_BACKOFF)
                time.sleep(wait_time * random.uniform(0.8, 1.2))
                continue
            
            elif response.status_code >= 500:
                wait_time = min(5 * (2 ** attempt), 60)
                time.sleep(wait_time * random.uniform(0.8, 1.2))
                continue
            
            else:
                return {
                    'row_index': row_index,
                    'model': model,
                    'response': None,
                    'recommended_rate': None,
                    'reasoning': None,
                    'status': f'error_{response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            wait_time = min(5 * (2 ** attempt), 30)
            time.sleep(wait_time * random.uniform(0.8, 1.2))
            continue
            
        except Exception as e:
            if attempt == config.MAX_RETRIES - 1:
                return {
                    'row_index': row_index,
                    'model': model,
                    'response': None,
                    'recommended_rate': None,
                    'reasoning': None,
                    'status': f'error_{str(e)}'
                }
            time.sleep(1 + random.random())
            continue
    
    return {
        'row_index': row_index,
        'model': model,
        'response': None,
        'recommended_rate': None,
        'reasoning': None,
        'status': 'max_retries_exceeded'
    }