from src.bot.fabien import Fabien
from discord import Intents
from src.constants import CMD_PREFIX

def main():
    intents: Intents = Intents.all()
    intents.message_content = True
    intents.members = True
    intents.reactions = True
    intents.guilds = True
    intents.voice_states = True

    fabien: Fabien = Fabien(
        command_prefix=CMD_PREFIX, 
        intents=intents
    )

    fabien.start_bot()
    

if __name__ == '__main__':
    main()