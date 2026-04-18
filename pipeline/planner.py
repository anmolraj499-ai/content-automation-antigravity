import json
from pathlib import Path
from pipeline.api_clients import call_openrouter

def run_planner_phase(research_data: dict, project_slug: str) -> dict:
    """
    Feeds the research data to the LLM via OpenRouter and asks it to plan a video layout (scene.json format).
    """
    print(f"Planning Video Scenes using OpenRouter LLM for: '{project_slug}'")
    
    sys_prompt = """
    You are an expert YouTube video director and scriptwriter for a deeply technical channel.
    Your job is to read raw research data and output a structured VideoPlan.
    
    Your response MUST be identical to the following JSON schema format:
    {
      "project_name": "slug_name",
      "scenes": [
        {
          "id": 1,
          "narration": "Text to be spoken by narrator.",
          "visual_text": "Text to be displayed on the slide.",
          "visual_type": "title_slide"
        }
      ]
    }
    
    Important rules:
    - visual_type must be either 'title_slide' or 'bullet_slide'.
    - narration must be highly engaging, factual, and concise.
    - Make sure the JSON is perfectly valid. Do not wrap it in markdown block quotes.
    """
    
    user_prompt = f"""
    Please generate a video plan based on these facts:
    
    Topic: {research_data.get('topic')}
    Summary: {research_data.get('overall_summary')}
    
    Raw Facts:
    {json.dumps(research_data.get('key_facts'), indent=2)}
    
    Create a 3 to 5 scene script layout.
    """
    
    response_text = call_openrouter(sys_prompt, user_prompt, is_json=True)
    
    # Strip markdown block quotes if they exist
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
        
    try:
        scene_json = json.loads(response_text)
    except json.JSONDecodeError as e:
        print("LLM returned malformed JSON. You will need to implement a retry mechanism here for production.")
        raise e
        
    # Save the output
    out_dir = Path("brain") / "plans"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{project_slug}_scenes.json"
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(scene_json, f, indent=4)
        
    print(f"Video plan generated and saved to {out_file}")
    return scene_json

if __name__ == "__main__":
    # Test block
    dummy_research = {"topic": "Test", "overall_summary": "Testing OpenRouter", "key_facts": []}
    run_planner_phase(dummy_research, "test_slug")
