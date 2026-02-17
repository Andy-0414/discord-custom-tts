import torch
import soundfile as sf
from pathlib import Path
from typing import Optional, Tuple
import logging

from qwen_tts import Qwen3TTSModel
import config

logger = logging.getLogger(__name__)


class TTSEngine:
    """Qwen3-TTS Voice Clone Engine"""
    
    def __init__(self):
        self.model: Optional[Qwen3TTSModel] = None
        self.device = config.DEVICE
        self.model_name = config.MODEL_NAME
        
    def load_model(self):
        """Load Qwen3-TTS model (called once at startup)"""
        if self.model is not None:
            logger.info("Model already loaded")
            return
            
        logger.info(f"Loading Qwen3-TTS model: {self.model_name} on {self.device}")
        
        try:
            self.model = Qwen3TTSModel.from_pretrained(
                self.model_name,
                device_map=self.device,
                dtype=torch.bfloat16,
                attn_implementation="flash_attention_2",
            )
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _get_voice_files(self, voice_name: str) -> Tuple[Path, Path]:
        """Get reference audio and text files for a voice profile"""
        voice_dir = config.VOICES_DIR / voice_name
        ref_audio = voice_dir / "reference.wav"
        ref_text = voice_dir / "reference.txt"
        
        if not ref_audio.exists():
            raise FileNotFoundError(f"Reference audio not found: {ref_audio}")
        if not ref_text.exists():
            raise FileNotFoundError(f"Reference text not found: {ref_text}")
            
        return ref_audio, ref_text
    
    def generate(self, text: str, voice_name: str = None, output_path: Path = None) -> Path:
        """
        Generate speech using voice cloning
        
        Args:
            text: Text to synthesize
            voice_name: Voice profile name (default: config.DEFAULT_VOICE)
            output_path: Output file path (default: temp/output_{timestamp}.wav)
            
        Returns:
            Path to generated audio file
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        voice_name = voice_name or config.DEFAULT_VOICE
        
        # Get reference files
        ref_audio_path, ref_text_path = self._get_voice_files(voice_name)
        ref_text = ref_text_path.read_text(encoding="utf-8").strip()
        
        # Generate output path
        if output_path is None:
            import time
            timestamp = int(time.time() * 1000)
            output_path = config.TEMP_DIR / f"output_{timestamp}.{config.AUDIO_FORMAT}"
        
        logger.info(f"Generating TTS: '{text[:50]}...' using voice '{voice_name}'")
        
        try:
            # Generate voice clone
            wavs, sr = self.model.generate_voice_clone(
                text=text,
                language="Korean",
                ref_audio=str(ref_audio_path),
                ref_text=ref_text,
            )
            
            # Save audio
            sf.write(str(output_path), wavs[0], sr)
            logger.info(f"Audio saved to {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate TTS: {e}")
            raise
    
    def unload_model(self):
        """Unload model to free GPU memory"""
        if self.model is not None:
            del self.model
            self.model = None
            torch.cuda.empty_cache()
            logger.info("Model unloaded")
