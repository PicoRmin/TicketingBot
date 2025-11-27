# راهنمای استفاده از TailwindCSS

این پروژه از **TailwindCSS** همراه با **CSS Variables** برای مدیریت تم استفاده می‌کند.

## 🎨 ساختار Styling

### CSS Variables + TailwindCSS

ما از یک رویکرد ترکیبی استفاده می‌کنیم:

1. **CSS Variables** برای رنگ‌ها و تم (Light/Dark Mode)
2. **TailwindCSS** برای utility classes و responsive design

### تم روشن و تاریک

تم‌ها از طریق CSS Variables مدیریت می‌شوند:

```css
:root {
  --bg: #ffffff;
  --primary: #2563eb;
  /* ... */
}

.dark {
  --bg: #0f172a;
  --primary: #3b82f6;
  /* ... */
}
```

TailwindCSS از این متغیرها استفاده می‌کند:

```jsx
<div className="bg-bg text-fg">
  {/* استفاده از CSS Variables از طریق Tailwind */}
</div>
```

## 📝 استفاده از TailwindCSS

### رنگ‌ها

از کلاس‌های Tailwind با نام‌های CSS Variables استفاده کنید:

```jsx
// Background
<div className="bg-bg">...</div>
<div className="bg-bg-secondary">...</div>

// Text
<p className="text-fg">...</p>
<p className="text-fg-secondary">...</p>

// Colors
<button className="bg-primary text-white">...</button>
<span className="text-success">...</span>
<span className="text-warning">...</span>
<span className="text-error">...</span>
```

### Responsive Design

```jsx
<div className="
  w-full
  md:w-1/2
  lg:w-1/3
  xl:w-1/4
">
  Responsive container
</div>
```

### Dark Mode

Dark mode به صورت خودکار از طریق کلاس `.dark` کار می‌کند:

```jsx
<div className="bg-bg text-fg dark:bg-bg-secondary">
  {/* رنگ‌ها به صورت خودکار تغییر می‌کنند */}
</div>
```

## 🔤 فونت‌های فارسی

### فونت اصلی: Vazirmatn

فونت فارسی **Vazirmatn** به صورت خودکار در تمام پروژه استفاده می‌شود:

```jsx
// به صورت پیش‌فرض استفاده می‌شود
<p>متن فارسی</p>

// یا به صورت صریح
<p className="font-sans">متن فارسی</p>
```

### فونت Mono: Vazir Code

برای کد و متن‌های monospace:

```jsx
<code className="font-mono">کد فارسی</code>
```

## 🎯 Best Practices

### 1. استفاده از CSS Variables برای رنگ‌ها

✅ **خوب:**
```jsx
<div className="bg-bg text-fg border border-border">
```

❌ **بد:**
```jsx
<div className="bg-white text-gray-900 border-gray-300">
```

### 2. ترکیب TailwindCSS با Custom CSS

✅ **خوب:**
```jsx
<div className="card p-4">
  {/* card یک کلاس custom است */}
</div>
```

```css
.card {
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
}
```

### 3. Responsive Design

✅ **خوب:**
```jsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
```

### 4. Dark Mode

✅ **خوب:**
```jsx
<div className="bg-bg text-fg">
  {/* به صورت خودکار در dark mode تغییر می‌کند */}
</div>
```

## 📦 Utility Classes سفارشی

می‌توانید utility classes سفارشی در `styles.css` اضافه کنید:

```css
@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}
```

## 🔧 پیکربندی

پیکربندی TailwindCSS در `tailwind.config.js`:

- **Colors**: از CSS Variables استفاده می‌کند
- **Fonts**: Vazirmatn برای فارسی
- **Dark Mode**: class-based
- **Spacing**: با spacing scale سفارشی

## 📚 منابع

- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [Vazirmatn Font](https://fonts.google.com/specimen/Vazirmatn)
- [Vazir Code Font](https://github.com/rastikerdar/vazir-code-font)

