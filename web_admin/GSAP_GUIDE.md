# راهنمای استفاده از GSAP

این پروژه از **GSAP (GreenSock Animation Platform)** برای انیمیشن‌های پیشرفته استفاده می‌کند.

## 📦 نصب

GSAP و ScrollTrigger به صورت خودکار در `package.json` نصب شده‌اند:

```bash
npm install
```

## 🚀 شروع سریع

### استفاده از Custom Hooks

```tsx
import { useFadeIn, useSlideIn, useScrollAnimation } from "../hooks/useGSAP";

function MyComponent() {
  // Fade in animation
  const fadeRef = useFadeIn({ delay: 0.2 });
  
  // Slide in animation
  const slideRef = useSlideIn("left", { duration: 0.8 });
  
  // Scroll-triggered animation
  const scrollRef = useScrollAnimation(fadeIn, {
    start: "top 80%",
    once: true,
  });

  return (
    <>
      <div ref={fadeRef}>Fade in content</div>
      <div ref={slideRef}>Slide in content</div>
      <div ref={scrollRef}>Scroll-triggered content</div>
    </>
  );
}
```

### استفاده از Utility Functions

```tsx
import { fadeIn, slideIn, stagger } from "../lib/gsap";
import { useEffect, useRef } from "react";

function MyComponent() {
  const cardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (cardRef.current) {
      // Fade in
      fadeIn(cardRef.current, { duration: 0.8 });
      
      // Or slide in
      slideIn(cardRef.current, "left", { distance: 100 });
      
      // Or stagger multiple elements
      stagger(".card", fadeIn, { stagger: 0.1 });
    }
  }, []);

  return <div ref={cardRef}>Content</div>;
}
```

## 🎨 انیمیشن‌های موجود

### 1. Fade In/Out

```tsx
import { useFadeIn } from "../hooks/useGSAP";

const ref = useFadeIn({ duration: 0.8, delay: 0.2 });
```

### 2. Slide In

```tsx
import { useSlideIn } from "../hooks/useGSAP";

const ref = useSlideIn("left", { duration: 0.8, distance: 100 });
```

### 3. Scale In

```tsx
import { useScaleIn } from "../hooks/useGSAP";

const ref = useScaleIn({ from: 0.8, to: 1, duration: 0.8 });
```

### 4. Scroll-Triggered Animation

```tsx
import { useScrollAnimation } from "../hooks/useGSAP";
import { fadeIn } from "../lib/gsap";

const ref = useScrollAnimation(fadeIn, {
  start: "top 80%",
  once: true,
});
```

### 5. Parallax Effect

```tsx
import { useParallax } from "../hooks/useGSAP";

const ref = useParallax(-0.5); // Negative for reverse
```

## 📝 مثال‌های کامل

### مثال 1: Animated Card List

```tsx
import { useEffect } from "react";
import { stagger, fadeIn } from "../lib/gsap";

function CardList({ items }: { items: any[] }) {
  useEffect(() => {
    stagger(".card-item", fadeIn, { stagger: 0.1 });
  }, [items]);

  return (
    <div>
      {items.map((item, index) => (
        <div key={index} className="card-item">
          {item.title}
        </div>
      ))}
    </div>
  );
}
```

### مثال 2: Scroll-Triggered Sections

```tsx
import { useScrollAnimation } from "../hooks/useGSAP";
import { slideIn } from "../lib/gsap";

function Section({ title, children }: { title: string; children: ReactNode }) {
  const ref = useScrollAnimation(
    (el) => slideIn(el, "left", { duration: 0.8 }),
    {
      start: "top 80%",
      once: true,
    }
  );

  return (
    <section ref={ref as React.RefObject<HTMLElement>}>
      <h2>{title}</h2>
      {children}
    </section>
  );
}
```

### مثال 3: Timeline Animation

```tsx
import { useTimeline } from "../hooks/useGSAP";
import { useEffect } from "react";

function AnimatedSequence() {
  const { timeline, play } = useTimeline();

  useEffect(() => {
    if (timeline) {
      timeline
        .to(".element1", { x: 100, duration: 1 })
        .to(".element2", { y: 50, duration: 1 }, "-=0.5")
        .to(".element3", { rotation: 360, duration: 1 });
    }
  }, [timeline]);

  return (
    <div>
      <button onClick={play}>Play Animation</button>
      <div className="element1">Element 1</div>
      <div className="element2">Element 2</div>
      <div className="element3">Element 3</div>
    </div>
  );
}
```

### مثال 4: Parallax Background

```tsx
import { useParallax } from "../hooks/useGSAP";

function HeroSection() {
  const backgroundRef = useParallax(-0.5);
  const contentRef = useParallax(0.3);

  return (
    <section className="hero">
      <div ref={backgroundRef as React.RefObject<HTMLDivElement>} className="background">
        Background
      </div>
      <div ref={contentRef as React.RefObject<HTMLDivElement>} className="content">
        Content
      </div>
    </section>
  );
}
```

## ⚙️ تنظیمات

### Default Settings

```typescript
export const GSAP_DEFAULTS = {
  duration: 0.6,
  ease: "power2.out",
  stagger: 0.1,
};
```

### Easing Functions

```typescript
export const EASING = {
  smooth: "power2.out",
  bounce: "bounce.out",
  elastic: "elastic.out(1, 0.3)",
  back: "back.out(1.7)",
  sine: "sine.out",
};
```

## 🎯 Best Practices

### 1. Cleanup ScrollTriggers

همیشه ScrollTriggers را در cleanup function پاک کنید:

```tsx
useEffect(() => {
  // Setup animations
  return () => {
    cleanupScrollTriggers();
  };
}, []);
```

### 2. Refresh After DOM Changes

بعد از تغییرات DOM، ScrollTriggers را refresh کنید:

```tsx
import { useScrollRefresh } from "../hooks/useGSAP";

function DynamicList({ items }: { items: any[] }) {
  const refresh = useScrollRefresh();

  useEffect(() => {
    refresh();
  }, [items, refresh]);
}
```

### 3. Performance

- از `will-change` CSS property برای عناصر متحرک استفاده کنید
- از `transform` و `opacity` استفاده کنید (GPU-accelerated)
- از `once: true` در ScrollTrigger برای انیمیشن‌های یک‌باره استفاده کنید

### 4. Accessibility

- انیمیشن‌ها را برای کاربرانی که `prefers-reduced-motion` دارند غیرفعال کنید:

```tsx
import { useEffect } from "react";
import { gsap } from "gsap";

useEffect(() => {
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (prefersReducedMotion) {
    gsap.set("*", { clearProps: "all" });
  }
}, []);
```

## 🔧 Advanced Usage

### Custom Animation

```tsx
import { gsap } from "gsap";

function CustomAnimation() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current) {
      gsap.to(ref.current, {
        x: 100,
        rotation: 360,
        duration: 2,
        ease: "elastic.out(1, 0.3)",
      });
    }
  }, []);

  return <div ref={ref}>Animated</div>;
}
```

### ScrollTrigger Advanced

```tsx
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { gsap } from "gsap";

useEffect(() => {
  ScrollTrigger.create({
    trigger: ".element",
    start: "top center",
    end: "bottom top",
    pin: true,
    scrub: 1,
    animation: gsap.to(".element", {
      x: 500,
      duration: 1,
    }),
  });

  return () => {
    ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
  };
}, []);
```

## 📚 منابع بیشتر

- [GSAP Documentation](https://greensock.com/docs/)
- [ScrollTrigger Documentation](https://greensock.com/docs/v3/Plugins/ScrollTrigger)
- [GSAP React Integration](https://greensock.com/react/)

