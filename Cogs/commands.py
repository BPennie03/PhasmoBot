import os

import discord
from discord.ext import commands
from discord import app_commands

import fandom

# Global lists for ghosts, cursed possessions, and evidences
ghost_list = ["Banshee", "Demon", "Deogen", "Goryo", "Hantu", "Jinn", "Mare", "Moroi", "Myling", "Obake", "Oni", "Onryo",
              "Phantom", "Poltergeist", "Raiju", "Revenant", "Shade", "Spirit", "Thaye", "The Mimic", "The Twins", "Wraith", "Yokai", "Yurei"]
cursed_poss_list = ["Haunted Mirror", "Monkey Paw", "Music Box",
                    "Ouija Board", "Summoning Circle", "Tarot Cards", "Voodoo Doll"]
evidence_list = ["D.O.T.S Projector", "EMF Level 5", "Fingerprints",
                 "Freezing Temperatures", "Ghost Orb", "Ghost Writing", "Spirit Box"]


async def setup(bot: commands.Bot):
    await bot.add_cog(commands(bot))

class commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Sets the fandom page to be Phasmophobia upon initialization, as we will never change this
    fandom.set_wiki("Phasmophobia")

    @commands.command(name='sync')
    async def sync(self, ctx):
        print("IT SYNCED IT SYNCED!")
        await self.bot.tree.sync()
        self.bot.tree.copy_global_to(guild=ctx.guild)

    @app_commands.command(description="Lists the evidence required for a specific ghost")
    async def ghostevidence(self, interaction: discord.Interaction, ghost_type: str):
        await interaction.response.defer()

        if ghost_type not in ghost_list:
            await interaction.followup.send(f"Incorrect or invalid ghost type: \"{ghost_type}\"", ephemeral=True)
            return

        # Gets the page and section for the ghost and evidence
        page = fandom.page(ghost_type)
        ghost_evidence_list = page.section("Evidence").split("\n")

        message = f"**{ghost_evidence_list[0]} for {ghost_type}: **\n"

        # Prints the ghosts evidence
        for i in range(1, 4):
            message += " > " + ghost_evidence_list[i] + "\n"

        # If this specific ghost has an extra slot for special evidence, print it
        if len(ghost_evidence_list) == 5:
            message += f"\n**Special {ghost_type} evidence:** {ghost_evidence_list[4]}"

        await interaction.followup.send(message)

    # autocomplete function for ghostevidence command
    @ghostevidence.autocomplete("ghost_type")
    async def ghostevidence_autocompletion(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        data = []
        choices = ghost_list

        for choice in choices:
            data.append(app_commands.Choice(name=choice, value=choice))
        return data

    # @app_commands.command(description="Gives important info regarding a specific Cursed Possession")
    # async def cursed(self, interaction: discord.Interaction, cursed_poss: str):
    #     await interaction.response.defer()
    #     for item in cursed_poss_list:
    #         if cursed_poss.lower() == item.lower():
    #             page = fandom.page(item)
    #             await interaction.followup.send(page.section("Mechanics"))
    #             return

    #     await interaction.response.send_message("Not a valid Cursed Possession")

    @app_commands.command(description="Find the exact ghost type for your investigation!")
    async def whatghost(self, interaction: discord.Interaction):
        await interaction.response.send_message("Its a Jinn!")

    @app_commands.command(description="Finds possible ghosts based on given evidence")
    async def possibleghosts(self, interaction: discord.Interaction, evidence: str):
        await interaction.response.defer()
        if evidence not in evidence_list:
            await interaction.response.send_message("Invalid or Incorrect evidence", ephemeral=True)
            return

        # Gets the page and section for the evidence and possible ghosts
        page = fandom.page(evidence)
        possible_list = page.section("Possible ghosts").split("\n")

        # Output string that will be appended to
        possible_ghosts = f"**Possible Ghosts with: {evidence}**\n"

        # For every item in the list, if the item is a ghost, append it to the output string
        for item in possible_list:
            if item in ghost_list:
                possible_ghosts += " > " + item + "\n"

        await interaction.followup.send(possible_ghosts)

    # autocomplete function for possibleghost command
    @possibleghosts.autocomplete("evidence")
    async def possibleghost_autocompletion(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        data = []
        choices = evidence_list

        for choice in choices:
            data.append(app_commands.Choice(name=choice, value=choice))
        return data

    @app_commands.command(description="Display the rewards for 3 star ghost photos")
    async def photos(self, interaction: discord.Interaction):
        output = """```Ghost = $20
                    Bone = $10
                    Burned Crucifix = $10
                    Dirty Water = $10
                    Cursed Possession = $5
                    Dead Body = $5
                    D.O.T.S Ghost = $5
                    Fingerprints = $5
                    Footprints = $5
                    Ghost Writing = $5
                    Interaction = $5```"""
        await interaction.response.send_message(output)
