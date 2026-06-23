import json

class CosmosPrompter:
    """
    Translates static storyboard panels into Cosmos-optimized video prompts.
    Focuses on camera dynamics, temporal motion, and heavy character weighting.
    """
    def __init__(self):
        self.base_style = "High-fidelity, cinematic, detailed manhwa style, high quality."

    def generate_prompt(self, panel: dict) -> str:
        camera = self._get_camera_action(panel.get("shot_type", "medium_shot"))
        action = self._enhance_action(panel.get("description", ""))
        characters = ", ".join(panel.get("characters", []))
        location = panel.get("location", "unknown location")
        
        # Cosmos 3 requires structured temporal descriptions
        prompt = f"{camera}. {action}. Characters: {characters}. Location: {location}. {self.base_style}"
        return prompt

    def _get_camera_action(self, shot_type: str) -> str:
        shot_map = {
            "establishing_shot": "Slow drone panning shot across the environment",
            "wide_shot": "Wide cinematic tracking shot",
            "medium_shot": "Stable medium shot focusing on subject movement",
            "close_up": "Intimate close-up shot with shallow depth of field",
            "extreme_close_up": "Macro extreme close-up highlighting subtle facial expressions",
            "over_shoulder": "Over-the-shoulder tracking shot"
        }
        return shot_map.get(shot_type.lower(), "Stable tracking shot")

    def _enhance_action(self, description: str) -> str:
        # Cosmos works best with explicit verb-driven motion
        # For a production pipeline, this would invoke an LLM. For the PoC, we pass it through.
        return description
