import os
from dotenv import load_dotenv

COGS_DIR: str = "src/bot/cogs/"
SETTINGS_DIR: str = "rsc/settings/"
LOGGER_CONFIG_FILE: str = "rsc/logs/logger.conf"
CMD_PREFIX: str = "!"
MEMORY_DIR = "rsc/memory/"
MODELS = ["mannix/llama3.1-8b-abliterated"]

# Load private app-specific settings
load_dotenv(f"{SETTINGS_DIR}.env")
FABIEN_APP_ID: str = os.getenv("FABIEN_APP_ID")
FABIEN_TOKEN: str = os.getenv("FABIEN_TOKEN")

ALLOWED_GUILD_IDS = [
    int(gid) for gid in os.getenv("ALLOWED_GUILD_IDS", "").split(",") if gid.strip()
]
