import os
import random
import requests

import asyncio
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

STEAM_API_KEY = os.getenv('STEAM_KEY')


async def setup(bot: commands.Bot):
    await bot.add_cog(commands(bot))

# Helper function for possibleghosts to trim possible_ghost list to only include ghosts


def get_ghostlist(possible_list: list):
    """Helper method for possibleghosts commnand

    Args:
        possible_list (list): list of possible ghosts

    Outputs:
        A new list of possilbe ghosts with correct Capitalization and spelling
    """

    temp_list = []
    for item in possible_list:
        if item in ghost_list:
            temp_list.append(item)
    return temp_list


def get_recent_news():
    """Helper method for news command
    Uses the Steam Web API to get the most recent news item for a specified game (Phasmophobia)

    Outputs:
        Either the most recent news item, or None if there isn't one
    """

    url = f'https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid=739630&count=1&maxlength=100&format=json'
    response = requests.get(url)
    data = response.json()
    if 'appnews' in data and 'newsitems' in data['appnews']:
        news_items = data['appnews']['newsitems']
        if len(news_items) > 0:
            return news_items[0]
    return None


class commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Sets the fandom page to be Phasmophobia upon initialization, as we will never change this
    fandom.set_wiki("Phasmophobia")

    @commands.command(name='sync')
    async def sync(self, ctx):
        await self.bot.tree.sync()
        self.bot.tree.copy_global_to(guild=ctx.guild)
        await ctx.send(f'All slash commands have been synced')

    @app_commands.command(description="Get recent Phasmo news!")
    async def news(self, interaction: discord.Interaction):
        """Command to get most recent Phasmo News
        Calls the get_recent_news helper method and creates an embed from the returned information

        Outputs:
            A message embed containing a link to the news item
        """

        await interaction.response.defer()

        news_item = get_recent_news()

        if news_item is not None:
            embed = discord.Embed(
                title=news_item['title'], description=news_item['contents'], color=discord.Color.blurple())

            if 'url' in news_item:
                embed.url = news_item['url']
        else:
            print("No recent news update found.")

        await interaction.followup.send(embed=embed)

    @app_commands.command(description="Lists the evidence required for a specific ghost")
    async def ghostevidence(self, interaction: discord.Interaction, ghost_type: str):
        """Command to get evidence list of a specific ghost
        Uses the fandom api to get specific page and sections to gather the evidence for a specific ghost, then 
        returns it as a string message

        Args:
            ghost_type (str): The ghost type the user wishes to get the evidence for

        Outputs:
            A message containing the inputted ghost type and it's evidence
        """

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
            message += f" > {ghost_evidence_list[i]}\n"

        # If this specific ghost has an extra slot for special evidence, print it
        if len(ghost_evidence_list) == 5:
            message += f"\n**Special {ghost_type} evidence:** {ghost_evidence_list[4]}"

        await interaction.followup.send(message)

    # autocomplete function for ghostevidence command
    @ghostevidence.autocomplete("ghost_type")
    async def ghostevidence_autocompletion(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        """Autocomplete helper method for ghostevidence command
        Uses a list of possible autocomplete options and updates the list based on what
        the user is currently typing in

        Args:
            current (str): Current text that is being typed by the user

        Outputs:
            A data list containing possible autocomplete options
        """

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
        """Command to display what ghost you have
        Grabs a random ghost from the list of all ghosts and displays the ghost type

        Outputs:
            A random ghost name and displays as a message
        """

        await interaction.response.send_message(f"It's a {random.choice(ghost_list)} !")

    @app_commands.command(description="Finds possible ghosts based on given evidence (must enter at least one evidence)")
    async def possibleghosts(self, interaction: discord.Interaction, evidence_1: str, evidence_2: str = 'None', evidence_3: str = 'None'):
        """Command to get list of possible ghost
        Takes 1-3 evidence types from the user and creates a list of possible ghosts from those evidence types.
        At least 1 evidence type is required, but the other 2 are optional

        Args:
            evidence_1 (str): string for a desired evidence type
            evidence_2 (str)[optional]: string for a desired evidence type
            evidence_3 (str)[optional]: string for a desired evidence type

        Outputs:
            A message containing a list of ghosts defined by the given evidence types
        """

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
            possible_ghosts = set(possible_list1).intersection(
                set(possible_list2).intersection(possible_list3))

        # For every item in the list, if the item is a ghost, append it to the output string
        if len(possible_ghosts) == 0:
            await interaction.followup.send("Erorr: No ghosts match those given evidences")
        else:
            for ghost in possible_ghosts:
                output += " > " + ghost + "\n"
            await interaction.followup.send(output)

    # autocomplete functions for possibleghost command

    @possibleghosts.autocomplete("evidence_1")
    @possibleghosts.autocomplete("evidence_2")
    @possibleghosts.autocomplete("evidence_3")
    async def possibleghost_autocompletion(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        """Autocomplete helper method for possibleghosts command
        Uses a list of possible autocomplete options and updates the list based on what
        the user is currently typing in. This one autocompletes for each of the 3 evidences

        Args:
            current (str): Current text that is being typed by the user

        Outputs:
            A data list containing possible autocomplete options
        """
        data = []
        choices = evidence_list

        for choice in choices:
            data.append(app_commands.Choice(name=choice, value=choice))
        return data

    @app_commands.command(description="Starts a smudge timer")
    async def smudge(self, interaction: discord.Interaction):
        """Command to start a smudge timer
        Starts a smudge timer and alerts at 60s, 90s, and 180s. 

        Outputs:
            A message at 60s, 90s, and 180s for when Demons, Normal Ghosts, and Spirits
            can start hunts after a smudge stick as been used
        """

        await interaction.response.defer()

        demon_duration = 5
        normal_duration = 10
        spirit_duration = 15

        await interaction.channel.send(f"**Smudge timer has started for {spirit_duration} seconds**")

        # Timer for Demons (60s)
        await asyncio.sleep(demon_duration)
        await interaction.channel.send(f"> {demon_duration} seconds have passed. Demons can now hunt")

        # Timer for Normal Ghosts (90s)
        await asyncio.sleep(normal_duration - demon_duration)
        await interaction.channel.send(f"> {normal_duration} seconds have passed. Normal Ghosts can now hunt")

        # Timer for Spirits (180s)
        await asyncio.sleep(spirit_duration - normal_duration)
        await interaction.channel.send(f"> {spirit_duration} seconds have passed. Spirit can now hunt")
