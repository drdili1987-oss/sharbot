from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
import keyboards as kb
from states import YangiZakaz, AddSharchiForm, TolovForm, OylikHisobotForm, AdminQarzForm
from config import ADMIN_ID, ARKA_NARXI_METR, LOGOTIP_NARXI_DONA, TRANSPORT_NARXI_KM

router = Router()


def is_admin(message_or_call) -> bool:
    return message_or_call.from_user.id == ADMIN_ID


# ---------------- BEKOR QILISH / BOSH MENYU ----------------

@router.message(F.text.in_({"❌ Bosh menyu", "Bosh menyu"}), F.from_user.id == ADMIN_ID)
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Bosh menyuga qaytildi.",
        reply_markup=kb.admin_menu_kb(),
    )


# ---------------- START ----------------

@router.message(CommandStart(), F.from_user.id == ADMIN_ID)
async def cmd_start_admin(message: Message):
    await message.answer(
        "Assalomu alaykum, Admin!\nQuyidagi menyudan foydalaning:",
        reply_markup=kb.admin_menu_kb(),
    )


# ---------------- SHARCHI QO'SHISH ----------------

@router.message(F.text == "➕ Sharchi qo'shish", F.from_user.id == ADMIN_ID)
async def add_sharchi_start(message: Message, state: FSMContext):
    await message.answer(
        "Sharchining Telegram ID raqamini yuboring (masalan @userinfobot orqali bilib oling):",
        reply_markup=kb.cancel_kb()
    )
    await state.set_state(AddSharchiForm.tg_id)


@router.message(AddSharchiForm.tg_id, F.from_user.id == ADMIN_ID)
async def add_sharchi_tgid(message: Message, state: FSMContext):
    if not message.text.strip().isdigit():
        await message.answer("Iltimos, faqat raqam yuboring.")
        return
    await state.update_data(tg_id=int(message.text.strip()))
    await message.answer("Endi sharchining ismini yozing:", reply_markup=kb.cancel_kb())
    await state.set_state(AddSharchiForm.ism)


@router.message(AddSharchiForm.ism, F.from_user.id == ADMIN_ID)
async def add_sharchi_ism(message: Message, state: FSMContext):
    data = await state.get_data()
    await db.add_worker(data["tg_id"], message.text.strip())
    await message.answer(
        f"✅ Sharchi qo'shildi: {message.text.strip()} (ID: {data['tg_id']})\n"
        f"Sharchi botga /start yozib, o'z panelini ochishi mumkin.",
        reply_markup=kb.admin_menu_kb(),
    )
    await state.clear()


# ---------------- YANGI ZAKAZ ----------------

@router.message(F.text == "🆕 Yangi zakaz", F.from_user.id == ADMIN_ID)
async def yangi_zakaz_start(message: Message, state: FSMContext):
    await message.answer("Magazin kodini kiriting:", reply_markup=kb.cancel_kb())
    await state.set_state(YangiZakaz.magazin_kodi)


@router.message(YangiZakaz.magazin_kodi, F.from_user.id == ADMIN_ID)
async def zakaz_magazin(message: Message, state: FSMContext):
    await state.update_data(magazin_kodi=message.text.strip())
    await message.answer("Sanani kiriting (masalan 15.07.2026):", reply_markup=kb.cancel_kb())
    await state.set_state(YangiZakaz.sana)


@router.message(YangiZakaz.sana, F.from_user.id == ADMIN_ID)
async def zakaz_sana(message: Message, state: FSMContext):
    await state.update_data(sana=message.text.strip())
    await message.answer("Lokatsiya (manzil) havolasini yuboring:", reply_markup=kb.cancel_kb())
    await state.set_state(YangiZakaz.manzil)


@router.message(YangiZakaz.manzil, F.from_user.id == ADMIN_ID)
async def zakaz_manzil(message: Message, state: FSMContext):
    await state.update_data(manzil=message.text.strip())
    await message.answer("Taxminiy arka o'lchamini kiriting (metrda, masalan 15 yoki 0):", reply_markup=kb.cancel_kb())
    await state.set_state(YangiZakaz.arka_metr)


