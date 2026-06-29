import logging
from checker import Checker
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
        
    async def on_message(self, message):
        if str(bot.user.id) in message.content:
            await message.add_reaction("❌")
            await change_status(discord.Status.dnd)
        elif message.author.id != bot.user.id:
            checker = Checker()
            corrections = checker.checkText(message.content)
            desc = "❌ "
            feedbacklen = 20
            for i, correction in enumerate(corrections):
                # location = " "
                # correctiondesc = ""
                # for _ in range(correction.offset):
                #     location = f"{location} "
                # for _ in range(correction.error_length):
                #     location = f"{location}^"
                # msg = textwrap.fill(correction.message, width=50)
                if correction.offset <= feedbacklen:
                    msg = message.content
                    msg = msg[:correction.offset] + "__**" + msg[correction.offset:correction.offset + correction.error_length] + "**__" + msg[correction.offset + correction.error_length:]
                    msg = "\"" + msg[0:(min(correction.offset + feedbacklen, correction.offset + correction.error_length + feedbacklen))] + "\"..."
                else:
                    msg = message.content
                    msg = msg[:correction.offset] + "__**" + msg[correction.offset:correction.offset + correction.error_length] + "**__" + msg[correction.offset + correction.error_length:]
                    msg = "...\"" + msg[int(correction.offset - (feedbacklen)):int(min(correction.offset + feedbacklen, correction.offset + correction.error_length + feedbacklen))] + "\"..."
                correctiondesc = f"{msg}\n➡️ {correction.message}\n\n"
                desc += correctiondesc.replace('\n', '\n❌ ')
            desc += f"\n\"{message.content}\" 🥀 🔪 😭\n\"{checker.getCorrectedText(message.content)}\" 🌈 ❤️ 😀"
            embed = discord.Embed(
                title=f"{message.author.name}, please check your sentence.",
                description=desc,
                color=16730186
            )
            await message.reply(embed=embed)


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
    


@bot.command(name="ping")
async def ping(ctx: commands.Context) -> None:
    """Reply with the bot latency."""
    latency_ms = round(bot.latency * 1000)
    await ctx.reply(f"Pong! `{latency_ms}ms`")


@bot.tree.command(name="hello", description="Say hello to the bot.")
async def hello(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(
        f"Hello, {interaction.user.mention}!",
        allowed_mentions=discord.AllowedMentions.none(),
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
