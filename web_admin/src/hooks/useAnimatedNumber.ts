import { useEffect, useRef, useState } from "react";

type AnimatedNumberOptions = {
  duration?: number;
};

const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);

export function useAnimatedNumber(target: number, options: AnimatedNumberOptions = {}): number {
  const { duration = 600 } = options;
  const [value, setValue] = useState(target);
  const valueRef = useRef(target);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    const startValue = valueRef.current;
    const delta = target - startValue;
    let startTime: number | null = null;

    const step = (timestamp: number) => {
      if (startTime === null) {
        startTime = timestamp;
      }
      const progress = Math.min((timestamp - startTime) / duration, 1);
      const eased = easeOutCubic(progress);
      const nextValue = Math.round(startValue + delta * eased);
      valueRef.current = nextValue;
      setValue(nextValue);

      if (progress < 1) {
        rafRef.current = requestAnimationFrame(step);
      }
    };

    rafRef.current = requestAnimationFrame(step);
    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
      }
    };
  }, [target, duration]);

  return value;
}

