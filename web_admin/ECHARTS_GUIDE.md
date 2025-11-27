# راهنمای استفاده از ECharts

این پروژه برای داشبوردهای تحلیلی و نمودارهای SLA از **Apache ECharts 5** به همراه wrapper رسمی React استفاده می‌کند. ساختار جدید جایگزین کامل Recharts شده و ویژگی‌هایی مانند تم پویا، انیمیشن نرم، بهینه‌سازی عملکرد و انعطاف‌پذیری بالا را امکان‌پذیر کرده است.

## 📦 نصب و پیش‌نیاز

در `package.json` کتابخانه‌های زیر نصب شده‌اند:

- `echarts`
- `echarts-for-react`

اگر نیاز به بروزرسانی یا نصب مجدد بود:

```bash
cd web_admin
npm install echarts echarts-for-react
```

## 🧱 ساختار ماژول‌ها

| مسیر | توضیح |
| --- | --- |
| `src/hooks/useChartTheme.ts` | استخراج خودکار رنگ‌ها از CSS Variables و واکنش به تغییر تم |
| `src/lib/echartsConfig.ts` | Builder های Grid، Tooltip، Legend، محور‌ها، گرادیان، Toolbox و DataZoom |
| `src/components/charts/EChart.tsx` | Wrapper مشترک با ثبت ماژول‌های مورد نیاز ECharts و loader داخلی |
| `src/pages/Dashboard.tsx` | استفاده از ECharts برای تمامی نمودارهای داشبورد مدیریت |
| `src/pages/SLAManagement.tsx` | استفاده از ECharts در نمودارهای SLA |

## 🚀 نحوه استفاده سریع

```tsx
import { useMemo } from "react";
import type { EChartsOption } from "echarts";
import { EChart } from "../components/charts/EChart";
import { useChartTheme } from "../hooks/useChartTheme";
import { buildGrid, buildTooltip, buildCategoryAxis, buildValueAxis } from "../lib/echartsConfig";

export function ExampleChart({ data }) {
  const chartTheme = useChartTheme();

  const option = useMemo<EChartsOption>(() => ({
    grid: buildGrid(),
    tooltip: buildTooltip(chartTheme),
    xAxis: buildCategoryAxis(data.map((d) => d.label), chartTheme),
    yAxis: buildValueAxis(chartTheme),
    series: [
      {
        type: "bar",
        data: data.map((d) => d.value),
      },
    ],
  }), [data, chartTheme]);

  return <EChart option={option} height={320} ariaLabel="نمودار نمونه" />;
}
```

## ✨ امکانات کلیدی

- **تم پویا:** هوک `useChartTheme` به محض تغییر حالت تاریک/روشن یا تغییر CSS Variables رنگ‌ها را بروزرسانی می‌کند.
- **حالت‌های Count/Percent:** با state `chartMode` می‌توان بین نمایش تعدادی و درصدی سویچ کرد؛ محور و tooltipها به صورت خودکار تنظیم می‌شوند.
- **کنترل‌های حرفه‌ای:** `buildToolbox` امکان ذخیره تصویر، DataView و Restore را فعال می‌کند و `buildHorizontalZoom` روی نمودارهای زمانی Data Zoom داخلی و اسلایدری اضافه می‌کند.
- **ماژولار بودن:** تمامی نمودارها از Wrapper مشترک `EChart` استفاده می‌کنند تا فقط اجزای لازم ECharts بارگذاری شود.
- **گرادیان‌های هماهنگ:** تابع `buildLinearGradient` از رنگ‌های سیستمی استفاده کرده و تضاد بصری را حفظ می‌کند.
- **دسترسی و i18n:** برای aria-label ها و پیام‌های بدون داده از `t("dashboard.noData")` استفاده شده است.
- **کارایی:** `echarts-for-react` به صورت lazyUpdate و بدون merge پیکربندی شده تا از رندر اضافی جلوگیری شود.

## 🎛️ حالت نمایش Count / Percent

```tsx
const [chartMode, setChartMode] = useState<"count" | "percent">("count");
const isPercentMode = chartMode === "percent";
const formatValue = useCallback(
  (value: number, total: number) =>
    !isPercentMode || !total ? value : Number(((value / total) * 100).toFixed(2)),
  [isPercentMode]
);
```

برای tooltip ها مقدار خام (`raw`) و مقدار نمایش داده‌شده (`value`) را توأمان نگه دارید تا امکان نمایش همزمان درصد و تعداد وجود داشته باشد.

## 🧪 چک‌لیست توسعه نمودار جدید

1. داده‌ها را پیش از ساخت گزینه‌ها نرمال کنید (مثلاً با `useMemo`).
2. از helper های `buildGrid`, `buildTooltip`, `buildCategoryAxis`, `buildValueAxis`, `buildToolbox` برای استایل یکپارچه استفاده کنید.
3. برای نمودارهای زمانی یا حجیم، `dataZoom: buildHorizontalZoom()` را اضافه کنید تا کاربر بتواند بازه دلخواه را انتخاب کند.
4. رنگ‌ها و متن‌ها را از `useChartTheme` و i18n دریافت کنید.
5. ارتفاع نمودار را متناسب با کارت والد تعیین کنید (`<EChart height={300} />`).
6. در صورت امکان، داده‌های خالی را مدیریت کرده و پیام `dashboard.noData` را نمایش دهید.

## 📘 منابع مفید

- [مستندات رسمی ECharts](https://echarts.apache.org/en/option.html)
- [React ECharts Wrapper](https://github.com/hustcc/echarts-for-react)
- نمونه‌های جاری در فایل‌های `Dashboard.tsx` و `SLAManagement.tsx`

