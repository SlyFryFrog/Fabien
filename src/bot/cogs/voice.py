import discord
from discord.ext import commands
import pyttsx3
from discord import Interaction, app_commands
from discord.ext.commands import Bot
import gtts

from src.bot.ai.fabien_ai import FabienAI
from src.constants import ALLOWED_GUILD_IDS

# Set up the TTS engine
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 300)  # Speed
tts_engine.setProperty('volume', 1.0)  # Volume

class FabienVoice(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.vc = discord.utils.get(self.bot.voice_clients, guild=ALLOWED_GUILD_IDS[0])
        self.fabien_ai: FabienAI = FabienAI()
        self.fabien_ai.load_memory()

    @app_commands.command(name="join")
    async def join(self, interaction: Interaction):
        if interaction.user.voice is not None:
            if not interaction.guild.voice_client:
                self.vc = await interaction.user.voice.channel.connect()
                await interaction.response.send_message("Joined the voice channel.", ephemeral=True)
            else:
                await interaction.response.send_message("Already connected to a voice channel.", ephemeral=True)
        else:
            await interaction.response.send_message("You're not in a voice channel!", ephemeral=True)

    @app_commands.command(name="leave")
    async def leave(self, interaction: Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("Disconnected from the voice channel.", ephemeral=True)
        else:
            await interaction.response.send_message("I'm not in a voice channel!", ephemeral=True)

    @app_commands.command(name="ask")
    async def ask(self, interaction: Interaction, question: str):
        context = self.fabien_ai.get_whole_response(interaction.user.name, str(interaction.user.id), question)

        # Start the response generation
        response_message = self.fabien_ai.get_whole_response(interaction.user, interaction.guild_id, question)

        audio = gtts.gTTS(text=response_message)
        audio.save("rsc/audio/audio.mp3")

        self.vc.play(discord.FFmpegPCMAudio("rsc/audio/audio.mp3"))
    
    @app_commands.command(name="tts")
    async def text_to_speech(self, interaction: Interaction, message: str):
        audio = gtts.gTTS(text=f"{interaction.user} said: {message}")
        audio.save("rsc/audio/audio.mp3")

        self.vc.play(discord.FFmpegPCMAudio("rsc/audio/audio.mp3"))


async def setup(bot: Bot):
    await bot.add_cog(FabienVoice(bot))
