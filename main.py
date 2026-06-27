import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")


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


bot = PotatoBot()


@bot.event
async def on_ready() -> None:
    if bot.user is None:
        return

    logging.info("Logged in as %s (ID: %s)", bot.user, bot.user.id)
    await bot.change_presence(
        activity=discord.Game(name=f"{COMMAND_PREFIX}ping"),
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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if not DISCORD_TOKEN:
        raise RuntimeError(
            "Missing DISCORD_TOKEN. Copy .env.example to .env and add your bot token."
        )

    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
