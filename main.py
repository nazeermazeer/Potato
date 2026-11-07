import logging
import os
from datetime import datetime, timezone
import discord
from discord.ext import commands
import humanize
from dotenv import load_dotenv
import textwrap
from discord.ext import tasks



load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")
LOGGER = logging.getLogger("discord.potato")


class PotatoBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self) -> None:
        await self.tree.sync()
        
    async def on_message(self, message: discord.Message):
        if str(bot.user.id) in message.content and message.author.id != bot.user.id:
            await message.add_reaction("❌")
            await change_status(discord.Status.dnd)
        elif message.author.id != bot.user.id:
            text = message.content
            pos = text.find("im")
            if (pos != -1):
                result = text[pos + len("im") :].lstrip()
                await message.reply("Hi " + result + "! I'm " + bot.user.mention)


bot = PotatoBot()


@bot.event
async def on_ready() -> None:
    if bot.user is None:
        return
    
    datestr = "2026-06-26 23:42:27"
    dateformat = "%Y-%m-%d %H:%M:%S"
    dt = datetime.strptime(datestr, dateformat)
    timestamp = int(dt.timestamp())
    global time
    time = datetime.fromtimestamp(timestamp, tz=timezone.utc)


    LOGGER.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    
    if not change_status.is_running():
        change_status.start()

    
@tasks.loop(seconds=5)
async def change_status(status=discord.Status.online) -> None:
    relative_time = humanize.naturaltime(time)
    await bot.change_presence(
    status=status,
    activity=discord.CustomActivity(name=relative_time)
)


@bot.tree.command(name="hello", description="Say hello to the bot.")
async def hello(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(
        "ok", allowed_mentions=discord.AllowedMentions.none(),
    )


def main() -> None:
    discord.utils.setup_logging(level=logging.INFO)

    if not DISCORD_TOKEN:
        raise RuntimeError(
            "Missing DISCORD_TOKEN. Copy .env.example to .env and add your bot token."
        )

    bot.run(DISCORD_TOKEN, log_handler=None)



if __name__ == "__main__":
    main()
