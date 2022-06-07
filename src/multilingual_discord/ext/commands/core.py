from typing import Any, Callable, Iterable

from discord.ext.commands.core import Command, GroupMixin, Group


class MultilingualCommand(Command):
    def __init__(self, func: Callable, **kwargs: Any) -> None:
        default_language = kwargs.get("default_language", "en")
        match kwargs.get("language_aliases"):
            case None:
                super(MultilingualCommand, self).__init__(func, **kwargs)
                self.language_aliases = {
                    alias: default_language for alias in self.aliases
                }
            case dict(languages_dict) if all(
                isinstance(language, str) and isinstance(aliases, Iterable)
                for language, aliases in languages_dict.items()
            ):
                if default_aliases := kwargs.pop("aliases", None):
                    languages_dict = {
                        alias: default_language for alias in default_aliases
                    } | languages_dict
                super(MultilingualCommand, self).__init__(
                    func,
                    aliases=[
                        alias
                        for aliases in languages_dict.values()
                        for alias in aliases
                    ],
                    **kwargs,
                )
                self.language_aliases = {
                    alias: language
                    for language, aliases in languages_dict.items()
                    for alias in aliases
                }
            case _:
                raise TypeError(
                    f"Language aliases should be a dict with language names as keys and Iterable objects as values"
                )
        self.language_aliases.setdefault(self.name, default_language)


class MultilingualGroupMixin(GroupMixin):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(MultilingualGroupMixin, self).__init__(*args, **kwargs)
        self.default_language = kwargs.get("default_language", "en")

    def command(
        self, *args: Any, **kwargs: Any
    ) -> Callable[[Callable], MultilingualCommand]:
        def decorator(func: Callable) -> MultilingualCommand:
            kwargs.setdefault("parent", self)
            kwargs.setdefault("default_language", self.default_language)
            result = multilingual_command(*args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator

    def group(self, *args, **kwargs):
        def decorator(func):
            kwargs.setdefault("parent", self)
            result = multilingual_group(*args, **kwargs)(func)
            self.add_command(result)
            return result

        return decorator


class MultilingualGroup(MultilingualGroupMixin, MultilingualCommand, Group):
    pass


def multilingual_command(name: str = None, cls=None, **attrs: Any) -> Callable:
    if cls is None:
        cls = MultilingualCommand

    def decorator(func: Callable) -> cls:
        if isinstance(func, Command):
            raise TypeError("Callback is already a command.")
        return cls(func, name=name, **attrs)

    return decorator


def multilingual_group(name: str = None, **attrs: Any) -> Callable:
    attrs.setdefault("cls", MultilingualGroup)
    return multilingual_command(name=name, **attrs)
