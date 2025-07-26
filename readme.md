# Discord AI Chatbot

This chatbot has the following features:

- Use slash commands to /play, /queue, /pause, /skip, and /resume songs. Use /stop to stop all music.

# Set up

1. Clone or download the repository to a local folder

2. Open a terminal and navigate to the repository folder

3. Run the following to create and activate a virtual environment. \
   `python venv venv` \
   `./venv/activate`

4. Run `pip install requirements.txt` to install dependencies.

5. Place ffmpeg.exe in bin/ffmpeg/ffmpeg.exe. FFmpeg can be downloaded here: https://www.ffmpeg.org/download.html.

6. Create a new .env file in the top-level directory and add your discord bot token. \
   `DISCORD_TOKEN=<Put your token here>`
