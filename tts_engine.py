import torch
import soundfile as sf
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import logging

from qwen_tts import Qwen3TTSModel
import config

logger = logging.getLogger(__name__)


class TTSEngine:
    """Qwen3-TTS Voice Clone Engine with optimizations"""
    
    def __init__(self):
        self.model: Optional[Qwen3TTSModel] = None
        self.device = config.DEVICE
        self.model_name = config.MODEL_NAME
        self.voice_prompts: Dict[str, Any] = {}  # Cache for voice prompts
        self._compiled = False
        
    def load_model(self):
        """Load Qwen3-TTS model with optimizations"""
        if self.model is not None:
            logger.info("Model already loaded")
            return
            
        logger.info(f"Loading Qwen3-TTS model: {self.model_name} on {self.device}")
        
        try:
            # Try FlashAttention2 first, fallback to eager
            attn_impl = "eager"  # Default
            try:
                import flash_attn
                attn_impl = "flash_attention_2"
                logger.info("FlashAttention2 detected, using optimized attention")
            except ImportError:
                logger.info("FlashAttention2 not available, using eager mode")
            
            self.model = Qwen3TTSModel.from_pretrained(
                self.model_name,
                device_map=self.device,
                dtype=torch.bfloat16,
                attn_implementation=attn_impl,
            )
            
            # Enable PyTorch optimizations
            if hasattr(torch, 'compile'):
                logger.info("Compiling model with torch.compile()...")
                try:
                    self.model = torch.compile(self.model, mode="reduce-overhead")
                    self._compiled = True
                    logger.info("Model compiled successfully!")
                except Exception as e:
                    logger.warning(f"torch.compile() failed: {e}")
            
            # Enable CUDA optimizations
            if torch.cuda.is_available():
                torch.backends.cudnn.benchmark = True
                torch.backends.cuda.matmul.allow_tf32 = True
                torch.backends.cudnn.allow_tf32 = True
                logger.info("CUDA optimizations enabled")
            
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
    
    def _get_or_create_prompt(self, voice_name: str) -> Any:
        """Get cached voice prompt or create new one"""
        if voice_name in self.voice_prompts:
            logger.info(f"Using cached prompt for voice '{voice_name}'")
            return self.voice_prompts[voice_name]
        
        logger.info(f"Creating new voice prompt for '{voice_name}'")
        ref_audio_path, ref_text_path = self._get_voice_files(voice_name)
        ref_text = ref_text_path.read_text(encoding="utf-8").strip()
        
        prompt = self.model.create_voice_clone_prompt(
            ref_audio=str(ref_audio_path),
            ref_text=ref_text,
            x_vector_only_mode=False,
        )
        
        self.voice_prompts[voice_name] = prompt
        return prompt
    
    def generate(self, text: str, voice_name: str = None, output_path: Path = None) -> Path:
        """
        Generate speech using voice cloning with caching
        
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
        
        # Generate output path
        if output_path is None:
            import time
            timestamp = int(time.time() * 1000)
            output_path = config.TEMP_DIR / f"output_{timestamp}.{config.AUDIO_FORMAT}"
        
        logger.info(f"Generating TTS: '{text[:50]}...' using voice '{voice_name}'")
        
        try:
            # Get or create cached voice prompt (2x faster!)
            voice_prompt = self._get_or_create_prompt(voice_name)
            
            # Use autocast for mixed precision
            with torch.cuda.amp.autocast(dtype=torch.bfloat16):
                # Generate voice clone with cached prompt
                wavs, sr = self.model.generate_voice_clone(
                    text=text,
                    language="Korean",
                    voice_clone_prompt=voice_prompt,
                )
            
            # Save audio
            sf.write(str(output_path), wavs[0], sr)
            logger.info(f"Audio saved to {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate TTS: {e}")
            raise
    

    async def generate_streaming(self, text: str, voice_name: str = None):
        """Generate speech in streaming mode with optimizations"""
        import asyncio
        if self.model is None:
            raise RuntimeError("Model not loaded")
        
        voice_name = voice_name or config.DEFAULT_VOICE
        voice_prompt = self._get_or_create_prompt(voice_name)
        
        sentences = self._split_sentences(text)
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
                
            logger.info(f"Chunk {i+1}/{len(sentences)}: {sentence[:30]}...")
            
            loop = asyncio.get_event_loop()
            
            # Use autocast wrapper
            def generate_with_autocast(s):
                with torch.cuda.amp.autocast(dtype=torch.bfloat16):
                    return self.model.generate_voice_clone(
                        text=s,
                        language="Korean",
                        voice_clone_prompt=voice_prompt,
                    )
            
            wavs, sr = await loop.run_in_executor(
                None,
                lambda s=sentence: generate_with_autocast(s)
            )
            
            import time
            chunk_path = config.TEMP_DIR / f"chunk_{i}_{int(time.time()*1000)}.wav"
            sf.write(str(chunk_path), wavs[0], sr)
            
            yield (chunk_path, sr)
    
    def _split_sentences(self, text: str):
        """Split text into sentences"""
        import re
        sentences = re.split(r"([.!?]\s+)", text)
        result = []
        for i in range(0, len(sentences), 2):
            if i+1 < len(sentences):
                result.append(sentences[i] + sentences[i+1])
            else:
                result.append(sentences[i])
        return [s.strip() for s in result if s.strip()]

    def clear_cache(self, voice_name: str = None):
        """Clear cached voice prompts"""
        if voice_name:
            self.voice_prompts.pop(voice_name, None)
            logger.info(f"Cleared cache for voice '{voice_name}'")
        else:
            self.voice_prompts.clear()
            logger.info("Cleared all voice prompts cache")
    
    def unload_model(self):
        """Unload model to free GPU memory"""
        if self.model is not None:
            del self.model
            self.model = None
            self.voice_prompts.clear()
            torch.cuda.empty_cache()
            logger.info("Model unloaded")
