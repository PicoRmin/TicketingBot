/**
 * Example component using GSAP animations
 * 
 * این کامپوننت نمونه‌ای از استفاده از GSAP در کامپوننت‌های React است.
 */

import { ReactNode } from "react";
import { useScrollAnimation, useFadeIn } from "../hooks/useGSAP";
import { fadeIn } from "../lib/gsap";

interface AnimatedCardProps {
  children: ReactNode;
  animation?: "fade" | "slide" | "scale";
  direction?: "left" | "right" | "top" | "bottom";
  scrollTrigger?: boolean;
  className?: string;
}

/**
 * AnimatedCard component with GSAP animations
 * 
 * @example
 * <AnimatedCard animation="fade" scrollTrigger>
 *   <div>Card content</div>
 * </AnimatedCard>
 */
export function AnimatedCard({
  children,
  animation: _animation = "fade",
  direction: _direction = "left",
  scrollTrigger = false,
  className = "",
}: AnimatedCardProps) {
  // Use scroll-triggered animation if enabled
  const scrollRef = useScrollAnimation(
    fadeIn,
    scrollTrigger
      ? {
          start: "top 80%",
          once: true,
        }
      : undefined
  );

  // Use regular fade in if scroll trigger is disabled
  const fadeRef = useFadeIn(
    scrollTrigger
      ? undefined
      : {
          delay: 0.1,
        }
  );

  const ref = scrollTrigger ? scrollRef : fadeRef;

  return (
    <div ref={ref as React.RefObject<HTMLDivElement>} className={className}>
      {children}
    </div>
  );
}

