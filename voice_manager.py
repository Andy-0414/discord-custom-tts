import discord
from discord.ext import commands
from pathlib import Path
import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceManager:
    """Discord Voice Channel Manager"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_client: Optional[discord.VoiceClient] = None
        self.queue = asyncio.Queue()
        self.is_playing = False
        
    async def join_channel(self, channel: discord.VoiceChannel) -> bool:
        """Join a voice channel"""
        try:
            if self.voice_client and self.voice_client.is_connected():
                if self.voice_client.channel.id == channel.id:
                    logger.info(f"Already in channel: {channel.name}")
                    return True
                else:
                    await self.voice_client.move_to(channel)
                    logger.info(f"Moved to channel: {channel.name}")
                    return True
            
            self.voice_client = await channel.connect()
            logger.info(f"Joined channel: {channel.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to join channel: {e}")
            return False
    
    async def leave_channel(self) -> bool:
        """Leave current voice channel"""
        try:
            if self.voice_client and self.voice_client.is_connected():
                await self.voice_client.disconnect()
                self.voice_client = None
                logger.info("Left voice channel")
                return True
            else:
                logger.warning("Not in any voice channel")
                return False
                
        except Exception as e:
            logger.error(f"Failed to leave channel: {e}")
            return False
    
    async def play_audio(self, audio_path: Path, cleanup: bool = True) -> bool:
        """
        Play audio file in voice channel
        
        Args:
            audio_path: Path to audio file
            cleanup: Delete file after playing
            
        Returns:
            True if played successfully
        """
        if not self.voice_client or not self.voice_client.is_connected():
            logger.error("Not connected to voice channel")
            return False
        
        if not audio_path.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return False
        
        try:
            # Wait if already playing
            while self.is_playing:
                await asyncio.sleep(0.5)
            
            self.is_playing = True
            
            # Create audio source
            source = discord.FFmpegPCMAudio(str(audio_path))
            
            # Play audio
            def after_playing(error):
                if error:
                    logger.error(f"Error playing audio: {error}")
                self.is_playing = False
                
                # Cleanup
                if cleanup and audio_path.exists():
                    try:
                        audio_path.unlink()
                        logger.info(f"Deleted temp file: {audio_path}")
                    except Exception as e:
                        logger.error(f"Failed to delete temp file: {e}")
            
            self.voice_client.play(source, after=after_playing)
            logger.info(f"Playing audio: {audio_path}")
            
            # Wait for playback to finish
            while self.is_playing:
                await asyncio.sleep(0.5)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to play audio: {e}")
            self.is_playing = False
            return False
    
    def is_connected(self) -> bool:
        """Check if bot is connected to voice channel"""
        return self.voice_client is not None and self.voice_client.is_connected()
    
    def get_channel(self) -> Optional[discord.VoiceChannel]:
        """Get current voice channel"""
        if self.voice_client and self.voice_client.is_connected():
            return self.voice_client.channel
        return None
