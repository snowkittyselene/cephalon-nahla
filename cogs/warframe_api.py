import discord
from discord import app_commands as ac
from discord.ext import commands
from utils import PaginationView
import requests


ITEMS_PER_PAGE = 10
DUCATS = "<:wf_ducats:1327770728917110874>"
CREDITS = "<:wf_credits:1327770773158363267>"


class WarframeAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} cog loaded!")
        self.add_view()

    @ac.command(
        name="baro",
        description="Shows Baro Ki'Teer's current inventory or when he's next due",
    )
    async def baro(self, ctx: discord.Interaction):
        response = pull_from_api("voidTrader")
        api_data = response.json()
        start = 0
        if not api_data["active"]:
            await ctx.response.send_message(
                f"I'm so sorry, Tenno, but Baro Ki'Teer is currently ~~pregnant~~ scouring the Void for hidden treasures. He will be due to arrive at {api_data["location"]} in approximately {api_data["startString"]}"
            )
            return
        inventory = []
        for item in api_data["inventory"]:
            ducat_value, credit_value = 0, 0
            if item["credits"] is not None:
                credit_value = item["credits"]
            if item["ducats"] is not None:
                ducat_value = item["ducats"]
            inventory.append([item["item"], ducat_value, credit_value])
        is_one_page = len(inventory) <= ITEMS_PER_PAGE
        data = (api_data["location"], api_data["endString"])
        embed = await generate_base(start, inventory, data)
        view = PaginationView(inventory, data, ITEMS_PER_PAGE, 30, generate_base)
        if is_one_page:
            view.clear_items()
        await ctx.response.send_message(embed=embed, view=view)

    @ac.command(
        name="worldstate",
        description="Gets the current state of the open world locations",
    )
    async def worldstate(self, ctx: discord.Interaction):
        embed = discord.Embed(
            title="Current world data", description="Open worlds and Earth plant cycle"
        )
        # cetus
        cetus_response = pull_from_api("cetusCycle")
        cetus_data = cetus_response.json()
        embed.add_field(
            name="Plains of Eidolon (Earth)",
            value=f"{cetus_data["state"].title()} - Changing in {cetus_data["timeLeft"]}",
            inline=False,
        )
        # earth plants
        plants_reponse = pull_from_api("earthCycle")
        plants_data = plants_reponse.json()
        embed.add_field(
            name="Earth Day/Night Cycle (Plants)",
            value=f"{plants_data["state"].title()} - Changing in {plants_data["timeLeft"]}",
            inline=False,
        )
        # fortuna
        fortuna_response = pull_from_api("vallisCycle")
        fortuna_data = fortuna_response.json()
        embed.add_field(
            name="Orb Vallis (Venus)",
            value=f"{fortuna_data["state"].title()} - Changing in {fortuna_data["timeLeft"]}",
            inline=False,
        )
        # cambion drift
        deimos_response = pull_from_api("cambionCycle")
        deimos_data = deimos_response.json()
        embed.add_field(
            name="Cambion Drift (Deimos)",
            value=f"{deimos_data["state"].title()} - Changing in {deimos_data["timeLeft"]}",
            inline=False,
        )
        # duviri
        duviri_response = pull_from_api("duviriCycle")
        duviri_data = duviri_response.json()
        embed.add_field(
            name="Duviri",
            value=f"Current spiral: {duviri_data["state"].title()}",
            inline=False,
        )

        await ctx.response.send_message(embed=embed)

    @ac.command(name="circuit", description="Gets the current rewards for the Circuit")
    async def circuit(self, ctx: discord.Interaction):
        circuit_response = pull_from_api("duviriCycle")
        circuit_data = circuit_response.json()
        regular_rewards = circuit_data["choices"][0]["choices"]
        steel_path_rewards = circuit_data["choices"][1]["choices"]
        embed = discord.Embed(
            title="The Circuit - Rewards",
            description="Warframes and Incarnon Geneses",
        )
        embed.add_field(name="Normal Circuit", value="Warframes", inline=False)
        for reward in regular_rewards:
            embed.add_field(name=reward, value="")
        embed.add_field(
            name="Steel Path Circuit", value="Incarnon Geneses", inline=False
        )
        for reward in steel_path_rewards:
            embed.add_field(name=reward, value="")

        await ctx.response.send_message(embed=embed)


async def generate_base(start, inventory, info):
    current_page_inv = inventory[start : start + ITEMS_PER_PAGE]
    current_page = (start // ITEMS_PER_PAGE) + 1
    total_pages = (len(inventory) // ITEMS_PER_PAGE) + 1
    embed = discord.Embed(
        title=f"Void Trader surfaced at {info[0]}",
        description=f"Baro's inventory, page {current_page} of {total_pages}",
    )
    embed.set_author(name="The wait is over, Tenno! Baro Ki'Teer has arrived~")
    embed.set_footer(text=f"Void Trader leaving in {info[1]}")
    for item in current_page_inv:
        embed.add_field(
            name=item[0],
            value=f"{item[1]} {DUCATS} and {item[2]:,} {CREDITS}",
            inline=False,
        )
    return embed


def pull_from_api(section=None):
    url = "https://api.warframestat.us/pc"
    if section:
        url += f"/{section}"
    return requests.get(url)


async def setup(bot):
    await bot.add_cog(WarframeAPI(bot))