@router.message(YangiZakaz.arka_metr, F.from_user.id == ADMIN_ID)
async def zakaz_arka_metr(message: Message, state: FSMContext):
    text = message.text.strip().replace(",", ".")
    try:
        arka_metr = float(text)
    except ValueError:
        await message.answer("Iltimos, faqat raqam kiriting (masalan 12.5 yoki 0):")
        return
    await state.update_data(arka_metr=arka_metr)
    # Initialize logo counts
    await state.update_data(qizil=0, oq=0, orange=0, sariq=0)
    await send_logo_menu(message, state)


async def send_logo_menu(message: Message, state: FSMContext):
    data = await state.get_data()
    qizil = data.get("qizil", 0)
    oq = data.get("oq", 0)
    orange = data.get("orange", 0)
    sariq = data.get("sariq", 0)
    
    text = (
        "Logotip sharlar sonini kiriting:\n\n"
        f"🔴 Qizil: {qizil} dona\n"
        f"⚪ Oq: {oq} dona\n"
        f"🟠 Orange: {orange} dona\n"
        f"🟡 Sariq: {sariq} dona\n\n"
        "Rang tugmasini bosib sonini kiriting, tugatgach 'Keyingi' tugmasini bosing:"
    )
    await message.answer(text, reply_markup=kb.logotip_colors_kb())
    await state.set_state(YangiZakaz.logotip_menu)


@router.callback_query(YangiZakaz.logotip_menu, F.data.startswith("logo_color_"))
async def logo_color_callback(call: CallbackQuery, state: FSMContext):
    color = call.data.split("_")[2]
    if color == "done":
        workers = await db.list_active_workers()
        if not workers:
            await call.message.answer(
                "Hozircha sharchilar ro'yxati bo'sh. Avval '➕ Sharchi qo'shish' orqali sharchi qo'shing.",
                reply_markup=kb.admin_menu_kb(),
            )
            await state.clear()
            await call.answer()
            return
        
        await call.message.answer("Zakazni qaysi sharchiga yuboramiz?", reply_markup=kb.workers_inline_kb(workers))
        await state.set_state(YangiZakaz.sharchi_tanlash)
        await call.answer()
        return
    
    await state.update_data(current_color=color)
    color_names = {"qizil": "Qizil", "oq": "Oq", "orange": "Orange", "sariq": "Sariq"}
    await call.message.answer(f"Nechta {color_names.get(color, color)} logotip shar kerak?", reply_markup=kb.cancel_kb())
    await state.set_state(YangiZakaz.logotip_soni)
    await call.answer()


