from typing import Any

from discord.ext.commands.context import Context


class MultilingualContext(Context):
    def __init__(self, **attrs: Any) -> None:
        super(MultilingualContext, self).__init__(**attrs)
        self.language = attrs.pop("language", attrs.pop("default_language", None))
