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
        self.semaphore = asyncio.Semaphore(5) # Instantiate a semphore to limit number of concurrent requests

    @app_commands.command(name="talk", description="Talk to this discord bot")
    async def talk(self, interaction: discord.Interaction, message: str):
        await interaction.response.defer()  # thinking indicator
        reply = await self.getAIResponse(message)
        await interaction.followup.send(reply)

    async def getAIResponse(self, user_message: str) -> str:
        # Exit if the given message is None or empty ("") after removing extra whitespace.
        user_message = user_message.strip()
        if not user_message:
            return "No message detected."
        
        try:
            # Enforce a timeout so that the program doesn't hang forever if something goes wrong here.
            async with asyncio.timeout(15): 
                async with self.semaphore: # Obtain a semaphore lock to limit the number of concurrent requests
                    response = await asyncio.to_thread(
                        self.client.chat.completions.create,
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": user_message},
                        ]
                    )
        except asyncio.TimeoutError:
            error = f"Error: {e}"
            return "I'm taking too long to process your request. Please try again later."
        except Exception as e:
            error = f"Error: {e}"
            print(error)
            return error
        
        print(f"Tokens: {response.usage.total_tokens} (prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens})")
        reply = response.choices[0].message.content
        return reply

async def setup(bot: commands.Bot):
    """
    Adds the cog to the bot. This should be defined at the 
    end of the cog file, outside of the cog class.
    """
    await bot.add_cog(OpenAICog(bot))