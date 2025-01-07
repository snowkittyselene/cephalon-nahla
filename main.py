import discord
from discord import app_commands
from config import PREFIX, BOT_TOKEN  # Sensitive content!

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    content = message.content
    tokens = content.split(" ")
    if tokens[0] == PREFIX + "test":
        await message.channel.send("Test complete.")


def main():
    client.run(BOT_TOKEN)


if __name__ == "__main__":
    main()
