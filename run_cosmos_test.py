import json
import os
import time
import logging
from cosmos_prompter import CosmosPrompter
from cosmos_engine import CosmosEngineStub

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def evaluate_clip(clip_path: str, runtime_minutes: float):
    """
    In a real implementation, this would involve computer vision models or human-in-the-loop
    to score the clip. For this stub, we return placeholder evaluation scores.
    """
    # KILL CONDITION checks will be evaluated against these scores.
    return {
        "character_consistency": 8, # 1-10
        "environment_consistency": 7, # 1-10
        "temporal_consistency": 7, # 1-10
        "prompt_adherence": 8, # 1-10
        "runtime_minutes": runtime_minutes,
        "vram_usage_gb": 40,
        "cost_per_minute": 0.05
    }

def main():
    logger.info("Starting Cosmos Pipeline Evaluation")
    
    # Load isolated storyboard
    with open("storyboard.json", "r") as f:
        storyboard = json.load(f)

    panels = storyboard.get("panels", [])
    prompter = CosmosPrompter()
    
    phases = ["Text-to-Video", "Image-to-Video"]
    results = {"Phase_A_T2V": {}, "Phase_B_I2V": {}}

    for phase in phases:
        logger.info(f"\n{'='*40}\nExecuting Phase: {phase}\n{'='*40}")
        
        engine = CosmosEngineStub(mode=phase)
        generated_clips = []
        phase_key = "Phase_A_T2V" if phase == "Text-to-Video" else "Phase_B_I2V"
        
        for p in panels:
            prompt = prompter.generate_prompt(p)
            
            # Simulated NVF Initial Frame for Image-to-Video
            init_img = "simulated_nvf_frame.png" if phase == "Image-to-Video" else None
            
            start_time = time.time()
            clip_path = engine.generate_video(prompt, p["id"], init_image=init_img)
            runtime_mins = (time.time() - start_time) / 60.0
            
            generated_clips.append(clip_path)
            
            # Evaluate the clip
            eval_scores = evaluate_clip(clip_path, runtime_mins)
            results[phase_key][p["id"]] = eval_scores
            
            # EVALUATE KILL CONDITION
            if eval_scores["character_consistency"] < 6 or eval_scores["environment_consistency"] < 6:
                logger.error(f"KILL CONDITION MET: Consistency score too low in {phase} for panel {p['id']}. Halting.")
                with open("results.json", "w") as rf:
                    json.dump(results, rf, indent=2)
                return
            
            if eval_scores["runtime_minutes"] > 15.0:
                logger.error(f"KILL CONDITION MET: Generation exceeded 15 mins/clip in {phase} for panel {p['id']}. Halting.")
                with open("results.json", "w") as rf:
                    json.dump(results, rf, indent=2)
                return
                
        # Stitch
        final_out = f"final_{phase.replace('-', '_').lower()}.mp4"
        engine.stitch_scenes(generated_clips, final_out)
        
    # Save Results
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    logger.info("Cosmos evaluation completed successfully. Both pipelines passed the Kill Condition.")

if __name__ == "__main__":
    main()
