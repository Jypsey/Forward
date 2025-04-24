from pyrogram import Client, filters
import os
import logging
from bot.database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Userbot:
    def __init__(self, api_id, api_hash, session_string, db):
        self.app = Client(session_string, api_id=api_id, api_hash=api_hash)
        self.db = db
        self.config = {"source_chat": None}  # You can load this from a file if needed

    async def download_handler(self, client, message):
        if message.video or message.document:
            try:
                file_path = await message.download()
                is_video = bool(message.video)

                # Save media info to the database
                await self.db.add_media(
                    file_id=str(message.id),
                    file_path=file_path,
                    caption=message.caption or "",
                    is_video=is_video,
                    source_message_id=message.id
                )

                logger.info(f"Stored media {message.id} in database")
            except Exception as e:
                logger.error(f"Download error: {e}")

    async def run(self):
        await self.app.start()
        # Assuming source_chat is set
        self.app.add_handler(filters.chat(self.config["source_chat"]) & 
                             (filters.video | filters.document), 
                             self.download_handler)

        me = await self.app.get_me()
        logger.info(f"Userbot started as {me.first_name}")

        while True:
            await asyncio.sleep(60)
