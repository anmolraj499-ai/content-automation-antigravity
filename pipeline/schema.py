from typing import List, Optional
from pydantic import BaseModel, Field

class Scene(BaseModel):
    id: int = Field(description="Sequential ID of the scene")
    narration: str = Field(description="The exact text to be spoken by the TTS engine for this scene.")
    visual_text: str = Field(description="The text to be displayed on the screen.")
    visual_type: str = Field(description="The type of visual template to use. Examples: 'title_slide', 'bullet_slide'")
    duration: Optional[float] = Field(default=None, description="Duration in seconds. Usually inferred from TTS output.")

class VideoPlan(BaseModel):
    project_name: str = Field(description="The identifier / slug for the project.")
    scenes: List[Scene] = Field(description="The ordered list of scenes making up the video.")
