import asyncio
import logging
import os
import sys
from aiohttp import web

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID
from database import init_db
import handlers_admin
import handlers_worker
import handlers_xodim
from scheduler import daily_scheduler


async def handle(request):
    return web.Response(text="Bot is running!")


async def start_dummy_web():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"Dummy web server started on port {port}")


async def main():
    logging.basicConfig(level=logging.INFO)

    if BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE" or not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN sozlanmagan. config.py faylida yoki BOT_TOKEN environment "
            "variable orqali @BotFather bergan tokenni kiriting."
        )
    if ADMIN_ID == 0:
        raise RuntimeError(
            "ADMIN_ID sozlanmagan. config.py faylida yoki ADMIN_ID environment "
            "variable orqali o'zingizning Telegram ID raqamingizni kiriting "
            "(@userinfobot orqali bilib olishingiz mumkin)."
        )

    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(handlers_admin.router)
    dp.include_router(handlers_worker.router)
    dp.include_router(handlers_xodim.router)

    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start dummy web server for Render's port-binding requirement
    if os.getenv("PORT"):
        await start_dummy_web()
        
    asyncio.create_task(daily_scheduler(bot))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
