import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
DEV_MODE = os.getenv("DEV_MODE")
DEV_GUILD_ID = os.getenv("DEV_GUILD_ID")


# Set bot intents (permissions)
intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is online! (ID: {bot.user.id})")
    try:
        if DEV_MODE == "true" and DEV_GUILD_ID:
            guild = discord.Object(id=DEV_GUILD_ID)
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"[DEV MODE] Synced {len(synced)} command(s) to guild {DEV_GUILD_ID}.")
        else:
            synced = await bot.tree.sync()
            print(f"[PROD MODE] Synced {len(synced)} global command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    # Uncomment to print out all comamnds
    print(await bot.tree.fetch_commands())


@bot.event
async def on_message(msg):
    print(msg.guild.id)
    ## TODO reply with llm if bot is mentioned 
    if (msg.author.id != bot.user.id):
        await msg.channel.send(f"Interesting message, {msg.author.mention}")

    # Allow bot to finish processing commands.
    await bot.process_commands(msg)


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
    try:
        await bot.load_extension("cogs.openai_cog")
        print("🎵 OpenAI Cog loaded.")
    except Exception as e:
        print(f"❌ Error loading OpenAI cog: {e}")

    # Run the bot
    await bot.start(os.getenv("DISCORD_TOKEN"))

# Launch the bot using asyncio.run() for full async context
if __name__ == "__main__":
    asyncio.run(main())