@router.message(YangiZakaz.logotip_soni, F.from_user.id == ADMIN_ID)
async def logo_quantity_handler(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("Iltimos, faqat musbat butun son kiriting:")
        return
    
    data = await state.get_data()
    color = data.get("current_color")
    await state.update_data({color: int(text)})
    await send_logo_menu(message, state)


@router.callback_query(YangiZakaz.sharchi_tanlash, F.data.startswith("tanla_"))
async def zakaz_sharchi_tanlash(call: CallbackQuery, state: FSMContext):
    worker_id = int(call.data.split("_")[1])
    data = await state.get_data()

    order_id = await db.create_order(
        data["magazin_kodi"],
        data["sana"],
        data["manzil"],
        data.get("qizil", 0),
        data.get("oq", 0),
        data.get("orange", 0),
        data.get("sariq", 0),
        data.get("arka_metr", 0.0),
        worker_id
    )

    worker = await db.get_worker_by_id(worker_id)
    text = (
        f"🆕 Yangi zakaz #{order_id}\n"
        f"🏪 Magazin: {data['magazin_kodi']}\n"
        f"📅 Sana: {data['sana']}\n"
        f"📍 Manzil: {data['manzil']}\n"
        f"📐 Taxminiy arka: {data.get('arka_metr', 0)} metr\n"
        f"🔴 Qizil logotip: {data.get('qizil', 0)} dona\n"
        f"⚪ Oq logotip: {data.get('oq', 0)} dona\n"
        f"🟠 Orange logotip: {data.get('orange', 0)} dona\n"
        f"🟡 Sariq logotip: {data.get('sariq', 0)} dona"
    )
    await call.bot.send_message(worker["tg_id"], text, reply_markup=kb.qabul_rad_kb(order_id), disable_notification=False)

    # Notify xodim
    from config import XODIM_ID
    text_xodim = (
        f"🔔 **Yangi buyurtma yaratildi!**\n\n"
        f"🏪 Magazin: {data['magazin_kodi']}\n"
        f"📅 Sana: {data['sana']}\n"
        f"📍 Manzil: {data['manzil']}\n"
        f"📐 Taxminiy arka: {data.get('arka_metr', 0)} metr\n"
        f"🔴 Qizil logotip: {data.get('qizil', 0)} dona\n"
        f"⚪ Oq logotip: {data.get('oq', 0)} dona\n"
        f"🟠 Orange logotip: {data.get('orange', 0)} dona\n"
        f"🟡 Sariq logotip: {data.get('sariq', 0)} dona\n"
        f"👤 Sharchi: {worker['ism']}"
    )
    try:
        await call.bot.send_message(XODIM_ID, text_xodim, disable_notification=False)
    except Exception:
        pass

    await call.message.edit_text(f"✅ Zakaz #{order_id} {worker['ism']} ga yuborildi.")
    await state.clear()
    await call.answer()


# ---------------- BUYURTMALAR RO'YXATI (admin) ----------------

@router.message(F.text == "📋 Buyurtmalar", F.from_user.id == ADMIN_ID)
async def list_orders(message: Message):
    orders = await db.list_orders_by_status(limit=15)
    if not orders:
        await message.answer("Hozircha buyurtmalar yo'q.")
        return
    lines = []
    for o in orders:
        worker = await db.get_worker_by_id(o["worker_id"])
        wname = worker["ism"] if worker else "?"
        lines.append(
            f"#{o['id']} | {o['magazin_kodi']} | {o['sana']} | {wname} | holat: {o['status']}"
        )
    await message.answer("\n".join(lines))


# ---------------- ISHNI TASDIQLASH ----------------

@router.callback_query(F.data.startswith("tasdiqlash_"))
async def tasdiqlash_callback(call: CallbackQuery):
    if not is_admin(call):
        await call.answer("Bu tugma faqat admin uchun.", show_alert=True)
        return

    execution_id = int(call.data.split("_")[1])
    execution = await db.get_execution(execution_id)
    order = await db.get_order(execution["order_id"])

    await db.confirm_execution(execution_id)
    await db.set_order_status(order["id"], "tasdiqlangan")
    await db.create_debt(order["worker_id"], order["id"], execution["summa"])

    worker = await db.get_worker_by_id(order["worker_id"])

    await call.message.edit_text(
        call.message.text + "\n\n✅ TASDIQLANDI. Qarz hisobotga qo'shildi."
    )
    await call.bot.send_message(
        worker["tg_id"],
        f"✅ #{order['id']} zakaz bo'yicha ishingiz tasdiqlandi.\n"
        f"Sizga {execution['summa']:,.0f} so'm qarz yozildi.".replace(",", " "),
    )
    await call.answer("Tasdiqlandi")


# ---------------- ADMIN HISOB-KITOB ----------------

@router.message(F.text == "📊 Hisob-kitob", F.from_user.id == ADMIN_ID)
async def admin_hisob_kitob(message: Message):
    qarz = await db.get_admin_total_debt()
    text = (
        "📊 Sizning hisob-kitobingiz:\n\n"
        f"💸 Admin siz (Dilfuza) dan: {qarz:,.0f} so'm qarz"
    ).replace(",", " ")
    await message.answer(text, reply_markup=kb.admin_hisob_kitob_kb())


@router.callback_query(F.data == "admin_qarz_qoshish")
async def admin_qarz_qoshish_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call):
        await call.answer()
        return
    await call.message.answer("Yangi qarz summasini kiriting (so'mda):", reply_markup=kb.cancel_kb())
    await state.set_state(AdminQarzForm.summa)
    await call.answer()


