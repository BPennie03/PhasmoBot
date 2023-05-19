import os
import sys

import discord
from discord import app_commands
from discord.ext import commands


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminCommands(bot))


class AdminCommands(commands.Cog):
    """Restart the discord bot
    Send message to user, then restarts the bot

    Outputs:
        Message to chat confirming that the bot is restarting.
    """

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Restarts the discord bot")
    @app_commands.default_permissions(administrator=True)
    async def restart(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Restarting...")
        os.execv(sys.argv[0], sys.argv)


@app_commands.command(description="shutdown the discord bot")
@app_commands.default_permissions(administrator=True)
async def stop(self, interaction: discord.Interaction):
    """Shutdown the discord bot
    Send message to user. Exit program.

    Outputs:
        Message to user that discord bot is being shut down
    """

    await interaction.response.defer(ephemeral=True)
    await interaction.channel.send('Stopping...')
    await self.bot.close()
