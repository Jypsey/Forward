import os
import logging
from pyrogram import Client, filters
from database.manager import DatabaseManager

logging.basicConfig(level=logging.INFO)

class UserBot:
    def __init__(self, db: DatabaseManager):
        self.app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=USERBOT_SESSION)
        self.db = db

    async def download_media(self, client, message):
        if message.video or message.document:
            try:
                file_path = await message.download()
                is_video = bool(message.video)
                await self.db.add_media(file_id=str(message.id), file_path=file_path, caption=message.caption or "", is_video=is_video, source_message_id=message.id)
                logging.info(f"Stored media {message.id} in database.")
            except Exception as e:
                logging.error(f"Download error: {e}")

    async def run(self):
        await self.app.start()
        self.app.add_handler(filters.chat(self.config["source_chat"]) & (filters.video | filters.document), self.download_media)
        me = await self.app.get_me()
        logging.info(f"Userbot started as {me.first_name}")
        await asyncio.Event().wait()  # Keep running indefinitely