@router.message(AdminQarzForm.summa, F.from_user.id == ADMIN_ID)
async def admin_qarz_summa(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "").replace(",", "")
    if not text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting.")
        return
    summa = float(text)
    await state.update_data(summa=summa)
    await message.answer("Qarz izohi (masalan: 'Ombor', 'Mahsulot xaridi'). Izohsiz bo'lsa, '-' yuboring:", reply_markup=kb.cancel_kb())
    await state.set_state(AdminQarzForm.izoh)


@router.message(AdminQarzForm.izoh, F.from_user.id == ADMIN_ID)
async def admin_qarz_izoh(message: Message, state: FSMContext):
    izoh = message.text.strip()
    data = await state.get_data()
    summa = data["summa"]
    await db.add_admin_debt(summa, izoh if izoh != "-" else "")
    qarz_jami = await db.get_admin_total_debt()
    await message.answer(
        f"✅ {summa:,.0f} so'm qarz qo'shildi.\n"
        f"💸 Jami qarz: {qarz_jami:,.0f} so'm".replace(",", " "),
        reply_markup=kb.admin_menu_kb()
    )
    await state.clear()


@router.callback_query(F.data == "admin_qarz_tozalash")
async def admin_qarz_tozalash(call: CallbackQuery):
    if not is_admin(call):
        await call.answer()
        return
    await db.mark_admin_debts_paid()
    await call.message.edit_text("✅ Barcha qarzlar to'landi deb belgilandi. Balans: 0 so'm.")
    await call.answer("Tozalandi")


# ---------------- HISOBOT ----------------

@router.message(F.text == "💰 Hisobot", F.from_user.id == ADMIN_ID)
async def hisobot_menu(message: Message):
    await message.answer("Qaysi hisobotni ko'rmoqchisiz?", reply_markup=kb.hisobot_menu_kb())


@router.callback_query(F.data == "qarzlar")
async def qarzlar_callback(call: CallbackQuery):
    if not is_admin(call):
        await call.answer()
        return
    summary = await db.get_unpaid_debts_summary()
    if not summary:
        await call.message.answer("Sharchilar ro'yxati bo'sh.")
        await call.answer()
        return
    for row in summary:
        if row["jami"] and row["jami"] > 0:
            text = f"👤 {row['ism']}: {row['jami']:,.0f} so'm qarz".replace(",", " ")
            await call.message.answer(text, reply_markup=kb.worker_debt_paid_kb(row["id"]))
    if all((not r["jami"]) or r["jami"] == 0 for r in summary):
        await call.message.answer("Hech kimga qarz yo'q. 🎉")
    await call.answer()


@router.callback_query(F.data.startswith("tolov_"))
async def tolov_callback(call: CallbackQuery):
    if not is_admin(call):
        await call.answer()
        return
    worker_id = int(call.data.split("_")[1])
    worker = await db.get_worker_by_id(worker_id)
    if not worker:
        await call.message.edit_text("Xatolik: Sharchi topilmadi.")
        await call.answer()
        return
    
    unpaid_debt = await db.get_worker_unpaid_debt(worker_id)
    if unpaid_debt <= 0:
        await call.message.edit_text(f"👤 {worker['ism']} ga to'lanishi kerak bo'lgan qarz mavjud emas.")
        await call.answer()
        return
        
    try:
        text = (
            f"⚠️ Admin siz bilan hisob-kitob qilindi (to'landi) deb belgiladi.\n"
            f"Buni tasdiqlaysizmi?\n\n"
            f"💰 Summa: {unpaid_debt:,.0f} so'm"
        ).replace(",", " ")
        await call.bot.send_message(worker["tg_id"], text, reply_markup=kb.worker_confirm_payment_kb(worker_id))
        await call.message.edit_text(f"👤 {worker['ism']} ga hisob-kitobni tasdiqlash so'rovi yuborildi. Kutilmoqda...")
    except Exception as e:
        await call.message.edit_text(
            f"❌ {worker['ism']} ga xabar yuborishda xatolik. "
            f"Ehtimol, u botni bloklagan yoki hali start bosmagan."
        )
    await call.answer()


@router.callback_query(F.data == "oylik")
async def oylik_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call):
        await call.answer()
        return
    await call.message.answer("Qaysi oy uchun? Format: YYYY-MM (masalan 2026-07)", reply_markup=kb.cancel_kb())
    await state.set_state(OylikHisobotForm.oy)
    await call.answer()


