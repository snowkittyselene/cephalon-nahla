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

    @commands.command(name="testpull")
    async def test_api_pull(self, ctx: commands.Context):
        response = pull_from_api("sortie")
        api_data = response.json()
        if "error" in api_data:
            await ctx.send(f"Error {api_data["code"]} occurred: {api_data["error"]}")
            return
        faction = api_data["faction"]
        boss = api_data["boss"]
        await ctx.send(
            f"Tenno. Today's sortie is an attack on the {faction}, currently led by {boss}"
        )

    @ac.command(
        name="baro",
        description="Shows Baro Ki'Teer's current inventory or when he's next due",
    )
    async def baro(self, original_interaction: discord.Interaction):
        response = pull_from_api("voidTrader")
        api_data = response.json()
        start = 0
        if not api_data["active"]:
            await original_interaction.response.send_message(
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
        await original_interaction.response.send_message(embed=embed, view=view)


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
