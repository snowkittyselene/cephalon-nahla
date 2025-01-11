import discord
from discord.ext import commands
import requests


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
        await ctx.send(f"Today's sortie: {faction} enemy, led by {boss}")


def pull_from_api(section=None):
    url = "https://api.warframestat.us/pc"
    if section:
        url += f"/{section}"
    return requests.get(url)


async def setup(bot):
    await bot.add_cog(WarframeAPI(bot))
