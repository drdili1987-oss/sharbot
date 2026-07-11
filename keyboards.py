from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def admin_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆕 Yangi zakaz")],
            [KeyboardButton(text="📋 Buyurtmalar"), KeyboardButton(text="➕ Sharchi qo'shish")],
            [KeyboardButton(text="💰 Hisobot"), KeyboardButton(text="💸 To'lov")],
        ],
        resize_keyboard=True,
    )


def worker_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Mening buyurtmalarim"), KeyboardButton(text="📊 Hisob-kitob")]
        ],
        resize_keyboard=True,
    )


def workers_inline_kb(workers, prefix="tanla"):
    buttons = [
        [InlineKeyboardButton(text=w["ism"], callback_data=f"{prefix}_{w['id']}")]
        for w in workers
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def qabul_rad_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Qabul qilish", callback_data=f"qabul_{order_id}"),
                InlineKeyboardButton(text="❌ Rad etish", callback_data=f"rad_{order_id}"),
            ]
        ]
    )


def worker_orders_kb(orders):
    buttons = [
        [
            InlineKeyboardButton(
                text=f"#{o['id']} | {o['magazin_kodi']} | {o['sana']}",
                callback_data=f"buyurtma_{o['id']}",
            )
        ]
        for o in orders
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def bajarildi_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Bajarildi", callback_data=f"bajarildi_{order_id}")]
        ]
    )


def ha_yoq_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Ha, uzoq", callback_data="uzoq_ha"),
                InlineKeyboardButton(text="Yo'q, yaqin", callback_data="uzoq_yoq"),
            ]
        ]
    )


def tasdiqlash_kb(execution_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"tasdiqlash_{execution_id}")]
        ]
    )


def hisobot_menu_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Umumiy qarzlar", callback_data="qarzlar")],
            [InlineKeyboardButton(text="📅 Oylik hisobot", callback_data="oylik")],
        ]
    )


# kirim_chiqim_menu_kb removed


def worker_debt_paid_kb(worker_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ To'landi deb belgilash", callback_data=f"tolov_{worker_id}")]
        ]
    )


def logotip_colors_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔴 Qizil", callback_data="logo_color_qizil"),
                InlineKeyboardButton(text="⚪ Oq", callback_data="logo_color_oq"),
            ],
            [
                InlineKeyboardButton(text="🟠 Orange", callback_data="logo_color_orange"),
                InlineKeyboardButton(text="🟡 Sariq", callback_data="logo_color_sariq"),
            ],
            [
                InlineKeyboardButton(text="➡️ Keyingi", callback_data="logo_color_done"),
            ]
        ]
    )


def worker_confirm_payment_kb(worker_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"wconfirm_pay_{worker_id}"),
                InlineKeyboardButton(text="❌ Yo'q", callback_data=f"wreject_pay_{worker_id}"),
            ]
        ]
    )


def worker_confirm_tolov_kb(worker_id: int, summa: float):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"wc_tl_{worker_id}_{int(summa)}"),
                InlineKeyboardButton(text="❌ Yo'q", callback_data=f"wr_tl_{worker_id}"),
            ]
        ]
    )


def cancel_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bosh menyu")]],
        resize_keyboard=True,
    )


def xodim_upload_kb(order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📷 Rasmlarni yuklash", callback_data=f"xodim_upload_{order_id}"),
            ]
        ]
    )
