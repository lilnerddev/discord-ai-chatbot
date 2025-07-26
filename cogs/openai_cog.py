import discord
from discord.ext import commands
from discord import app_commands
from openai import OpenAI
import asyncio
import os
from config import SYSTEM_PROMPT

class OpenAICog(commands.Cog):
    """A class that provides the ability to send and recieve messages from an LLM (currently only supports OpenAI)."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # Expects OPENAI_API_KEY in env

    @app_commands.command(name="talk", description="Talk to this discord bot")
    async def talk(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()  # thinking indicator
        reply = await self.getAIResponse(message)
        await interaction.followup.send(reply)

    
    async def getAIResponse(self, user_message: str) -> str:
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ]
            )
            print(f"Total tokens: {response.usage.total_tokens} (prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens})")
            reply = response.choices[0].message.content
            return reply

        except Exception as e:
            error = f"OpenAICog error in getAIResponse: {e}"
            print(error)
            return error

async def setup(bot: commands.Bot):
    """
    Adds the cog to the bot. This should be defined at the 
    end of the cog file, outside of the cog class.
    """
    await bot.add_cog(OpenAICog(bot))