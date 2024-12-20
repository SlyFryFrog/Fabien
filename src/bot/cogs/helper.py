from discord import app_commands, Interaction
from discord.ext import commands
from discord.ext.commands import Bot

class FabienHelp(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(name="fabien_help")
    async def fabien_help(self, interaction: Interaction) -> None:
        await interaction.response.send_message(
            """Fabien Commands:
- !fabien <text>  : Prompts Fabien for a reply. This may take a while on slower hardware.
- /clear_memory   : Clears your specific chat history with Fabien.
- /help            : Displays this message.
            """,
            ephemeral=True
        )


async def setup(bot: Bot):
    await bot.add_cog(FabienHelp(bot))