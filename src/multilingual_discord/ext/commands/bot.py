from discord.ext.commands.bot import BotBase, Bot, AutoShardedBot

from .core import MultilingualCommand, MultilingualGroupMixin
from .context import MultilingualContext


class MultilingualBotBase(MultilingualGroupMixin, BotBase):
    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("help_command", None)
        super(MultilingualBotBase, self).__init__(*args, **kwargs)

    async def get_context(
        self, message, *, cls=MultilingualContext
    ) -> MultilingualContext:
        ctx = await super(MultilingualBotBase, self).get_context(message, cls=cls)
        if isinstance(ctx.command, MultilingualCommand):
            if self.case_insensitive:
                ctx.language = ctx.command.language_aliases.get(
                    ctx.invoked_with.casefold(), self.default_language
                )
            else:
                ctx.language = ctx.command.language_aliases.get(
                    ctx.invoked_with, self.default_language
                )
        return ctx


class MultilingualBot(MultilingualBotBase, Bot):
    pass


class MultilingualAutoShardedBot(MultilingualBotBase, AutoShardedBot):
    pass
