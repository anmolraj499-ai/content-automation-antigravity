import os
import json
import requests
from typing import Dict, Any

# Simple dotenv loader since we might not have python-dotenv installed
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, val = line.strip().split('=', 1)
                    os.environ[key] = val

load_env()

def call_openrouter(sys_prompt: str, user_prompt: str, is_json: bool = False) -> str:
    """
    Calls the OpenRouter API with the desired model.
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    # Default to Gemini 1.5 Pro if not specified
    model = os.environ.get("OPENROUTER_MODEL", "google/gemini-pro-1.5")
    
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in .env")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/anmolraj499-ai/ai-content-automation",
        "X-Title": "AI Content Automation Pipeline"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    
    # We ask for JSON response format if specified
    if is_json:
         payload["response_format"] = {"type": "json_object"}

    res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )
    res.raise_for_status()
    data = res.json()
    return data['choices'][0]['message']['content']


def call_tavily(query: str, search_depth: str = "advanced") -> Dict[str, Any]:
    """
    Calls the Tavily API to gather realtime facts and research.
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in .env")

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": search_depth,
        "include_answer": True,
        "include_raw_content": False,
        "max_results": 5
    }

    res = requests.post(
        "https://api.tavily.com/search",
        json=payload
    )
    res.raise_for_status()
    return res.json()
