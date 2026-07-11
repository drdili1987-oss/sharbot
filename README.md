# Shar Arka / Shar Logotip Zakaz Boti

Bu bot orqali siz (admin) mijozlardan kelgan zakazlarni sharchilarga (ijrochi xodimlarga)
yuborasiz, ular bajarilgach hisobotini olasiz, tasdiqlaysiz va har bir sharchiga qancha
qarzdorligingiz avtomatik hisoblab boriladi. Shuningdek umumiy kirim-chiqim va oylik
hisobot ham yuritiladi.

## 1. O'rnatish

```bash
cd sharbot
pip install -r requirements.txt
```

(Python 3.10+ talab qilinadi)

## 2. Bot tokenini olish

1. Telegram'da **@BotFather** ga yozing
2. `/newbot` buyrug'ini yuboring, nom bering
3. U sizga token beradi, masalan: `7123456789:AAExampleTokenHere`

## 3. O'zingizning Telegram ID raqamingizni bilish

**@userinfobot** ga `/start` yozing — u sizga ID raqamingizni ko'rsatadi (masalan `123456789`).
Aynan shu ID — **admin** ID hisoblanadi.

## 4. Sozlash

`config.py` faylini oching va quyidagilarni to'ldiring:

```python
BOT_TOKEN = "7123456789:AAExampleTokenHere"
ADMIN_ID = 123456789
```

Yoki muhit o'zgaruvchilari orqali (server uchun tavsiya etiladi):

```bash
export BOT_TOKEN="7123456789:AAExampleTokenHere"
export ADMIN_ID="123456789"
```

Narxlarni ham shu faylda o'zgartirishingiz mumkin:
- `ARKA_NARXI_METR = 120_000` — 1 metr arka narxi
- `LOGOTIP_NARXI_DONA = 12_000` — 1 dona logotip shar narxi
- `TRANSPORT_NARXI_KM = 2_000` — 1 km transport narxi

## 5. Ishga tushirish

```bash
python3 main.py
```

Bot ishga tushgach, o'zingiz botga `/start` yozing — admin menyusi chiqadi.

## 6. Ishlatish tartibi

### Sharchi qo'shish
`➕ Sharchi qo'shish` tugmasini bosing → sharchining Telegram ID raqamini kiriting →
ismini kiriting. Sharchi keyin botga o'zi `/start` bossa, o'z panelini ko'radi.

**Muhim:** sharchi botga avval `/start` bosgan bo'lishi shart emas — siz uni ID orqali
qo'shishingiz mumkin, lekin xabar yuborish uchun u avvalroq botni topib, hech bo'lmasa
bironta xabar yozgan/`/start` bosgan bo'lishi kerak (Telegram qoidasi: bot foydalanuvchiga
faqat u botni bir marta ishga tushirgandan keyin yoza oladi).

### Yangi zakaz
`🆕 Yangi zakaz` → magazin kodi → sana → lokatsiya havolasi → qizil soni → oq soni →
qaysi sharchiga yuborishni tanlaysiz. Sharchiga xabar avtomatik ketadi, u
**Qabul qilish / Rad etish** tugmalari orqali javob beradi.

### Sharchi tomonidan bajarish
Sharchi `📋 Mening buyurtmalarim` orqali qabul qilingan buyurtmalarini ko'radi,
kerakli buyurtmani bosadi, so'ng **✅ Bajarildi** tugmasini bosadi. Bot ketma-ket so'raydi:
- Necha metr arka qilindi
- Nechta logotip shar berildi
- Do'kon uzoqmi (Ha/Yo'q) — Ha bo'lsa, necha km

Shundan so'ng hisoblangan summa bilan sizga (adminga) xabar keladi.

### Tasdiqlash
Siz kelgan xabarni ko'rib, **✅ Tasdiqlash** tugmasini bosasiz. Shu zahoti hisoblangan
summa o'sha sharchiga sizning **qarzingiz** sifatida hisobotga yoziladi.

### Hisobot
`💰 Hisobot` →
- **📊 Umumiy qarzlar** — har bir sharchiga qancha qarzdor ekanligingiz, va
  **✅ To'landi deb belgilash** tugmasi (pul to'lab bo'lgach bosasiz — qarz nolga tushadi)
- **📅 Oylik hisobot** — `YYYY-MM` formatida oy kiritasiz (masalan `2026-07`), bot sizga
  o'sha oy uchun: nechta buyurtma bajarilgani, jami metr, jami logotip, jami km,
  sharchilarga jami xarajat, jami kirim/chiqim va sof natijani chiqarib beradi

### Kirim/Chiqim
`💵 Kirim/Chiqim` → kirim yoki chiqim qo'shasiz (summa + izoh), yoki oxirgi
yozuvlar ro'yxatini ko'rasiz. Bu bo'lim zakazlardan mustaqil — masalan shar xarid qilish,
boshqa xarajatlar yoki mijozdan naqd tushum kabi holatlar uchun.

## 7. Botni doimiy ishlab turishi uchun

Kompyuteringiz o'chsa bot ham to'xtaydi. Doimiy ishlashi uchun uni arzon VPS
(masalan Timeweb, Beget, DigitalOcean) ga joylashtirib, `systemd` yoki `screen`/`tmux`
yordamida orqa fonda ishlatish tavsiya etiladi. Xohlasangiz, buni ham sozlab beraman.

## 8. Ma'lumotlar bazasi

Barcha ma'lumotlar `sharbot.db` (SQLite) faylida saqlanadi — u avtomatik yaratiladi.
Bu faylni muntazam zaxira (backup) qilib turishni tavsiya qilaman.
