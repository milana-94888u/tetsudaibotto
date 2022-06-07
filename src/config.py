import logging

import os
import json

from log_config import configure_logging


def get_bool_variable(name: str, default: bool = False) -> bool:
    value = os.environ.get(name, None)
    if value is None:
        return default
    else:
        return value.lower() in ("true", "1")


def load_commands_language_aliases_from_json(
    path: str, default_language: str = "en"
) -> dict:
    with open(path) as f:
        data = json.load(f)
    commands = {
        command: {default_language: aliases}
        for command, aliases in data.pop(default_language).items()
    }
    for language in data:
        for command in commands.keys():
            commands[command].update({language: data[language][command]})
    return commands


def load_discord_display_translations(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


# Logging
ENABLE_LOGGING = get_bool_variable("ENABLE_LOGGING", False)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Localization
LOCALIZATION_PATH = os.getenv("LOCALIZATION_PATH", "../localization")

# Goolabs
GOOLABS_APP_ID = os.getenv("GOOLABS_APP_ID")

# Discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_BOT_DEFAULT_LANGUAGE = os.getenv(
    "DISCORD_BOT_DEFAULT_LANGUAGE", "en"
).casefold()
DISCORD_LANGUAGE_ALIASES = load_commands_language_aliases_from_json(
    os.path.join(LOCALIZATION_PATH, "discord_commands.json")
)
DISCORD_DISPLAY_TRANSLATIONS = load_discord_display_translations(
    os.path.join(LOCALIZATION_PATH, "discord_display.json")
)


if ENABLE_LOGGING:
    configure_logging(
        {
            "services.goolabs.utils": (
                LOG_LEVEL,
                ["default_console", "goolabs_service_file"],
            )
        }
    )
else:
    logging.disable()
