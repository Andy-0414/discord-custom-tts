import discord
from discord.ext import commands
import logging
import asyncio
from pathlib import Path

import config
from tts_engine import TTSEngine
from voice_manager import VoiceManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)

# Initialize modules
tts_engine = TTSEngine()
voice_manager = VoiceManager(bot)


@bot.event
async def on_ready():
    """Called when bot is ready"""
    logger.info(f"Bot logged in as {bot.user.name} ({bot.user.id})")
    logger.info(f"Discord.py version: {discord.__version__}")
    
    # Load TTS model
    try:
        await asyncio.get_event_loop().run_in_executor(None, tts_engine.load_model)
        logger.info("TTS engine initialized")
    except Exception as e:
        logger.error(f"Failed to initialize TTS engine: {e}")
        await bot.close()
        return
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{config.COMMAND_PREFIX}tts <텍스트>"
        )
    )
    
    logger.info("Bot is ready!")


@bot.command(name="tts")
async def tts_command(ctx: commands.Context, *, text: str):
    """
    Generate TTS and play in voice channel
    
    Usage: !tts <텍스트>
    """
    # Check if user is in voice channel
    if not ctx.author.voice:
        await ctx.reply("❌ 음성 채널에 먼저 들어가주세요!")
        return
    
    user_channel = ctx.author.voice.channel
    
    # Join channel if not connected
    if not voice_manager.is_connected():
        success = await voice_manager.join_channel(user_channel)
        if not success:
            await ctx.reply("❌ 음성 채널 연결에 실패했습니다.")
            return
    elif voice_manager.get_channel().id != user_channel.id:
        # Move to user's channel
        success = await voice_manager.join_channel(user_channel)
        if not success:
            await ctx.reply("❌ 음성 채널 이동에 실패했습니다.")
            return
    
    # Show typing indicator
    async with ctx.typing():
        try:
            # Generate TTS
            audio_path = await asyncio.get_event_loop().run_in_executor(
                None,
                tts_engine.generate,
                text,
                config.DEFAULT_VOICE,
                None
            )
            
            await ctx.reply(f"🔊 생성 완료! 재생합니다...")
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            await ctx.reply(f"❌ TTS 생성 실패: {str(e)}")
            return
    
    # Play audio
    success = await voice_manager.play_audio(audio_path, cleanup=True)
    
    if not success:
        await ctx.reply("❌ 오디오 재생에 실패했습니다.")


@bot.command(name="join")
async def join_command(ctx: commands.Context):
    """
    Join user's voice channel
    
    Usage: !join
    """
    if not ctx.author.voice:
        await ctx.reply("❌ 먼저 음성 채널에 들어가주세요!")
        return
    
    channel = ctx.author.voice.channel
    success = await voice_manager.join_channel(channel)
    
    if success:
        await ctx.reply(f"✅ **{channel.name}** 채널에 참가했습니다!")
    else:
        await ctx.reply("❌ 채널 참가에 실패했습니다.")


@bot.command(name="leave")
async def leave_command(ctx: commands.Context):
    """
    Leave voice channel
    
    Usage: !leave
    """
    if not voice_manager.is_connected():
        await ctx.reply("❌ 음성 채널에 연결되어 있지 않습니다.")
        return
    
    channel_name = voice_manager.get_channel().name
    success = await voice_manager.leave_channel()
    
    if success:
        await ctx.reply(f"✅ **{channel_name}** 채널에서 나갔습니다.")
    else:
        await ctx.reply("❌ 채널 나가기에 실패했습니다.")


