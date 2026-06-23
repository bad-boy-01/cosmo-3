import os
import time
import logging
import subprocess
import torch
import gc
from diffusers import LTXPipeline
from diffusers.utils import export_to_video

logger = logging.getLogger(__name__)

class CosmosEngineStub:
    """
    REAL IMPLEMENTATION: Nvidia Cosmos Engine Adapter using LTX-Video.
    Named CosmosEngineStub for backward compatibility with the run script, 
    but this now performs REAL inference via Diffusers.
    """
    def __init__(self, mode="text2video"):
        self.mode = mode
        self.output_dir = "cosmos_outputs"
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.pipe = None
        self.model_id = "Lightricks/LTX-Video"

    def _load_model(self):
        if self.pipe is None:
            logger.info(f"Loading REAL {self.model_id} model...")
            self.pipe = LTXPipeline.from_pretrained(self.model_id, torch_dtype=torch.bfloat16)
            
            # Aggressive Memory Optimizations
            self.pipe.enable_model_cpu_offload()
            try:
                self.pipe.enable_xformers_memory_efficient_attention()
            except:
                pass
            try:
                self.pipe.enable_vae_slicing()
                self.pipe.enable_vae_tiling()
                self.pipe.enable_attention_slicing()
            except:
                pass
            logger.info("Model loaded and optimized.")

    def generate_video(self, prompt: str, scene_id: str, init_image: str = None) -> str:
        """
        Executes REAL inference for a 5-second video clip.
        """
        self._load_model()
        logger.info(f"Generating video for {scene_id}. Prompt: {prompt}")
        
        start_time = time.time()
        
        # Free memory before generation
        torch.cuda.empty_cache()
        gc.collect()

        try:
            # Generate 73 frames (approx 3 seconds at 24fps) at 512x512
            video_frames = self.pipe(
                prompt=prompt,
                negative_prompt="worst quality, inconsistent, blurry, deformed",
                width=512,
                height=512,
                num_frames=73,
                num_inference_steps=30,
            ).frames[0]
        except Exception as e:
            logger.error(f"Inference crashed: {e}")
            raise e

        output_path = os.path.join(self.output_dir, f"{scene_id}_cosmos.mp4")
        
        # Diagnostic 1: Pre-write path verification
        logger.info(f"Output path generated: {output_path}")
        
        # Write real MP4
        export_to_video(video_frames, output_path, fps=24)
        
        # Diagnostic 2: Size Check
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Video generation failed: File {output_path} does not exist!")
            
        file_size_kb = os.path.getsize(output_path) / 1024
        logger.info(f"Output size: {file_size_kb:.2f} KB")
        
        if file_size_kb < 100:
            raise ValueError(f"Video generation failed: File is suspiciously small ({file_size_kb:.2f} KB).")

        # Diagnostic 3: FFprobe verification
        try:
            subprocess.run(["ffprobe", output_path], capture_output=True, text=True, check=True)
            logger.info("FFprobe validation: SUCCESS")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Video generation failed: FFprobe rejected the file as corrupt.\nFFprobe Error: {e.stderr}")
        except FileNotFoundError:
            logger.warning("FFprobe not installed in system PATH. Skipping stream validation, but file exists and meets size threshold.")

        return output_path

    def stitch_scenes(self, video_paths: list, final_output: str) -> str:
        # Stub for stitching remains until we validate Step 1
        return final_output
