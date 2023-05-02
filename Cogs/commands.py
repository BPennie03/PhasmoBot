import os

import discord
from discord.ext import commands
from discord import app_commands

import fandom

ghost_list = ["Banshee", "Demon", "Deogen", "Goryo", "Hantu", "Jinn", "Mare", "Moroi", "Myling", "Obake", "Oni", "Onryo", "Phantom", "Poltergeist", "Raiju", "Revenant", "Shade", "Spirit", "Thaye", "The Mimic", "The Twins", "Wraith", "Yokai", "Yurei"]
cursed_poss_list = ["Haunted Mirror", "Monkey Paw", "Music Box", "Ouija Board", "Summoning Circle", "Tarot Cards", "Voodoo Doll"]
evidence_list = ["D.O.T.S Projector", "EMF Level 5", "Fingerprints", "Freezing Temperatures", "Ghost Orb", "Ghost Writing", "Spirit Box"]

async def setup(bot: commands.Bot):
    await bot.add_cog(commands(bot))

class commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    fandom.set_wiki("Phasmophobia")

    @commands.command(name='sync')
    async def sync(self, ctx):
        print("IT SYNCED IT SYNCED!")
        await self.bot.tree.sync()
        self.bot.tree.copy_global_to(guild=ctx.guild)

    @app_commands.command(description="Lists the evidence required for a specific ghost")
    async def ghostevidence(self, interaction: discord.Interaction, ghost_type: str):
        await interaction.response.defer()
        for ghost in ghost_list:
            if ghost_type.lower() == ghost.lower():
                page = fandom.page(ghost)
                await interaction.followup.send(page.section("Evidence"))
                return

        await interaction.followup.send("Not a valid ghost type")

    @app_commands.command(description="Gives important info regarding a specific Cursed Possession")
    async def cursed(self, interaction: discord.Interaction, cursed_poss: str):
        await interaction.response.defer()
        for item in cursed_poss_list:
            if cursed_poss.lower() == item.lower():
                page = fandom.page(item)
                await interaction.followup.send(page.section("Mechanics"))
                return
        
        await interaction.response.send_message("Not a valid Cursed Possession")

    @app_commands.command(description="Find the exact ghost type for your investigation!")
    async def whatghost(self, interaction: discord.Interaction):
        await interaction.response.send_message("Its a Jinn!")

    @app_commands.command(description="Finds possible ghosts based on given evidence")
    async def possibleghosts(self, interaction: discord.Interaction, evidence: str):
        await interaction.response.defer()
        if evidence not in evidence_list:
            await interaction.response.send_message("Invalid or Incorrect evidence", ephemeral=True)
            return
        
        page = fandom.page(evidence)
        possible_list = page.section("Possible ghosts").split("\n")
        possible_ghosts = f"**Possible Ghosts with: {evidence}**\n"
        for item in possible_list:
            if item in ghost_list:
                possible_ghosts += item + "\n"

        await interaction.followup.send(possible_ghosts)

    # @app_commands.command(description="Display the rewards for 3 star ghost photos")
    # def photos(self, interaction: discord.Interaction):
