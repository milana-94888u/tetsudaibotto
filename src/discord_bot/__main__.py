from discord_bot import create_bot

import config

if __name__ == "__main__":
    create_bot().run(config.DISCORD_TOKEN)
    print("Started")
