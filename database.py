import psycopg
from psycopg.rows import dict_row
from datetime import datetime
from config import DATABASE_URL

SCHEMA = """
CREATE TABLE IF NOT EXISTS workers (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT UNIQUE NOT NULL,
    ism TEXT NOT NULL,
    active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    magazin_kodi TEXT,
    sana TEXT,
    manzil TEXT,
    qizil INTEGER DEFAULT 0,
    oq INTEGER DEFAULT 0,
    orange INTEGER DEFAULT 0,
    sariq INTEGER DEFAULT 0,
    arka_metr REAL DEFAULT 0,
    worker_id INTEGER,
    status TEXT DEFAULT 'yuborilgan',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS execution (
    id SERIAL PRIMARY KEY,
    order_id INTEGER,
    metr REAL,
    logotip_soni INTEGER,
    transport_km REAL DEFAULT 0,
    summa REAL,
    tasdiqlangan INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS debts (
    id SERIAL PRIMARY KEY,
    worker_id INTEGER,
    order_id INTEGER,
    summa REAL,
    tolangan INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TEXT
);

CREATE TABLE IF NOT EXISTS cashflow (
    id SERIAL PRIMARY KEY,
    turi TEXT,
    summa REAL,
    izoh TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admin_debts (
    id SERIAL PRIMARY KEY,
    izoh TEXT,
    summa REAL,
    tolangan INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

async def init_db():
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(SCHEMA)
        await conn.commit()
    # Dilfuza (sharchi) — faqat yo'q bo'lsa qo'shiladi
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            # Dilfuzani sharchi sifatida qo'shish
            await cur.execute(
                "INSERT INTO workers (tg_id, ism, active) VALUES (%s, %s, 1) "
                "ON CONFLICT (tg_id) DO UPDATE SET ism = EXCLUDED.ism, active = 1",
                (2098476593, "Dilfuza")
            )
            # Dilfuzaning worker id ini olish
            await cur.execute("SELECT id FROM workers WHERE tg_id = %s", (2098476593,))
            row = await cur.fetchone()
            if row:
                worker_id = row["id"]
                # 8 610 000 so'm boshlang'ich qarz — faqat hech qarz yo'q bo'lsa yoziladi
                await cur.execute(
                    "SELECT COUNT(*) as cnt FROM debts WHERE worker_id = %s",
                    (worker_id,)
                )
                cnt_row = await cur.fetchone()
                if cnt_row and list(cnt_row.values())[0] == 0:
                    await cur.execute(
                        "INSERT INTO debts (worker_id, order_id, summa) VALUES (%s, NULL, %s)",
                        (worker_id, 8610000.0)
                    )
        await conn.commit()


# ---------- WORKERS ----------

async def add_worker(tg_id: int, ism: str):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO workers (tg_id, ism, active) VALUES (%s, %s, 1) ON CONFLICT (tg_id) DO UPDATE SET ism = EXCLUDED.ism, active = 1",
                (tg_id, ism),
            )
        await conn.commit()

async def get_worker_by_tgid(tg_id: int):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM workers WHERE tg_id = %s AND active = 1", (tg_id,))
            return await cur.fetchone()

async def get_worker_by_id(worker_id: int):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM workers WHERE id = %s", (worker_id,))
            return await cur.fetchone()

async def list_active_workers():
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM workers WHERE active = 1")
            return await cur.fetchall()

# ---------- ORDERS ----------

async def create_order(magazin_kodi, sana, manzil, qizil, oq, orange, sariq, arka_metr, worker_id):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """INSERT INTO orders (magazin_kodi, sana, manzil, qizil, oq, orange, sariq, arka_metr, worker_id, status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'yuborilgan') RETURNING id""",
                (magazin_kodi, sana, manzil, qizil, oq, orange, sariq, arka_metr, worker_id),
            )
            row = await cur.fetchone()
            await conn.commit()
            return row["id"] if row else None

async def get_order(order_id: int):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
            return await cur.fetchone()

async def set_order_status(order_id: int, status: str):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE orders SET status = %s WHERE id = %s", (status, order_id))
        await conn.commit()

async def list_worker_orders(worker_id: int, status: str = None):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            if status:
                await cur.execute(
                    "SELECT * FROM orders WHERE worker_id = %s AND status = %s ORDER BY id DESC",
                    (worker_id, status),
                )
            else:
                await cur.execute(
                    "SELECT * FROM orders WHERE worker_id = %s ORDER BY id DESC", (worker_id,)
                )
            return await cur.fetchall()

async def list_orders_by_status(status: str = None, limit: int = 20):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            if status:
                await cur.execute(
                    "SELECT * FROM orders WHERE status = %s ORDER BY id DESC LIMIT %s", (status, limit)
                )
            else:
                await cur.execute("SELECT * FROM orders ORDER BY id DESC LIMIT %s", (limit,))
            return await cur.fetchall()

async def get_orders_by_statuses(statuses: list):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            placeholders = ",".join("%s" for _ in statuses)
            await cur.execute(
                f"SELECT * FROM orders WHERE status IN ({placeholders})",
                statuses
            )
            return await cur.fetchall()

# ---------- EXECUTION ----------

async def create_execution(order_id, metr, logotip_soni, transport_km, summa):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """INSERT INTO execution (order_id, metr, logotip_soni, transport_km, summa)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (order_id, metr, logotip_soni, transport_km, summa),
            )
            row = await cur.fetchone()
            await conn.commit()
            return row["id"] if row else None

