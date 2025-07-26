import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Set bot intents (permissions)
intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is online! (ID: {bot.user.id})")
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    print(await bot.tree.fetch_commands())


@bot.event
async def on_message(msg):
    print(msg.guild.id)
    if (msg.author.id != bot.user.id):
        await msg.channel.send(f"Interesting message, {msg.author.mention}")


@bot.tree.command(name="greet", description="Sends a greeting to the user")
async def greet(interaction: discord.Interaction):
    username = interaction.user.mention
    await interaction.response.send_message(f"Hello there, {username}")


async def main():
    # Load extensions
    try:
        await bot.load_extension("cogs.music")
        print("🎵 Music Cog loaded.")
    except Exception as e:
        print(f"❌ Error loading music cog: {e}")

    # Run the bot
    await bot.start(DISCORD_TOKEN)

# Launch the bot using asyncio.run() for full async context
if __name__ == "__main__":
    asyncio.run(main())

