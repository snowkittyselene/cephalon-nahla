import discord
from discord.ext import commands
import requests

DUCATS = "<:wf_ducats:1327770728917110874>"
CREDITS = "<:wf_credits:1327770773158363267>"


class WarframeAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{__name__} cog loaded!")

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

    @commands.command()
    async def baro(self, ctx):
        response = pull_from_api("voidTrader")
        api_data = response.json()
        if not api_data["active"]:
            await ctx.send(
                f"I'm so sorry, Tenno, but Baro Ki'Teer is currently ~~pregnant~~ scouring the Void for hidden treasures. He will be due to arrive at {api_data["location"]} in approximately {api_data["startString"]}"
            )
            return
        inventory = []
        for item in api_data["inventory"]:
            inventory.append([item["item"], item["ducats"], item["credits"]])
        emb = discord.Embed(
            title=f"Void Trader surfaced at {api_data["location"]}",
            description="Baro's Inventory:\n",
        )
        emb.set_author(name="The wait is over, Tenno! Baro Ki'Teer has arrived...")
        emb.set_footer(text=f"Void Trader leaving in {api_data["endString"]}")
        for item in inventory:
            emb.description += (
                f"{item[0]}: {item[1]} {DUCATS} and {item[2]} {CREDITS}\n"
            )
        await ctx.send(embed=emb)


def pull_from_api(section=None):
    url = "https://api.warframestat.us/pc"
    if section:
        url += f"/{section}"
    return requests.get(url)


async def setup(bot):
    await bot.add_cog(WarframeAPI(bot))
