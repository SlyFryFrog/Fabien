from discord import app_commands, Interaction
from discord.ext import commands
from discord.ext.commands import Bot

from src.bot.fabien import Fabien
from src.logger import LOGGER

class FabienHelp(commands.Cog):
    def __init__(self, bot: Fabien):
        super().__init__()
        self.bot = bot

    @app_commands.command(name="help")
    async def help(self, interaction: Interaction) -> None:
        await interaction.response.send_message(
            """Fabien Commands:
- /fabien <text>  : Prompts Fabien for a reply. This may take a while on slower hardware.
- /clear_memory   : Clears your specific chat history with Fabien.
- /help            : Displays this message.
            """,
            ephemeral=True
        )
    
    @app_commands.command(name="sync", description="Owner only")
    async def sync(self, interaction: Interaction) -> None:
        if interaction.user.guild_permissions.administrator:
            await self.bot.tree.sync(guild=interaction.guild)
            await interaction.response.send_message('Command tree synced.', ephemeral=True)
            LOGGER.debug('Command tree synced.')
        else:
            await interaction.response.send_message(
                'You must be an administrator to use this command!',
                ephemeral=True
            )
    
    @app_commands.command(name="set_system_prompt", description="Admin only; changes the system prompt used for the server.")
    async def set_system_prompt(self, interaction: Interaction):
        if interaction.user.guild_permissions.administrator:
            pass    # TODO
        else:
            await interaction.response.send_message(
                'You must be an administrator to use this command!',
                ephemeral=True
            )



async def setup(bot: Fabien):
    await bot.add_cog(FabienHelp(bot))