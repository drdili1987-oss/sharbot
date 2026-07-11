import os

# Telegram bot tokenini @BotFather dan oling va shu yerga yozing
# (yoki BOT_TOKEN nomli environment variable orqali bering)
BOT_TOKEN = os.getenv("BOT_TOKEN", "8402548265:AAGnC8b049b1Bn9hSbe2COdJfgT5v2hByp8")

# Sizning (admin) Telegram user ID raqamingiz.
# Bilish uchun @userinfobot ga /start yozing - u sizga ID raqamingizni beradi.
ADMIN_ID = int(os.getenv("ADMIN_ID", "156664"))

# Narxlar (so'mda)
ARKA_NARXI_METR = 120_000       # 1 metr shar arka narxi
LOGOTIP_NARXI_DONA = 11_000     # 1 dona shar logotip narxi
TRANSPORT_NARXI_KM = 2_000      # 1 km transport narxi

DB_PATH = os.getenv("DB_PATH", "sharbot.db")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_ODeoYbtCf5S7@ep-summer-bar-adrqqqpe-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require")
XODIM_ID = int(os.getenv("XODIM_ID", "261261387"))
