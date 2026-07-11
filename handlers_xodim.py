import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import database as db
import keyboards as kb
from states import XodimPhotoForm
from config import XODIM_ID, ADMIN_ID

router = Router()
logger = logging.getLogger("handlers_xodim")

@router.message(CommandStart(), F.from_user.id == XODIM_ID)
async def xodim_start(message: Message):
    await message.answer(
        "Assalomu alaykum, Xodim! Boshqaruv botiga xush kelibsiz.\n"
        "Sizga yangi buyurtmalar va buyurtmalarning bajarilishi haqidagi xabarlar yuboriladi.",
        reply_markup=ReplyKeyboardRemove()
    )

@router.callback_query(F.data.startswith("xodim_upload_"), F.from_user.id == XODIM_ID)
async def xodim_upload_start(call: CallbackQuery, state: FSMContext):
    order_id = int(call.data.split("_")[2])
    await state.update_data(order_id=order_id)
    await call.message.answer(
        "1. Qilingan arkaning rasmini yuboring (photo yuboring):",
        reply_markup=kb.cancel_kb()
    )
    await state.set_state(XodimPhotoForm.arka_photo)
    await call.answer()

@router.message(XodimPhotoForm.arka_photo, F.from_user.id == XODIM_ID)
async def xodim_arka_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Iltimos, rasm yuboring (photo):", reply_markup=kb.cancel_kb())
        return
    
    file_id = message.photo[-1].file_id
    await state.update_data(arka_photo_id=file_id)
    await message.answer(
        "2. Endi logotipli sharlar rasmini yuboring (photo yuboring):",
        reply_markup=kb.cancel_kb()
    )
    await state.set_state(XodimPhotoForm.logo_photo)

@router.message(XodimPhotoForm.logo_photo, F.from_user.id == XODIM_ID)
async def xodim_logo_photo(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("Iltimos, rasm yuboring (photo):", reply_markup=kb.cancel_kb())
        return
    
    logo_file_id = message.photo[-1].file_id
    data = await state.get_data()
    arka_file_id = data.get("arka_photo_id")
    order_id = data.get("order_id")
    
    order = await db.get_order(order_id)
    worker = await db.get_worker_by_id(order["worker_id"]) if order else None
    wname = worker["ism"] if worker else "Sharchi"
    magazin = order["magazin_kodi"] if order else "?"
    
    # Notify Admin
    try:
        await message.bot.send_photo(
            ADMIN_ID,
            photo=arka_file_id,
            caption=f"📷 Xodim dan hisobot rasmi (Arka)\n🏪 Magazin: {magazin}\n👤 Sharchi: {wname}"
        )
        await message.bot.send_photo(
            ADMIN_ID,
            photo=logo_file_id,
            caption=f"📷 Xodim dan hisobot rasmi (Logo sharlar)\n🏪 Magazin: {magazin}\n👤 Sharchi: {wname}"
        )
    except Exception as e:
        logger.error(f"Failed to forward photos to Admin: {e}")
        
    # Notify Worker
    if worker:
        try:
            await message.bot.send_photo(
                worker["tg_id"],
                photo=arka_file_id,
                caption=f"📷 Xodim dan buyurtma bezak rasmi (Arka)\n🏪 Magazin: {magazin}"
            )
            await message.bot.send_photo(
                worker["tg_id"],
                photo=logo_file_id,
                caption=f"📷 Xodim dan buyurtma bezak rasmi (Logo sharlar)\n🏪 Magazin: {magazin}"
            )
        except Exception as e:
            logger.error(f"Failed to forward photos to Worker: {e}")
            
    await message.answer(
        "✅ Rahmat! Rasmlar adminga va sharchiga yuborildi.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()
