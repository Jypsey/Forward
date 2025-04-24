import os
import json
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from db import Database
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Bot")

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))

class Bot:
    def __init__(self):
        self.db = Database()
        self.app = Client("forwarder_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
        self.config = self.load_config()

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except:
            return {"source_chat": None, "target_chat": None}

    def save_config(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=4)

    async def start(self):
        @self.app.on_message(filters.command("start") & filters.private)
        async def start_cmd(client, message):
            await message.reply("👋 Hello! Use /setsource, /settarget to configure chats.")

        @self.app.on_message(filters.command("setsource") & filters.user(OWNER_ID))
        async def set_source(client, message):
            if len(message.command) < 2:
                return await message.reply("Usage: /setsource <chat_id>")
            self.config["source_chat"] = int(message.command[1])
            self.save_config()
            await message.reply("✅ Source chat updated.")

        @self.app.on_message(filters.command("settarget") & filters.user(OWNER_ID))
        async def set_target(client, message):
            if len(message.command) < 2:
                return await message.reply("Usage: /settarget <chat_id>")
            self.config["target_chat"] = int(message.command[1])
            self.save_config()
            await message.reply("✅ Target chat updated.")

        async def upload_loop():
            while True:
                try:
                    pending = self.db.get_pending_media()
                    if not pending:
                        await asyncio.sleep(10)
                        continue

                    for media_id, file_path, caption, is_video in pending:
                        try:
                            if is_video:
                                await self.app.send_video(
                                    self.config["target_chat"], video=file_path, caption=caption
                                )
                            else:
                                await self.app.send_document(
                                    self.config["target_chat"], document=file_path, caption=caption
                                )
                            self.db.mark_completed(media_id)
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            logger.info(f"Uploaded media {media_id}")
                        except FloodWait as e:
                            logger.warning(f"Flood wait: {e.x}s")
                            await asyncio.sleep(e.x)
                        except Exception as e:
                            logger.error(f"Upload error: {e}")
                            await asyncio.sleep(5)

                except Exception as e:
                    logger.error(f"Loop error: {e}")
                    await asyncio.sleep(15)

        await self.app.start()
        logger.info("Bot started")
        await upload_loop()

if __name__ == "__main__":
    bot = Bot()
    asyncio.run(bot.start())
