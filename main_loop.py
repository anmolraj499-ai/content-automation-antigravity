import os
import sys
import argparse
from pathlib import Path

# Important: Load env before anything else
from pipeline.api_clients import load_env
load_env()

from pipeline.scout import run_scout_phase
from pipeline.researcher import run_research_phase
from pipeline.planner import run_planner_phase
from pipeline.schema import VideoPlan
from pipeline.render_engine import build_video_from_plan

def main():
    parser = argparse.ArgumentParser(description="Autonomous Content Pipeline Loop")
    parser.add_argument("--skip-render", action="store_true", help="Skip the actual video generation phase (useful if TTS isn't setup)")
    args = parser.parse_args()

    print("====================================")
    print("🚀 INIT: Autonomous Content Machine")
    print("====================================")

    # Step 1: Scout & Filter
    identity_path = Path("brain/identity.json")
    if not identity_path.exists():
        print("Error: identity.json not found in brain/")
        sys.exit(1)

    print("\n[PHASE 1] Checking for Topics...")
    winning_topic = run_scout_phase(identity_path)
    if not winning_topic:
        print("Pipeline stopped: No valid topics found matching channel identity.")
        sys.exit(0)
        
    topic_title = winning_topic["topic"]
    topic_slug = "".join(c if c.isalnum() else "_" for c in topic_title.lower()).strip("_")

    # Step 2: Research
    print("\n[PHASE 2] Researching Facts...")
    research_data = run_research_phase(topic_title)

    # Step 3: Planner
    print("\n[PHASE 3] Generating Scene Plan...")
    scene_json = run_planner_phase(research_data, topic_slug)
    
    # Optional Step 4: Render
    if args.skip_render:
        print("\n[PHASE 4] Render skipped via flag. Scene JSON is ready in brain/plans/")
    else:
        print("\n[PHASE 4] Rendering Video...")
        # Since we don't have Piper binaries specified dynamically here yet, this will fail
        # if Piper isn't setup on the system.
        try:
            plan = VideoPlan(**scene_json)
            work_dir = Path("work") / topic_slug
            work_dir.mkdir(parents=True, exist_ok=True)
            output_file = Path("render") / f"{topic_slug}.mp4"
            
            # Temporary dummy piper args assuming they exist on the C drive root
            piper_args = {
                "bin": "piper",
                "model": Path("models/dummy.onnx"),
                "config": Path("models/dummy.json")
            }
            
            # This calls the method from render_engine.py
            build_video_from_plan(plan, work_dir, output_file, piper_args)
            print(f"✅ Video successfully rendered: {output_file}")
        except Exception as e:
            print(f"⚠️ Render failed (Missing Piper Setup?): {e}")

    print("\n====================================")
    print("🏁 PIPELINE RUN COMPLETE")
    print("====================================")

if __name__ == "__main__":
    main()
