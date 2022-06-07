import config


class Translator:
    def __init__(self, language: str) -> None:
        self.language = language
        self.default_language = config.DISCORD_BOT_DEFAULT_LANGUAGE
        self.translations = config.DISCORD_DISPLAY_TRANSLATIONS

    def __call__(self, token: str) -> str:
        return self.translations.get(
            self.language, self.translations.get(self.default_language, {})
        ).get(token, self.translations.get(self.default_language, {}).get(token, token))
