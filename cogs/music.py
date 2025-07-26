import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio
from collections import deque
import os

# Dynamically construct the path to ffmpeg
FFMPEG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "bin", "ffmpeg", "ffmpeg.exe"))

class Music(commands.Cog):
    """A class that provides slash commands to queue, play, skip, resume and stop tracks."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.song_queues = {} # Create a Dictionary of queues for queueing songs for each guild/server

    @staticmethod
    def _extract(query, ydl_opts):
        """Perform the youtube query search and return the information"""
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(query, download=False)
        

    async def search_ytdlp_async(self, query, opts):
        """Get the current thread that is executing and create a separate"""
        # Get the current thread
        loop = asyncio.get_running_loop()
        # Run the _extract function in a separate thread
        return await loop.run_in_executor(None, lambda: self._extract(query, opts))


    @app_commands.command(name="play", description="Play a song or add it to the queue.")
    @app_commands.describe(song_query="Search query")
    async def play(self, interaction: discord.Interaction, song_query: str):
        """Query the requested song on youtube and add the song to the queue."""

        # Defer the response, which indicates to discord that this command might take >3s to process
        await interaction.response.defer()
        
        # Check if user is currently in a voice channel
        voice = interaction.user.voice
        if not voice or not voice.channel:
            await interaction.followup.send("You must be in a voice channel")
            return
        voice_channel = voice.channel
        
        # If not in the user's voice channel, connect to the user's voice channel,
        # or move to it if already in a different voice channel.
        voice_client = interaction.guild.voice_client
        if voice_client is None:
            voice_client = await voice_channel.connect()
        elif voice_channel != voice_client.channel:
            await voice_client.move_to(voice_channel)

        # Set youtube search options
        ytdlp_options = {
            "format": "bestaudio[abr<=96]/bestaudio",
            "noplaylist": True,
            "youtube_include_dash_manifest": False,
            "youtube_include_hls_manifest": False,
        }
        query = "ytsearch1: " + song_query # Only search for the top result

        # Get search results
        results = await self.search_ytdlp_async(query, ytdlp_options)
        if not results:
            await interaction.followup.send("No results found. :(")
            return
        tracks = results.get("entries", [])
        if not tracks:
            await interaction.followup.send("No tracks found.")
            return
                
        # Parse track url and title
        first_track = tracks[0]
        audio_url = first_track["url"]
        title = first_track.get("title", "Untitled")
        
        # Initialize queue for the server if no queue exists yet
        guild_id = str(interaction.guild_id)
        if self.song_queues.get(guild_id) is None:
            self.song_queues[guild_id] = deque()

        # Append the song request to the queue. Play immediately if no songs are currently playing.
        self.song_queues[guild_id].append((audio_url, title))
        if voice_client.is_playing() or voice_client.is_paused():
            await interaction.followup.send(f"Added to queue: **{title}**")
        else:
            await interaction.followup.send(f"Now playing: **{title}**")
            await self.play_next_song(voice_client, guild_id, interaction.channel)


    @app_commands.command(name="skip", description="Skips the current song")
    async def skip(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
            voice_client.stop() # End the current song
            await interaction.response.send_message("Skipped the current song.")
        else:
            await interaction.response.send_message("Not playing anything to skip.")


    @app_commands.command(name="pause", description="Pause the currently playing song.")
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client

        # Check if the bot is in a voice channel
        if voice_client is None:
            return await interaction.response.send_message("I'm not in a voice channel.")

        # Check if something is actually playing
        if not voice_client.is_playing():
            return await interaction.response.send_message("Nothing is currently playing.")
        
        # Pause the track
        voice_client.pause()
        await interaction.response.send_message("Playback paused!")


    @app_commands.command(name="stop", description="Stop playback and clear the queue.")
    async def stop(self, interaction: discord.Interaction):
        await interaction.response.defer()
        voice_client = interaction.guild.voice_client

        # Check if the bot is in a voice channel
        if not voice_client or not voice_client.is_connected():
            return await interaction.followup.send("I'm not connected to any voice channel.")

        # Clear the guild's queue
        guild_id_str = str(interaction.guild_id)
        if guild_id_str in self.song_queues:
            self.song_queues[guild_id_str].clear()

        # If something is playing or paused, stop it
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()

        await interaction.followup.send("Stopped playback and disconnected!")

        # (Optional) Disconnect from the channel
        await voice_client.disconnect()


    @app_commands.command(name="resume", description="Resume the currently paused song.")
    async def resume(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client

        # Check if the bot is in a voice channel
        if voice_client is None:
            return await interaction.response.send_message("I'm not in a voice channel.")

        # Check if it's actually paused
        if not voice_client.is_paused():
            return await interaction.response.send_message("I’m not paused right now.")
        
        # Resume playback
        voice_client.resume()
        await interaction.response.send_message("Playback resumed!")


    async def play_next_song(self, voice_client, guild_id, channel):
        print(f"Queue - {len(self.song_queues[guild_id])} songs left in queue")
        if self.song_queues[guild_id]:
            audio_url, title = self.song_queues[guild_id].popleft()
            print(f"Next up: {title}")

            # Set ffmeg options
            #   -reconnect 1 -> try to reconnect to audio source if connection lost
            #   -reconnected_stream 1 -> try to reconnect to audio stream if connection lost
            #   -reconnect_delay_max 5 -> max delay in seconds between connection attempts
            #   -vn -> disable video processing
            #   -c:a libopus -> use opus codec to encode audio streams
            #   -b:a 96k -> set audio bitrate to 96 kilobits per second
            ffmpeg_options = {
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                "options": "-vn -c:a libopus -b:a 96k",
            }

            # Generate the audio source
            source = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options, executable=FFMPEG_PATH)

            # Define a new function to be run after we finish playing the current song.
            def after_play(error):
                if error:
                    print(f"Error playing {title}: {error}")
                # Call play_next_song from the bot's main thread / event loop
                asyncio.run_coroutine_threadsafe(self.play_next_song(voice_client, guild_id, channel), self.bot.loop)

            # Play the audio and notify the channel of the song title
            voice_client.play(source, after=after_play)
            asyncio.create_task(channel.send(f"Now playing: **{title}**"))
        else:
            await voice_client.disconnect()
            self.song_queues[guild_id] = deque()


async def setup(bot: commands.Bot):
    """
    Adds the cog to the bot. This should be defined at the 
    end of the cog file, outside of the cog class.
    """
    await bot.add_cog(Music(bot))