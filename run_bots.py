import asyncio
from bot.userbot import Userbot
from bot.main import ForwarderBot
from bot.database import DatabaseManager

# Initialize database manager
db = DatabaseManager()

# Initialize both bots
userbot = Userbot(api_id=27657909, api_hash="2387c3c1a4830bc72c32bf61a1d590e8", session_string="BQGmBrUAuoW_Tpw4JesKnP-HuwlJq1_K0VCpDEYCorrZhcYcds5-MZoJp4gyFKvIQGbkrfmbYOekM6Je5L6EA4cpJVuHmtsze4eI8wv6NMGHDJ3sifNp6JG9vXtqUELz4MKFEATrfM19pWHGdAlpEV87oIyYNN1VGSAAZKBfJyAaGSXbTyqvnfrEjOt3pPZGiC5YayNO0TpkI8pTbF6aXUy-2GM0lZVqNvyzxiAiN8RD9jqTn0iH3JzSI8cumTvdELy7hRudeB-6MuCMmCbiGuzdZGDUuXs0VP8hfOIBwGCmOYy22GAkOMV4eeorzw5OJHtvIacWcfJXBIx5eqIsLSwvv7QoswAAAAHeX_-CAA", db=db)
forwarder_bot = ForwarderBot(api_id=27657909, api_hash="2387c3c1a4830bc72c32bf61a1d590e8", bot_token="7702796376:AAHtPdFCGbF4BqdOMYLP2JeIa4J0SATf3IE", db=db)

# Run both bots asynchronously
async def main():
    await asyncio.gather(
        userbot.run(),
        forwarder_bot.run()
    )

if __name__ == "__main__":
    asyncio.run(main())
