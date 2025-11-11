# راهنمای دریافت توکن ربات تلگرام / Telegram Bot Token Guide

## مراحل دریافت توکن ربات تلگرام

### مرحله ۱: ایجاد ربات جدید

1. **باز کردن تلگرام** و جستجوی `@BotFather`
2. **شروع گفتگو** با BotFather
3. ارسال دستور `/newbot` یا `/start`
4. **انتخاب نام** برای ربات (مثلاً: `Iranmehr Ticketing Bot`)
5. **انتخاب Username** برای ربات (باید به `bot` ختم شود، مثلاً: `iranmehr_ticketing_bot`)

### مرحله ۲: دریافت توکن

پس از ایجاد ربات، BotFather یک **توکن** به شما می‌دهد که شبیه این است:
```
1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
```

⚠️ **مهم**: این توکن را در جای امن نگه دارید و هرگز آن را در کد یا Git commit نکنید!

### مرحله ۳: تنظیم توکن در پروژه

1. فایل `.env` را باز کنید (یا از `env.example` کپی کنید)
2. مقدار `TELEGRAM_BOT_TOKEN` را با توکن دریافت شده جایگزین کنید:

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-1234567890
```

### دستورات مفید BotFather

- `/mybots` - مدیریت ربات‌های شما
- `/setdescription` - تنظیم توضیحات ربات
- `/setabouttext` - تنظیم متن درباره ربات
- `/setcommands` - تنظیم دستورات ربات
- `/setuserpic` - تنظیم تصویر ربات

### نکات امنیتی

1. ✅ توکن را فقط در فایل `.env` نگه دارید
2. ✅ فایل `.env` را به Git اضافه نکنید (در `.gitignore` است)
3. ✅ توکن را با کسی به اشتراک نگذارید
4. ✅ اگر توکن لو رفت، از BotFather با `/revoke` توکن جدید بگیرید

### تست ربات

پس از تنظیم توکن، می‌توانید ربات را در تلگرام پیدا کنید و با ارسال `/start` تست کنید.

---

**لینک‌های مفید:**
- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [BotFather در تلگرام](https://t.me/BotFather)

