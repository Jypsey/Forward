from pyrogram import Client, filters
from pyrogram.types import Message
from database.manager import DatabaseManager

async def set_source(client: Client, message: Message):
    chat_id = message.text.split(" ", 1)[1]
    await client.send_message(message.chat.id, f"Source channel set to {chat_id}")
    client.config["source_chat"] = chat_id

async def set_target(client: Client, message: Message):
    chat_id = message.text.split(" ", 1)[1]
    await client.send_message(message.chat.id, f"Target channel set to {chat_id}")
    client.config["target_chat"] = chat_id

async def start_forward(client: Client, message: Message):
    source_chat = client.config.get("source_chat")
    target_chat = client.config.get("target_chat")
    
    if not source_chat or not target_chat:
        await client.send_message(message.chat.id, "Please set source and target channels first.")
        return
    
    forwarder = client.get_forwarder()
    await forwarder.start_forwarding()

async def check_status(client: Client, message: Message):
    forwarder = client.get_forwarder()
    pending_count = await forwarder.get_pending_media_count()
    await client.send_message(message.chat.id, f"Pending media: {pending_count}")

def setup_handlers(bot: Client):
    bot.add_handler(filters.command("setsource") & filters.user(bot.config["owner_id"]), set_source)
    bot.add_handler(filters.command("settarget") & filters.user(bot.config["owner_id"]), set_target)
    bot.add_handler(filters.command("startforward") & filters.user(bot.config["owner_id"]), start_forward)
    bot.add_handler(filters.command("status") & filters.user(bot.config["owner_id"]), check_status)
