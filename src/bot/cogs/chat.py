from discord import Interaction, app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context
from src.bot.ai.fabien_ai import FabienAI

class FabienCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.fabien_ai: FabienAI = FabienAI()
        self.fabien_ai.load_memory()

    @app_commands.command(name="clear_memory")
    async def clear_user_memory(self, interaction: Interaction):
        try:
            self.fabien_ai.clear_user_memory(str(interaction.user.id))
            self.fabien_ai.save_memory()
            await interaction.response.send_message(
                "Successfully cleared memory.",
                ephemeral=True
            )
        except:
            await interaction.response.send_message(
                "Failed to clear memory.",
                ephemeral=True
            )

    @commands.command(name="fabien")
    async def fabien(self, ctx: Context, *, user_message: str):
        user_id = str(ctx.author.id)
        user_name = ctx.author.name

        try:
            response: str = self.fabien_ai.get_response(user_name, user_id, user_message)
            
            await ctx.send(response)
            self.fabien_ai.save_memory()

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
            raise e

async def setup(bot: Bot):
    await bot.add_cog(FabienCog(bot))
