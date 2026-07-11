import asyncio
import logging
import re
from datetime import datetime, date, timedelta
from config import ADMIN_ID
import database as db

# Setup logging
logger = logging.getLogger("scheduler")

async def send_tomorrow_notifications(bot):
    logger.info("Running send_tomorrow_notifications job...")
    tomorrow = date.today() + timedelta(days=1)
    
    # Fetch all active pending orders
    orders = await db.get_orders_by_statuses(['yuborilgan', 'qabul_qilingan'])
    
    # Group orders by worker
    worker_orders = {}
    for o in orders:
        sana_str = o.get("sana", "").strip()
        # Normalize separators to dots and remove spaces
        sana_str = re.sub(r'[\s\-/]+', '.', sana_str)
        
        parsed_date = None
        # Try parsing date formats: DD.MM.YYYY, DD.MM.YY, YYYY.MM.DD, DD.MM
        for fmt in ("%d.%m.%Y", "%d.%m.%y", "%Y.%m.%d", "%d.%m"):
            try:
                if fmt == "%d.%m":
                    parsed_date = datetime.strptime(sana_str, fmt).date().replace(year=tomorrow.year)
                else:
                    parsed_date = datetime.strptime(sana_str, fmt).date()
                break
            except ValueError:
                continue
        
        # Fallback manual numeric splitting
        if parsed_date is None:
            parts = [int(p) for p in re.findall(r'\d+', sana_str)]
            if len(parts) == 3:
                if parts[0] > 1000:
                    parsed_date = date(parts[0], parts[1], parts[2])
                else:
                    year = parts[2]
                    if year < 100:
                        year += 2000
                    parsed_date = date(year, parts[1], parts[0])
            elif len(parts) == 2:
                parsed_date = date(tomorrow.year, parts[1], parts[0])
        
        if parsed_date == tomorrow:
            worker_id = o["worker_id"]
            if worker_id not in worker_orders:
                worker_orders[worker_id] = []
            worker_orders[worker_id].append(o)
            
    # Send notifications to each worker
    for worker_id, orders_list in worker_orders.items():
        worker = await db.get_worker_by_id(worker_id)
        if not worker:
            continue
        
        lines = [
            f"🔔 **Eslatma!** Ertaga ({tomorrow.strftime('%d.%m.%Y')}) sizda {len(orders_list)} ta buyurtma bor:\n"
        ]
        for i, o in enumerate(orders_list, 1):
            lines.append(
                f"{i}. 🏪 Magazin: {o['magazin_kodi']}\n"
                f"📍 Manzil: {o['manzil']}\n"
                f"📐 Taxminiy arka: {o.get('arka_metr', 0)} metr\n"
                f"🔴 Qizil: {o.get('qizil', 0)} dona, ⚪ Oq: {o.get('oq', 0)} dona\n"
                f"🟠 Orange: {o.get('orange', 0)} dona, 🟡 Sariq: {o.get('sariq', 0)} dona\n"
            )
        
        text = "\n".join(lines)
        try:
            await bot.send_message(worker["tg_id"], text)
            logger.info(f"Sent tomorrow reminder to worker {worker['ism']} (ID: {worker['tg_id']})")
        except Exception as e:
            logger.error(f"Failed to send reminder to worker {worker['ism']}: {e}")

async def daily_scheduler(bot):
    logger.info("Daily reminder scheduler started.")
    while True:
        now = datetime.now()
        # Target time is 19:00 today
        target = now.replace(hour=19, minute=0, second=0, microsecond=0)
        if now >= target:
            # If 19:00 has already passed, schedule for tomorrow
            target += timedelta(days=1)
            
        sleep_seconds = (target - now).total_seconds()
        logger.info(f"Scheduler will run next at {target} (sleeping for {sleep_seconds:.1f} seconds)")
        await asyncio.sleep(sleep_seconds)
        
        try:
            await send_tomorrow_notifications(bot)
        except Exception as e:
            logger.error(f"Error in send_tomorrow_notifications: {e}")
        
        # Prevent double triggering within the same minute
        await asyncio.sleep(60)
