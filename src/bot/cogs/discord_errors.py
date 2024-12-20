from discord.ext import commands
from discord.ext.commands import Bot, CommandNotFound, MissingRequiredArgument, Context, errors

class DiscordErrors(commands.Cog):
    """
    Extension for the bot that gives special error handling to specific
    erros that may occur.

    Args:
        commands (Cog): inherited class that is used to create a Cog
    """

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: errors) -> None:
        """
        Args:
            ctx (Context): Context of the message
            error: Error thrown by the message

        Raises:
            error: Any unresolved error
        """
        
        if isinstance(error, CommandNotFound):
            return
        elif isinstance(error, MissingRequiredArgument):
            return
        else:
            raise error


async def setup(bot: Bot):
    """
    Setup function used to add DiscordErrors as an extension

    Args:
        bot (Bot): Discord bot object to have the extension added to
    """
    await bot.add_cog(DiscordErrors(bot))