@bot.command(name="clone")
@commands.check(lambda ctx: ctx.author.id in config.ADMIN_IDS)
async def clone_command(ctx: commands.Context, voice_name: str):
    """
    Create new voice clone from attached audio (Admin only)
    
    Usage: !clone <voice_name> (with audio attachment)
    """
    # Check for audio attachment
    if not ctx.message.attachments:
        await ctx.reply("❌ 오디오 파일을 첨부해주세요! (3초 이상 WAV 파일)")
        return
    
    attachment = ctx.message.attachments[0]
    
    # Validate file type
    if not attachment.filename.lower().endswith(('.wav', '.mp3', '.ogg')):
        await ctx.reply("❌ 지원하는 파일 형식: .wav, .mp3, .ogg")
        return
    
    # Create voice directory
    voice_dir = config.VOICES_DIR / voice_name
    voice_dir.mkdir(parents=True, exist_ok=True)
    
    ref_audio_path = voice_dir / "reference.wav"
    
    async with ctx.typing():
        try:
            # Download audio
            await attachment.save(ref_audio_path)
            
            # Create reference text file (placeholder)
            ref_text_path = voice_dir / "reference.txt"
            if not ref_text_path.exists():
                ref_text_path.write_text(
                    "참조 오디오의 텍스트를 여기에 입력하세요.",
                    encoding="utf-8"
                )
            
            await ctx.reply(
                f"✅ 새로운 목소리 프로필 **{voice_name}** 생성 완료!\n"
                f"📝 `voices/{voice_name}/reference.txt` 파일을 수정해서 참조 텍스트를 입력하세요."
            )
            
        except Exception as e:
            logger.error(f"Voice clone creation failed: {e}")
            await ctx.reply(f"❌ 목소리 프로필 생성 실패: {str(e)}")


@bot.command(name="voices")
async def voices_command(ctx: commands.Context):
    """
    List available voice profiles
    
    Usage: !voices
    """
    voices = []
    
    for voice_dir in config.VOICES_DIR.iterdir():
        if voice_dir.is_dir():
            ref_audio = voice_dir / "reference.wav"
            ref_text = voice_dir / "reference.txt"
            
            if ref_audio.exists() and ref_text.exists():
                is_default = "⭐" if voice_dir.name == config.DEFAULT_VOICE else ""
                voices.append(f"• **{voice_dir.name}** {is_default}")
    
    if voices:
        await ctx.reply("🎙️ **사용 가능한 목소리 프로필:**\n" + "\n".join(voices))
    else:
        await ctx.reply("❌ 사용 가능한 목소리 프로필이 없습니다.")


@bot.command(name="help")
async def help_command(ctx: commands.Context):
    """Show help message"""
    help_text = f"""
🤖 **Discord Custom TTS Bot**

**명령어:**
• `{config.COMMAND_PREFIX}tts <텍스트>` - 텍스트를 음성으로 변환
• `{config.COMMAND_PREFIX}join` - 음성 채널 참가
• `{config.COMMAND_PREFIX}leave` - 음성 채널 나가기
• `{config.COMMAND_PREFIX}voices` - 사용 가능한 목소리 목록
• `{config.COMMAND_PREFIX}clone <이름>` - 새 목소리 추가 (관리자)
• `{config.COMMAND_PREFIX}help` - 도움말

**사용법:**
1. 음성 채널에 들어갑니다
2. `{config.COMMAND_PREFIX}tts 안녕하세요!` 명령어 입력
3. 봇이 자동으로 채널에 참가해서 음성을 재생합니다

**기술 스택:**
• Qwen3-TTS Voice Clone
• Discord.py

**현재 목소리:** {config.DEFAULT_VOICE}
"""
    await ctx.reply(help_text)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(f"❌ 필수 인자가 누락되었습니다: `{error.param.name}`")
    elif isinstance(error, commands.CheckFailure):
        await ctx.reply("❌ 이 명령어를 실행할 권한이 없습니다. (관리자 전용)")
    else:
        logger.error(f"Command error: {error}")
        await ctx.reply(f"❌ 오류 발생: {str(error)}")


def main():
    """Main entry point"""
    if not config.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not set in .env file")
        return
    
    try:
        bot.run(config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
    finally:
        # Cleanup
        tts_engine.unload_model()


if __name__ == "__main__":
    main()
