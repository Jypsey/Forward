from pyrogram import Client, filters
from bot.database import DatabaseManager
import os
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ForwarderBot:
    def __init__(self, api_id, api_hash, bot_token, db):
        self.app = Client("forwarder_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
        self.db = db
        self.config = {"target_chat": None}  # You can load this from a file if needed

    async def upload_media(self):
        while True:
            try:
                pending_media = await self.db.get_pending_media()
                if not pending_media:
                    await asyncio.sleep(10)
                    continue

                for media_id, file_path, caption, is_video in pending_media:
                    try:
                        if is_video:
                            await self.app.send_video(
                                chat_id=self.config["target_chat"],
                                video=file_path,
                                caption=caption
                            )
                        else:
                            await self.app.send_document(
                                chat_id=self.config["target_chat"],
                                document=file_path,
                                caption=caption
                            )

                        # Mark media as completed in the database
                        await self.db.mark_completed(media_id)
                        logger.info(f"Uploaded media {media_id} successfully")
                        
                        # Cleanup file
                        if os.path.exists(file_path):
                            os.remove(file_path)

                    except Exception as e:
                        logger.error(f"Upload error: {e}")
                        await asyncio.sleep(10)

                # Periodic cleanup
                await self.db.cleanup_completed()

            except Exception as e:
                logger.error(f"Uploader error: {e}")
                await asyncio.sleep(30)

    async def run(self):
        await self.app.start()
        me = await self.app.get_me()
        logger.info(f"Forwarder bot started as @{me.username}")

        await self.upload_media()