async def get_execution(execution_id: int):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM execution WHERE id = %s", (execution_id,))
            return await cur.fetchone()

async def confirm_execution(execution_id: int):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute("UPDATE execution SET tasdiqlangan = 1 WHERE id = %s", (execution_id,))
        await conn.commit()

# ---------- DEBTS ----------

async def create_debt(worker_id: int, order_id: int, summa: float):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO debts (worker_id, order_id, summa) VALUES (%s, %s, %s)",
                (worker_id, order_id, summa),
            )
        await conn.commit()

async def get_unpaid_debts_summary():
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """SELECT w.id, w.ism, COALESCE(SUM(d.summa), 0) as jami
                   FROM workers w
                   LEFT JOIN debts d ON d.worker_id = w.id AND d.tolangan = 0
                   WHERE w.active = 1
                   GROUP BY w.id, w.ism"""
            )
            return await cur.fetchall()

async def mark_worker_debts_paid(worker_id: int):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE debts SET tolangan = 1, paid_at = %s WHERE worker_id = %s AND tolangan = 0",
                (datetime.now().isoformat(), worker_id),
            )
        await conn.commit()

async def get_worker_unpaid_debt(worker_id: int) -> float:
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT COALESCE(SUM(summa), 0) FROM debts WHERE worker_id = %s AND tolangan = 0",
                (worker_id,),
            )
            row = await cur.fetchone()
            return list(row.values())[0] if row else 0.0

# ---------- CASHFLOW ----------

async def add_cashflow(turi: str, summa: float, izoh: str):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO cashflow (turi, summa, izoh) VALUES (%s, %s, %s)", (turi, summa, izoh)
            )
        await conn.commit()

async def list_cashflow(limit: int = 20):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM cashflow ORDER BY id DESC LIMIT %s", (limit,))
            return await cur.fetchall()

# ---------- OYLIK HISOBOT ----------

async def monthly_report(year_month: str):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """SELECT COUNT(*) as buyurtmalar_soni,
                          COALESCE(SUM(e.metr), 0) as jami_metr,
                          COALESCE(SUM(e.logotip_soni), 0) as jami_logotip,
                          COALESCE(SUM(e.transport_km), 0) as jami_km,
                          COALESCE(SUM(e.summa), 0) as jami_xarajat
                   FROM execution e
                   JOIN orders o ON o.id = e.order_id
                   WHERE e.tasdiqlangan = 1 AND to_char(e.created_at, 'YYYY-MM') = %s""",
                (year_month,),
            )
            exec_summary = await cur.fetchone()

            await cur.execute(
                """SELECT turi, COALESCE(SUM(summa), 0) as jami
                   FROM cashflow
                   WHERE to_char(created_at, 'YYYY-MM') = %s
                   GROUP BY turi""",
                (year_month,),
            )
            rows2 = await cur.fetchall()
            cash_summary = {r["turi"]: r["jami"] for r in rows2}

            return exec_summary, cash_summary

# ---------- ADMIN QARZI ----------

async def add_admin_debt(summa: float, izoh: str = ""):
    """Admin qarzini qo'shish (masalan tashqi to'lov majburiyati)."""
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO admin_debts (summa, izoh) VALUES (%s, %s)",
                (summa, izoh),
            )
        await conn.commit()

async def get_admin_total_debt() -> float:
    """To'lanmagan admin qarzlari jamini qaytaradi."""
    async with await psycopg.AsyncConnection.connect(DATABASE_URL, row_factory=dict_row) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT COALESCE(SUM(summa), 0) FROM admin_debts WHERE tolangan = 0"
            )
            row = await cur.fetchone()
            return list(row.values())[0] if row else 0.0

async def mark_admin_debts_paid():
    """Barcha to'lanmagan admin qarzlarini to'langan deb belgilaydi."""
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE admin_debts SET tolangan = 1 WHERE tolangan = 0"
            )
        await conn.commit()
