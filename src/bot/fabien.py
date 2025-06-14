import discord
import os
from discord import Intents, Interaction
from discord import app_commands
from discord.app_commands import tree
from discord.ext.commands import Bot
from src.logger import LOGGER
from src.constants import COGS_DIR, FABIEN_APP_ID, FABIEN_TOKEN, ALLOWED_GUILD_IDS

class Fabien(Bot):
    def __init__(self, command_prefix: str, intents: Intents):
        if not FABIEN_APP_ID:
            LOGGER.critical("FABIEN_APP_ID not set in .env")
            raise ValueError("Missing FABIEN_APP_ID")

        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            application_id=FABIEN_APP_ID
        )

    def start_bot(self) -> None:
        @self.event
        async def on_ready():
            LOGGER.info("Logged in as %s", self.user)
            await self.tree.sync()
            await self.prune_unauthorized_guilds()
            
        if not FABIEN_TOKEN:
            LOGGER.critical("FABIEN_TOKEN not set in .env")
            raise ValueError("Missing FABIEN_TOKEN")

        self.run(FABIEN_TOKEN)
    
    async def prune_unauthorized_guilds(self):
        for guild in self.guilds:
            if guild.id not in ALLOWED_GUILD_IDS:
                LOGGER.warning("Leaving unauthorized guild: %s (%s)", guild.name, guild.id)
                await guild.leave()
            
    async def load_cogs(self) -> None:
        path: str = COGS_DIR.replace("/", ".")

        for file in os.listdir(COGS_DIR):
            if file.endswith(".py"):
                try:
                    await self.load_extension(f"{path}{file.rstrip(".py")}")
                    LOGGER.debug("Successfully loaded cog from file: %s.", file)
                except Exception as e:
                    LOGGER.error("Failed to load cog from file: %s. Cause: %s", file, e)
                    LOGGER.error(e)
                
    async def setup_hook(self):
        await self.load_cogs()
