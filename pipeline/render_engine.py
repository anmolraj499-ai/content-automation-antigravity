import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Support for older PIL versions
if not hasattr(Image, "ANTIALIAS") and hasattr(Image, "Resampling"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from moviepy.editor import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    concatenate_videoclips,
)

from pipeline.schema import VideoPlan, Scene

def run(cmd, **kwargs):
    subprocess.run(cmd, check=True, **kwargs)

def make_audio(piper_bin: str, model: Path, config: Path, script_text: str, out_wav: Path):
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    run(
        [piper_bin, "--model", str(model), "--config", str(config), "--output_file", str(out_wav)],
        input=script_text.encode("utf-8"),
    )

def create_slide(text: str, slide_type: str, out_png: Path, w: int = 1080, h: int = 1920):
    # For now, a very basic PIL generation
    img = Image.new("RGB", (w, h), color=(12, 14, 20))
    d = ImageDraw.Draw(img)
    
    # Try to load a font, otherwise fallback to default
    try:
        # standard windows font
        font_large = ImageFont.truetype("arialbd.ttf", 80)
        font_small = ImageFont.truetype("arial.ttf", 60)
    except IOError:
        font_large = ImageFont.load_default()
        font_small = font_large
    
    # Simple text wrapping and rendering. Real version needs textwrap.
    import textwrap
    lines = textwrap.wrap(text, width=25)
    
    y = h // 2 - (len(lines) * 90) // 2
    for line in lines:
        # Use simple text bounding box to center text
        bbox = d.textbbox((0, 0), line, font=font_large)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (w - text_w) / 2
        d.text((x, y), line, fill=(255, 255, 255), font=font_large)
        y += text_h + 20
        
    img.save(out_png)

def build_video_from_plan(plan: VideoPlan, work_dir: Path, output_file: Path, piper_args: dict, w: int = 1080, h: int = 1920):
    frames = []
    
    for scene in plan.scenes:
        # 1. Generate Audio per scene
        wav_path = work_dir / f"scene_{scene.id}.wav"
        make_audio(
            piper_args["bin"],
            piper_args["model"],
            piper_args["config"],
            scene.narration,
            wav_path
        )
        
        # Determine duration
        audio_clip = AudioFileClip(str(wav_path))
        duration = audio_clip.duration
        
        # 2. Generate Slide per scene
        png_path = work_dir / f"scene_{scene.id}.png"
        create_slide(scene.visual_text, scene.visual_type, png_path, w, h)
        
        # 3. Create Video Frame
        img_clip = ImageClip(str(png_path)).set_duration(duration)
        frame = img_clip.set_audio(audio_clip)
        frames.append(frame)
        
    # 4. Concatenate and Render
    final_video = concatenate_videoclips(frames, method="compose")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    final_video.write_videofile(str(output_file), fps=30, codec="libx264", audio_codec="aac", preset="medium")
    
    # Cleanup memory
    final_video.close()
    for f in frames:
        f.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", required=True, help="Path to scene.json")
    parser.add_argument("--output", required=True, help="Output MP4 path")
    parser.add_argument("--model", required=True, help="Piper model path")
    parser.add_argument("--config", required=True, help="Piper config path")
    parser.add_argument("--piper-bin", default="piper")
    args = parser.parse_args()

    plan_path = Path(args.plan)
    with open(plan_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        plan = VideoPlan(**data)
        
    work_dir = Path("work") / plan.project_name
    work_dir.mkdir(parents=True, exist_ok=True)
    
    piper_args = {
        "bin": args.piper_bin,
        "model": Path(args.model),
        "config": Path(args.config)
    }
    
    build_video_from_plan(plan, work_dir, Path(args.output), piper_args)
    print("Video generation successfully completed.")

if __name__ == "__main__":
    main()
