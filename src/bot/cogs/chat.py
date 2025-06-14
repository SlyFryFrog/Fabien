from discord import Interaction, app_commands
from discord.ext import commands
from discord.ext.commands import Bot, Context
from src.bot.ai.fabien_ai import FabienAI


class FabienChat(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot
        self.fabien_ai: FabienAI = FabienAI()
        self.fabien_ai.load_memory()

    @app_commands.command(name="clear_guild_memory")
    async def clear_memory(self, interaction: Interaction):
        try:
            self.fabien_ai.clear_memory(str(interaction.guild.id))
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
    
    @app_commands.command(name="fabien")
    async def fabien(self, interaction: Interaction, message: str):
        try:
            await interaction.response.defer(thinking=True)
            # Send an initial message that will be updated
            response_message = await interaction.followup.send("Loading response...")

            # Start the response generation
            response_generator = self.fabien_ai.get_response(interaction.user.name, interaction.guild.id, message)

            # Initialize the response content
            final_response = ""
            chunk_count = 0

            async def update_message():
                """Function to periodically update the message."""
                nonlocal final_response
                await response_message.edit(content=final_response)

            # Send partial responses and update the message content
            async for partial_response in response_generator:
                final_response += partial_response  # Append to the current response
                chunk_count += 1

                # Update message every 20 chunks
                if chunk_count % 20 == 0:
                    await update_message()

            # Final update after all chunks are received
            await response_message.edit(content=final_response)

            # Run async save memory concurrently
            await self.fabien_ai.save_memory()

        except Exception as e:
            await interaction.followup.send(f"An error occurred: {e}")
            raise e


async def setup(bot: Bot):
    await bot.add_cog(FabienChat(bot))
