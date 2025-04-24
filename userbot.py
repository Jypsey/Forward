import os
import asyncio
import logging
import json
from pyrogram import Client, filters
from db import Database
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Userbot")

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
USER_SESSION = os.getenv("USER_SESSION")

class UserBot:
    def __init__(self):
        self.db = Database()
        self.app = Client(
            name="userbot",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=USER_SESSION
        )
        self.config = self.load_config()

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except:
            return {"source_chat": None, "target_chat": None}

    async def start(self):
        @self.app.on_message(filters.chat(self.config["source_chat"]) & (filters.video | filters.document))
        async def handler(client, message):
            try:
                file_path = await message.download()
                is_video = bool(message.video)
                caption = message.caption or ""
                self.db.add_media(file_path, caption, is_video)
                logger.info(f"Downloaded and saved: {file_path}")
            except Exception as e:
                logger.error(f"Error downloading: {e}")

        await self.app.start()
        logger.info("Userbot started")
        await idle()

if __name__ == "__main__":
    userbot = UserBot()
    asyncio.run(userbot.start())
