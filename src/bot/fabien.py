import os
from discord import Intents
from discord.errors import LoginFailure
from discord.ext.commands import Bot
from src.logger import LOGGER
from src.constants import SETTINGS_DIR, COGS_DIR
from dotenv import load_dotenv

class Fabien(Bot):
    def __init__(self, command_prefix: str, intents: Intents):
        try:
            load_dotenv(f"{SETTINGS_DIR}.env")
            application_id = os.getenv("FABIEN_APP_ID")
        except LoginFailure:
            LOGGER.critical("Failed to load discord application id.")
        
        super().__init__(command_prefix=command_prefix, intents=intents, application_id=application_id)

    def load_key(self) -> None:

        @self.event
        async def on_ready() -> None:
            LOGGER.debug("Successfully logged in.")
        
        try:
            load_dotenv(f"{SETTINGS_DIR}.env")
            self.run(os.getenv("FABIEN_TOKEN"))
        except LoginFailure:
            LOGGER.critical("Failed to load discord token.")
            
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
        await self.tree.sync()
