# Discord AI Chatbot

This chatbot has the following features:

- Send the bot a message by tagging it (e.g. "@MyBot") in a channel message.
- Use slash commands to /play, /queue, /pause, /skip, and /resume songs. Use /stop to stop all music.

# Set up

1. Clone or download the repository to a local folder.

2. Open a terminal and navigate to the repository folder.

3. Run the following to create and activate a virtual environment. \
   `python -m venv .venv` \
   `.venv\Scripts\activate` \
   Note that this application was tested with python 3.13.5.

4. Run `pip install -r requirements.txt` to install dependencies.

5. Place ffmpeg.exe in bin/ffmpeg/ffmpeg.exe. FFmpeg can be downloaded here: https://www.ffmpeg.org/download.html.

6. Rename example.env in the top-level directory to just .env and add your DISCORD_TOKEN and OPENAI_API_KEY. All other environment variables can be left as they are. For those that want to tweak the bot, you can set DEV_MODE=true and specify your DEV_GUILD_ID to enable immediate syncing with your test server for slash commands. \
   `DISCORD_TOKEN=<Put your token here>` \
   `OPENAI_API_KEY=<Put your token here>`

7. Update the system prompt in config.py to give the bot a personality. For example, change the system prompt text to: \
   `SYSTEM_PROMPT = "You are Batman, the Dark Knight of Gotham."` \
   You can also ask OpenAI for a system prompt to make an AI act like **\_\_\_\_**, and fill in the blank with whatever you want!
