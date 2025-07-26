import asyncio
import discord
from discord.ext import commands
import yt_dlp
from discord import Interaction, app_commands
from discord.ext.commands import Bot

FFMPEG_OPTS = {
    "options": "-vn -loglevel error"
}

ytdl_flat_opts = {
    "quiet": True,
    "extract_flat": "in_playlist",
    "skip_download": True,
    "default_search": "auto",
    "noplaylist": False,
}

ytdl_stream_opts = {
    "quiet": True,
    "format": "bestaudio/best"
}

ytdl_flat = yt_dlp.YoutubeDL(ytdl_flat_opts)
ytdl_stream = yt_dlp.YoutubeDL(ytdl_stream_opts)

async def get_sources(url: str):
    data = ytdl_flat.extract_info(url, download=False)
    entries = data.get("entries", [data])

    for entry in entries:
        video_url = entry.get("url") if entry.get("_type") == "url" else f"https://www.youtube.com/watch?v={entry.get('id', '')}"
        yield entry.get("title", "Unknown"), video_url

class Music(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.vc = None
        self.queues = {}
        self.playback_tasks = {}
        self.current_audio = None
        self.is_paused = False
        self.stop = False

    async def player_loop(self, guild_id: int):
        vc = self.queues.get(guild_id, {}).get("vc")
        q: asyncio.Queue = self.queues[guild_id]["queue"]

        while not q.empty() and not self.stop:
            title, video_url = await q.get()
            try:
                info = ytdl_stream.extract_info(video_url, download=False)
                stream_url = info["url"]
                source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTS)
                self.current_audio = discord.PCMVolumeTransformer(source)
            except Exception as e:
                print(f"Error extracting audio: {e}")
                q.task_done()
                continue

            vc.play(self.current_audio)
            while vc.is_playing() and not self.stop or self.is_paused:
                await asyncio.sleep(1)

            vc.stop()
            q.task_done()

        self.stop = False  # reset stop flag when loop ends

    @app_commands.command(name="join")
    async def join(self, interaction: Interaction):
        if interaction.user.voice and not interaction.guild.voice_client:
            self.vc = await interaction.user.voice.channel.connect()
            self.queues[interaction.guild.id] = {"vc": self.vc, "queue": asyncio.Queue()}
            await interaction.response.send_message("Joined the voice channel.", ephemeral=True)
        elif interaction.guild.voice_client:
            await interaction.response.send_message("Already connected.", ephemeral=True)
        else:
            await interaction.response.send_message("You're not in a voice channel!", ephemeral=True)

    @app_commands.command(name="leave")
    async def leave(self, interaction: Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            self.queues.pop(interaction.guild.id, None)
            self.vc = None
            await interaction.response.send_message("Disconnected.", ephemeral=True)
        else:
            await interaction.response.send_message("I'm not in a voice channel!", ephemeral=True)

    @app_commands.command(name="play")
    async def play(self, interaction: Interaction, query: str):
        guild_id = interaction.guild.id

        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ You must be in a voice channel to use this command.", ephemeral=True)
            return

        # Defer the response early to avoid timeout
        await interaction.response.defer(ephemeral=True)

        if not self.vc:
            self.vc = await interaction.user.voice.channel.connect()

        if guild_id not in self.queues:
            self.queues[guild_id] = {"vc": self.vc, "queue": asyncio.Queue()}

        q = self.queues[guild_id]["queue"]
        added_titles = []

        async for title, url in get_sources(query):
            await q.put((title, url))
            added_titles.append(title)

        await interaction.followup.send(
            "🔊 Added to queue:\n" + "\n".join(f"• {t}" for t in added_titles)[:1900] + "...",
            ephemeral=True
        )

        if guild_id not in self.playback_tasks or self.playback_tasks[guild_id].done():
            self.playback_tasks[guild_id] = asyncio.create_task(self.player_loop(guild_id))

    @app_commands.command(name="queue")
    async def queue(self, interaction: Interaction):
        q_info = self.queues.get(interaction.guild.id)
        if not q_info or q_info["queue"].empty():
            await interaction.response.send_message("🎶 Queue is empty!", ephemeral=True)
            return

        items = list(q_info["queue"]._queue)
        message = "\n".join([f"{idx+1}. {title}" for idx, (title, _) in enumerate(items)])
        await interaction.response.send_message(f"🎶 **Current Queue:**\n{message}", ephemeral=True)

    @app_commands.command(name="remove")
    @app_commands.describe(index="Index of the song in the queue (starting from 1)")
    async def remove_from_queue(self, interaction: Interaction, index: int):
        q_info = self.queues.get(interaction.guild.id)
        if not q_info or q_info["queue"].empty():
            await interaction.response.send_message("❌ Queue is empty!", ephemeral=True)
            return

        items = list(q_info["queue"]._queue)
        if index < 1 or index > len(items):
            await interaction.response.send_message("❌ Invalid index!", ephemeral=True)
            return

        removed = items.pop(index - 1)
        q_info["queue"]._queue.clear()
        for item in items:
            q_info["queue"].put_nowait(item)

        await interaction.response.send_message(f"🗑️ Removed `{removed[0]}` from the queue.", ephemeral=True)

    @app_commands.command(name="clear_queue")
    async def clear_queue(self, interaction: Interaction):
        q_info = self.queues.get(interaction.guild.id)
        if q_info:
            self.stop = True
            q_info["queue"] = asyncio.Queue()  # Clear the queue

        await interaction.response.send_message("✅ Queue has been cleared.", ephemeral=True)

    @app_commands.command(name="skip")
    async def skip(self, interaction: Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("⏭️ Skipped!", ephemeral=True)
        else:
            await interaction.response.send_message("Nothing is playing!", ephemeral=True)
    
    @app_commands.command(name="pause")
    async def pause(self, interaction: Interaction):
        if self.vc and self.vc.is_playing():
            self.vc.pause()
            self.is_paused = True
            await interaction.response.send_message("⏸️ Playback paused.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)

    @app_commands.command(name="resume")
    async def resume(self, interaction: Interaction):
        if self.vc and self.is_paused:
            self.vc.resume()
            self.is_paused = False
            self.stop = False
            await interaction.response.send_message("▶️ Resumed playback.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Nothing to resume.", ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(Music(bot))
