import json
from pyrogram import Client
from bot.handlers import setup_handlers
from database.manager import DatabaseManager

# Read the config.json
def load_config():
    with open('config/config.json') as f:
        return json.load(f)

config = load_config()

API_ID = config["API_ID"]
API_HASH = config["API_HASH"]
BOT_TOKEN = config["BOT_TOKEN"]

# Normal Bot setup
async def run():
    bot = Client("forwarder_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
    db = DatabaseManager()
    
    # Set up handlers for commands
    setup_handlers(bot)
    
    forwarder = bot.get_forwarder()
    
    await bot.start()
    me = await bot.get_me()
    print(f"Bot started as @{me.username}")
    
    # Start forwarding and checking statuses
    await forwarder.start_forwarding()

if __name__ == "__main__":
    asyncio.run(run())
