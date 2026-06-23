import json
import logging
from cosmos_prompter import CosmosPrompter
from cosmos_engine import CosmosEngineStub

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Step 1 Validation: Scene 1 Generation ONLY")
    
    with open("storyboard.json", "r") as f:
        storyboard = json.load(f)

    # Extract only Scene 1 (p1)
    scene1_panel = next((p for p in storyboard.get("panels", []) if p["id"] == "p1"), None)
    if not scene1_panel:
        raise ValueError("Could not find panel p1 in storyboard.json")

    prompter = CosmosPrompter()
    engine = CosmosEngineStub(mode="text2video")
    
    prompt = prompter.generate_prompt(scene1_panel)
    
    try:
        output_path = engine.generate_video(prompt, scene1_panel["id"])
        logger.info(f"\n==========================================")
        logger.info(f"SUCCESS! Scene 1 Video Generated: {output_path}")
        logger.info(f"==========================================")
        logger.info("Please manually review the .mp4 file to evaluate visual quality and prompt adherence.")
    except Exception as e:
        logger.error(f"Failed to generate Scene 1: {e}")

if __name__ == "__main__":
    main()
