import json
import os
import requests
from typing import List, Dict
from pathlib import Path
from pydantic import BaseModel

# For this example, we mock the LLM call, but it should be powered by Gemini/OpenAI
# You can swap this out with actual API calls once we decide on the provider.

class InitialTopic(BaseModel):
    title: str
    source: str

def fetch_trending_topics() -> List[InitialTopic]:
    """
    Scouts for topics. 
    In the real world, this could hit Reddit, HackerNews, or YouTube RSS feeds.
    For now, we fetch a few tech news headlines or return a diverse static list to start the pipeline.
    """
    # Mocked fetched topics, replacing web search for now
    return [
        InitialTopic(title="Why Blackwell Architecture Changes Everything", source="Mock Tech News"),
        InitialTopic(title="Top 10 Budget Setup Keyboards", source="Mock Reddit"),
        InitialTopic(title="Understanding HBM Memory in modern GPUs", source="Mock Arxiv")
    ]

def evaluate_topic(topic: InitialTopic, identity: dict) -> Dict:
    """
    Uses an LLM (mocked here temporarily) to score if a topic fits the channel identity.
    """
    # Here is what the prompt to the LLM would look like:
    prompt = f"""
    You are evaluating a potential YouTube video topic.
    Channel Niche: {identity['niche']}
    Tone: {identity['tone']}
    Allowed Zones: {', '.join(identity['allowed_topic_zones'])}
    Unwanted Zones: {', '.join(identity['unwanted_topic_zones'])}
    
    Topic: {topic.title}
    
    Score this from 0 to 100 on how well it fits. 
    """
    
    # Mock evaluation logic based on keywords
    title_lower = topic.title.lower()
    score = 0
    if "keyboard" in title_lower or "budget" in title_lower:
        score = 10
    elif "gpu" in title_lower or "architecture" in title_lower or "hbm" in title_lower:
        score = 95
        
    return {"topic": topic.title, "score": score, "source": topic.source}


def run_scout_phase(identity_path: Path):
    with open(identity_path, "r", encoding="utf-8") as f:
        identity = json.load(f)
        
    print("Scouting for topics...")
    raw_topics = fetch_trending_topics()
    
    scored_topics = []
    print("Filtering topics using Identity...")
    for t in raw_topics:
        eval_result = evaluate_topic(t, identity)
        scored_topics.append(eval_result)
        print(f" - [{eval_result['score']}/100] {t.title}")
        
    # Sort and pick the winner
    scored_topics.sort(key=lambda x: x['score'], reverse=True)
    winner = scored_topics[0]
    
    if winner["score"] > 80:
        print(f"\n✅ Winning Topic Selected: {winner['topic']}")
        return winner
    else:
        print("\n❌ No suitable topics found.")
        return None

if __name__ == "__main__":
    winner = run_scout_phase(Path("brain/identity.json"))
