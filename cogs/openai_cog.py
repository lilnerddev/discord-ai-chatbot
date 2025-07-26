import discord
from discord.ext import commands
from discord import app_commands
from openai import OpenAI
import asyncio
import os

class OpenAICog(commands.Cog):
    """A class that provides the ability to send and recieve messages from an LLM (currently only supports OpenAI)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = OpenAI() # Expects OPENAI_API_KEY in env

    @app_commands.command(name="talk", description="Talk to this discord bot")
    async def talk(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()  # thinking indicator

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": message},
                ]
            )
            answer = response.choices[0].message.content
            await interaction.followup.send(answer)
        except Exception as e:
            print(f"OpenAICog error: {e}")
            await interaction.followup.send(f"Error: {e}")

async def setup(bot: commands.Bot):
    """
    Adds the cog to the bot. This should be defined at the 
    end of the cog file, outside of the cog class.
    """
    await bot.add_cog(OpenAICog(bot))