@router.message(OylikHisobotForm.oy, F.from_user.id == ADMIN_ID)
async def oylik_natija(message: Message, state: FSMContext):
    year_month = message.text.strip()
    exec_summary, cash_summary = await db.monthly_report(year_month)

    kirim = cash_summary.get("kirim", 0)
    chiqim = cash_summary.get("chiqim", 0)
    xarajat = exec_summary["jami_xarajat"] or 0

    text = (
        f"📅 {year_month} oyi uchun hisobot:\n\n"
        f"📦 Bajarilgan buyurtmalar: {exec_summary['buyurtmalar_soni']}\n"
        f"📏 Jami arka: {exec_summary['jami_metr']} metr\n"
        f"🎈 Jami logotip: {exec_summary['jami_logotip']} dona\n"
        f"🚗 Jami transport: {exec_summary['jami_km']} km\n"
        f"💸 Sharchilarga jami xarajat: {xarajat:,.0f} so'm\n\n"
        f"➕ Kirim: {kirim:,.0f} so'm\n"
        f"➖ Chiqim: {chiqim:,.0f} so'm\n"
        f"📊 Sof natija (kirim - chiqim - sharchi xarajati): {(kirim - chiqim - xarajat):,.0f} so'm"
    ).replace(",", " ")

    await message.answer(text, reply_markup=kb.admin_menu_kb())
    await state.clear()


# ---------------- TO'LOV (chiqim) ----------------

@router.message(F.text == "💸 To'lov", F.from_user.id == ADMIN_ID)
async def tolov_start(message: Message, state: FSMContext):
    workers = await db.list_active_workers()
    if not workers:
        await message.answer(
            "Hozircha sharchilar ro'yxati bo'sh. Avval '➕ Sharchi qo'shish' orqali sharchi qo'shing.",
            reply_markup=kb.admin_menu_kb(),
        )
        return
    
    await message.answer(
        "Kimga to'lov qilasiz?",
        reply_markup=kb.workers_inline_kb(workers, prefix="tolovworker")
    )
    await state.set_state(TolovForm.worker_id)


@router.callback_query(TolovForm.worker_id, F.data.startswith("tolovworker_"))
async def tolov_worker_callback(call: CallbackQuery, state: FSMContext):
    worker_id = int(call.data.split("_")[1])
    await state.update_data(worker_id=worker_id)
    worker = await db.get_worker_by_id(worker_id)
    await call.message.answer(f"{worker['ism']} ga qancha summa berasiz?", reply_markup=kb.cancel_kb())
    await state.set_state(TolovForm.summa)
    await call.answer()


@router.message(TolovForm.summa, F.from_user.id == ADMIN_ID)
async def tolov_summa(message: Message, state: FSMContext):
    text = message.text.strip().replace(" ", "")
    if not text.isdigit():
        await message.answer("Iltimos, faqat raqam kiriting.")
        return
    
    summa = float(text)
    data = await state.get_data()
    worker_id = data.get("worker_id")
    worker = await db.get_worker_by_id(worker_id)
    if not worker:
        await message.answer("Xatolik: Sharchi topilmadi.")
        await state.clear()
        return
    
    try:
        text_worker = (
            f"⚠️ Admin sizga {summa:,.0f} so'm to'lov qilmoqchi.\n"
            f"Buni tasdiqlaysizmi?"
        ).replace(",", " ")
        await message.bot.send_message(
            worker["tg_id"],
            text_worker,
            reply_markup=kb.worker_confirm_tolov_kb(worker_id, summa)
        )
        await message.answer(
            f"👤 {worker['ism']} ga {summa:,.0f} so'm to'lov tasdiqlash so'rovi yuborildi. Kutilmoqda...".replace(",", " "),
            reply_markup=kb.admin_menu_kb()
        )
    except Exception as e:
        await message.answer(
            f"❌ {worker['ism']} ga xabar yuborib bo'lmadi. Botni bloklagan bo'lishi mumkin.",
            reply_markup=kb.admin_menu_kb()
        )
    await state.clear()
