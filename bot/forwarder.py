import os
import asyncio
from pyrogram.errors import FloodWait
from database.manager import DatabaseManager

class Forwarder:
    def __init__(self, client: Client, db: DatabaseManager):
        self.client = client
        self.db = db

    async def start_forwarding(self):
        pending_media = await self.db.get_pending_media()
        total_media = len(pending_media)
        for idx, (media_id, file_path, caption, is_video) in enumerate(pending_media):
            progress = f"Forwarding {idx+1}/{total_media}..."
            await self.client.send_message(self.client.config["target_chat"], progress)

            try:
                if is_video:
                    await self.client.send_video(self.client.config["target_chat"], video=file_path, caption=caption)
                else:
                    await self.client.send_document(self.client.config["target_chat"], document=file_path, caption=caption)

                await self.db.mark_completed(media_id)
                os.remove(file_path)
                await self.client.send_message(self.client.config["target_chat"], f"Uploaded: {file_path}")

            except FloodWait as e:
                await asyncio.sleep(e.x)
            except Exception as e:
                await self.client.send_message(self.client.config["target_chat"], f"Error: {e}")

    async def get_pending_media_count(self):
        return len(await self.db.get_pending_media())
