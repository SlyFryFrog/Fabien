import asyncio
from src.bot.fabien import Fabien
from discord import Intents
from src.constants import CMD_PREFIX

def main():
    intents: Intents = Intents.default()
    intents.message_content = True
    intents.members = True
    intents.reactions = True
    intents.guilds = True

    fabien: Fabien = Fabien(
        command_prefix=CMD_PREFIX, 
        intents=intents
    )

    asyncio.run(fabien.load_cogs())
    fabien.load_key()

if __name__ == '__main__':
    main()