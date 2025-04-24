import asyncio
from userbot import UserBot
from bot import Bot

async def main():
    userbot = UserBot()
    bot = Bot()
    
    await asyncio.gather(
        userbot.run(),
        bot.start()
    )

if __name__ == "__main__":
    asyncio.run(main())
