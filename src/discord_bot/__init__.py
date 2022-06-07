from discord.ext.commands import when_mentioned_or

from .cogs import *
from multilingual_discord.ext.commands import MultilingualBot

import config


def create_bot() -> MultilingualBot:
    bot = MultilingualBot(
        command_prefix=when_mentioned_or("!", "！"),
        description="This is a Helper Bot",
        case_insensitive=True,
        default_language=config.DISCORD_BOT_DEFAULT_LANGUAGE,
    )
    bot.add_cog(GoolabsCog(bot))
    return bot
