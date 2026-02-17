import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", 0))

# Voice Configuration
DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "jonghun")
VOICES_DIR = Path("voices")

# Model Configuration
DEVICE = os.getenv("DEVICE", "cuda:0")
MODEL_SIZE = os.getenv("MODEL_SIZE", "1.7B")  # "0.6B" or "1.7B"
MODEL_NAME = f"Qwen/Qwen3-TTS-12Hz-{MODEL_SIZE}-Base"

# Admin Configuration
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]

# Audio Configuration
SAMPLE_RATE = 12000
AUDIO_FORMAT = "wav"
TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

# Command Prefix
COMMAND_PREFIX = "!"
