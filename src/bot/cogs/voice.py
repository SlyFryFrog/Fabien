import discord
from discord.ext import commands
import pyttsx3
from discord import Interaction, app_commands
from discord.ext.commands import Bot
import gtts

from src.bot.ai.fabien_ai import FabienAI
from src.constants import ALLOWED_GUILD_IDS


tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 300)
tts_engine.setProperty('volume', 1.0)


class FabienVoice(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.vc = None
        self.fabien_ai = FabienAI()
        self.fabien_ai.load_memory()

    @app_commands.command(name="ask")
    async def ask(self, interaction: Interaction, question: str):
        response_message = self.fabien_ai.get_whole_response(interaction.user.name, str(interaction.user.id), question)

        audio = gtts.gTTS(text=response_message)
        audio.save("rsc/audio/audio.mp3")

        if not self.vc and interaction.user.voice:
            self.vc = await interaction.user.voice.channel.connect()

        if self.vc:
            self.vc.play(discord.FFmpegPCMAudio("rsc/audio/audio.mp3"))
            await interaction.response.send_message("🎤 Speaking now...", ephemeral=True)
        else:
            await interaction.response.send_message("I'm not in a voice channel!", ephemeral=True)

    @app_commands.command(name="tts")
    async def text_to_speech(self, interaction: Interaction, message: str):
        audio = gtts.gTTS(text=f"{interaction.user.name} said: {message}")
        audio.save("rsc/audio/audio.mp3")

        if not self.vc and interaction.user.voice:
            self.vc = await interaction.user.voice.channel.connect()

        if self.vc:
            self.vc.play(discord.FFmpegPCMAudio("rsc/audio/audio.mp3"))
            await interaction.response.send_message("🗣️ Speaking now...", ephemeral=True)
        else:
            await interaction.response.send_message("I'm not in a voice channel!", ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(FabienVoice(bot))
