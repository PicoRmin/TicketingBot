# راهنمای استفاده از Framer Motion

این پروژه برای انیمیشن‌های تعاملی، ترنزیشن صفحات و micro-interaction ها از **Framer Motion** استفاده می‌کند. این سند خلاصه‌ای از ساختار، الگوها و نمونه‌کدهای پیاده‌سازی شده را ارائه می‌دهد.

## 📦 نصب

در پوشه `web_admin` کافی است یک‌بار دستور استاندارد را اجرا کنید تا پکیج نصب شود:

```bash
npm install
```

اگر قصد اضافه‌کردن امکانات جدید دارید:

```bash
npm install framer-motion
```

## 🧱 ساختار ماژول‌ها

| مسیر | توضیح |
| --- | --- |
| `src/lib/motion.ts` | شامل تمامی variants اشتراکی، انیمیشن‌های میکرو و helper ها |
| `src/hooks/useMotionPreferences.ts` | تشخیص `prefers-reduced-motion` برای غیرفعال‌سازی پویا |
| `src/components/PageTransition.tsx` | Wrapper رسمی برای انیمیشن مسیرها با `AnimatePresence` |
| `src/components/NotificationBell.tsx` | نمونه پیاده‌سازی micro-interaction برای دکمه و لیست اعلان‌ها |

## 🚀 شروع سریع

### 1. ترنزیشن صفحه

```tsx
import { PageTransition } from "./components/PageTransition";

export function Layout() {
  return (
    <main>
      <PageTransition />
    </main>
  );
}
```

تمام صفحات داخل `<Outlet />` به صورت خودکار با الگوی `pageTransitionVariants` انیمیت می‌شوند.

### 2. استفاده از variants آماده

```tsx
import { motion } from "framer-motion";
import { microButtonVariants } from "../lib/motion";

export function ActionButton(props) {
  return (
    <motion.button
      variants={microButtonVariants}
      initial="rest"
      whileHover="hover"
      whileTap="tap"
      {...props}
    />
  );
}
```

### 3. احترام به prefers-reduced-motion

```tsx
import { useMotionPreferences } from "../hooks/useMotionPreferences";
import { headerRevealVariants, reducedMotionVariants } from "../lib/motion";

const { shouldReduceMotion } = useMotionPreferences();
const variants = shouldReduceMotion ? reducedMotionVariants : headerRevealVariants;
```

## ✨ الگوهای آماده

- `pageTransitionVariants`: مخصوص ورود/خروج صفحات با Blur و حرکت عمودی.
- `headerRevealVariants`: نمایش نرم هدرها.
- `microButtonVariants`: مقیاس‌دهی فنری برای hover/tap دکمه‌ها.
- `dropdownVariants`: باز و بسته شدن منوها با fade+scale.
- `listItemVariants(index)`: ایجاد stagger برای لیست‌ها بر اساس index.

## 🧪 چک‌لیست سازگاری

1. از `useMotionPreferences` در سطح Layout استفاده کنید تا در دستگاه‌های ضعیف بتوان motion را کاهش داد.
2. برای Route transitions همیشه `key` را برابر `location.pathname` قرار دهید.
3. از `AnimatePresence` با `mode="wait"` جهت جلوگیری از overlap استفاده کنید.
4. قبل از انتشار، صفحات اصلی (Dashboard, Tickets, User Portal) را در دو زبان تست کنید تا تغییری در layout ایجاد نشود.

## ✅ بهترین‌عمل‌ها

- برای عناصر محدود (badge، icon) از micro variants استفاده کنید تا هزینه render پایین بماند.
- انیمیشن‌های پیچیده‌تر (timeline ها) را در فایل مجزا تعریف کنید تا قابل reuse باشند.
- همیشه رشته‌های متنی مرتبط با انیمیشن (مانند عنوان منو) را در i18n ثبت کنید.
- هنگام اضافه‌کردن انیمیشن جدید، سند حاضر را با توضیح و مثال به‌روزرسانی کنید.

