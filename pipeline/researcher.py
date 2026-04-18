import json
from pathlib import Path
from pipeline.api_clients import call_tavily

def run_research_phase(topic_title: str) -> dict:
    """
    Uses Tavily Search to gather deep, factual context about the given topic.
    Returns a unified research object to be ingested by the Planner LLM.
    """
    print(f"Researching factual data using Tavily for: '{topic_title}'")
    
    # We query Tavily for high-quality deep results.
    research_query = f"In-depth analysis, architecture details, and impact of {topic_title}"
    try:
        tavily_results = call_tavily(research_query, search_depth="advanced")
    except Exception as e:
        print(f"Failed to fetch research from Tavily. Error: {e}")
        return {"topic": topic_title, "summary": "Failed to fetch.", "facts": []}

    # Extract the AI-generated answer and the links
    summary = tavily_results.get("answer", "No direct answer provided by search.")
    
    facts = []
    for result in tavily_results.get("results", []):
        facts.append({
            "title": result.get("title"),
            "url": result.get("url"),
            "content": result.get("content")
        })

    compiled_research = {
        "topic": topic_title,
        "overall_summary": summary,
        "key_facts": facts
    }
    
    # Save the research locally to 'research/topic_name.json'
    safe_title = "".join(c if c.isalnum() else "_" for c in topic_title).strip("_")
    out_dir = Path("research")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{safe_title}.json"
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(compiled_research, f, indent=4)
        
    print(f"Research compiled and saved to {out_file}")
    return compiled_research

if __name__ == "__main__":
    # Test block
    res = run_research_phase("Nvidia Blackwell Architecture GPU")
