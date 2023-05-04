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

# Helper function for possibleghosts to trim possible_ghost list to only include ghosts


def get_ghostlist(possible_list):
    temp_list = []
    for item in possible_list:
        if item in ghost_list:
            temp_list.append(item)
    return temp_list


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

    @app_commands.command(description="Finds possible ghosts based on given evidence (must enter at least one evidence)")
    async def possibleghosts(self, interaction: discord.Interaction, evidence_1: str, evidence_2: str = 'None', evidence_3: str = 'None'):
        await interaction.response.defer()

        # Gets the page and section for the evidence and possible ghosts
        page1 = fandom.page(evidence_1)
        possible_list1 = get_ghostlist(
            page1.section("Possible ghosts").split("\n"))
        evidences_given = 1
        possible_ghosts = []

        # Output str that will be appended to
        output = f"**Possible Ghosts with: {evidence_1}"

        # If only 2 evidences are entered
        if evidence_2 != 'None':
            evidences_given += 1
            page2 = fandom.page(evidence_2)
            possible_list2 = get_ghostlist(
                page2.section("Possible ghosts").split("\n"))

            output += f", {evidence_2}"

        if evidence_3 != 'None':
            evidences_given += 1
            page3 = fandom.page(evidence_3)
            possible_list3 = get_ghostlist(
                page3.section("Possible ghosts").split("\n"))

            output += f", {evidence_3}"

        output += ": **\n"

        if evidences_given == 1:
            possible_ghosts = possible_list1
        elif evidences_given == 2:
            possible_ghosts = set(possible_list1).intersection(possible_list2)
        elif evidences_given == 3:
            for ghost in ghost_list:
                if ghost in possible_list1 and possible_list2 and possible_list3:
                    possible_ghosts.append(ghost)
                    break

        # For every item in the list, if the item is a ghost, append it to the output string
        if len(possible_ghosts) == 0:
            await interaction.followup.send("Erorr: No ghosts match those given evidences")
        else:
            print(possible_ghosts)
            for ghost in possible_ghosts:
                output += " > " + ghost + "\n"
            await interaction.followup.send(output)

    # autocomplete functions for possibleghost command

    @possibleghosts.autocomplete("evidence_1")
    @possibleghosts.autocomplete("evidence_2")
    @possibleghosts.autocomplete("evidence_3")
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
