# راهنمای راه‌اندازی پروژه Frontend

این فایل راهنمای کامل برای راه‌اندازی و توسعه پروژه Frontend است.

## 📋 پیش‌نیازها

- Node.js >= 18.0.0
- npm >= 9.0.0 (یا yarn/pnpm)

## 🚀 نصب و راه‌اندازی

### 1. نصب Dependencies

```bash
npm install
```

**نکته مهم:** بعد از نصب، تمام dependencies از جمله React Query نصب می‌شوند. اگر خطای TypeScript در مورد `@tanstack/react-query` دیدید، مطمئن شوید که `npm install` را اجرا کرده‌اید.

### 2. تنظیمات محیطی

فایل‌های `.env` را از `.env.example` کپی کنید:

```bash
# برای Development
cp .env.example .env.development

# برای Production
cp .env.example .env.production
```

سپس مقادیر را بر اساس محیط خود تنظیم کنید.

### 3. راه‌اندازی Husky (Git Hooks)

```bash
npm run prepare
```

این دستور Husky را نصب و پیکربندی می‌کند.

## 🛠️ دستورات موجود

### Development

```bash
# اجرای سرور توسعه
npm run dev

# بررسی TypeScript
npm run type-check

# اجرای Linter
npm run lint

# رفع خودکار خطاهای Linter
npm run lint:fix

# فرمت کردن کد با Prettier
npm run format

# بررسی فرمت کد
npm run format:check
```

### Build

```bash
# ساخت پروژه برای Production
npm run build

# پیش‌نمایش Build
npm run preview
```

## 📝 ESLint و Prettier

### ESLint

پیکربندی ESLint در `.eslintrc.cjs` قرار دارد. این پیکربندی شامل:

- TypeScript support
- React hooks rules
- React best practices
- Unused variables warnings

### Prettier

پیکربندی Prettier در `.prettierrc.json` قرار دارد. تنظیمات:

- 2 spaces indentation
- Single quotes: false
- Semicolons: true
- Print width: 100 characters

### Git Hooks

با استفاده از Husky، Git hooks زیر فعال شده‌اند:

- **pre-commit**: اجرای lint-staged برای فایل‌های staged
- **pre-push**: اجرای type-check و lint قبل از push

## 🔧 تنظیمات Vite

پیکربندی Vite در `vite.config.ts` شامل:

- Path aliases (`@/` برای `src/`)
- Code splitting برای vendor, charts, i18n
- Source maps برای production
- Port 5173 برای development

## 📁 ساختار پروژه

```
web_admin/
├── src/
│   ├── components/     # کامپوننت‌های قابل استفاده مجدد
│   ├── pages/          # صفحات اصلی
│   ├── hooks/          # Custom React Hooks
│   ├── services/       # API services
│   ├── routes/         # Route components
│   ├── locales/        # فایل‌های i18n
│   └── styles.css      # استایل‌های اصلی
├── public/             # فایل‌های استاتیک
├── .eslintrc.cjs      # پیکربندی ESLint
├── .prettierrc.json   # پیکربندی Prettier
├── .lintstagedrc.json  # پیکربندی lint-staged
├── tsconfig.json       # پیکربندی TypeScript
└── vite.config.ts      # پیکربندی Vite
```

## 🎯 Best Practices

### 1. Code Style

- همیشه قبل از commit، `npm run format` را اجرا کنید
- از `npm run lint:fix` برای رفع خودکار خطاها استفاده کنید
- TypeScript strict mode فعال است - از `any` استفاده نکنید

### 2. Git Workflow

- Git hooks به صورت خودکار lint و format را اجرا می‌کنند
- اگر hook خطا داد، ابتدا خطاها را رفع کنید سپس commit کنید

### 3. Environment Variables

- هرگز فایل‌های `.env` را commit نکنید
- از `.env.example` به عنوان template استفاده کنید
- متغیرهای محیطی باید با `VITE_` شروع شوند

## 🐛 Troubleshooting

### خطای ESLint

```bash
# رفع خودکار خطاها
npm run lint:fix
```

### خطای TypeScript

```bash
# بررسی نوع‌ها
npm run type-check
```

### مشکل با Husky

```bash
# نصب مجدد Husky
npm run prepare
```

## 📚 منابع بیشتر

- [Vite Documentation](https://vitejs.dev/)
- [ESLint Documentation](https://eslint.org/)
- [Prettier Documentation](https://prettier.io/)
- [TypeScript Documentation](https://www.typescriptlang.org/)

