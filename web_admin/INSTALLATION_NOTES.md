# یادداشت‌های نصب

## ⚠️ نکات مهم

### بعد از تغییر package.json

اگر `package.json` را تغییر داده‌اید، حتماً:

```bash
npm install
```

را اجرا کنید تا dependencies جدید نصب شوند.

### خطاهای TypeScript

اگر بعد از تغییر `package.json` خطای TypeScript در مورد modules جدید دیدید (مثل `@tanstack/react-query`)، این طبیعی است و بعد از اجرای `npm install` برطرف می‌شود.

### React Query

React Query به صورت خودکار در `main.tsx` راه‌اندازی شده است. بعد از نصب dependencies، QueryProvider فعال می‌شود.

### DevTools

React Query DevTools فقط در development mode نمایش داده می‌شود. برای مشاهده آن:

1. پروژه را در development mode اجرا کنید (`npm run dev`)
2. در گوشه پایین راست صفحه، دکمه React Query را ببینید
3. کلیک کنید تا DevTools باز شود

