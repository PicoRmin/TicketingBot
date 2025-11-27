/**
 * Custom React Hook for GSAP animations
 * 
 * این hook برای استفاده از GSAP در کامپوننت‌های React طراحی شده است.
 */

import { useEffect, useRef, RefObject } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import {
  fadeIn,
  fadeOut,
  slideIn,
  scaleIn,
  scrollAnimation,
  parallax,
  cleanupScrollTriggers,
  refreshScrollTriggers,
  type EASING,
} from "../lib/gsap";

/**
 * Hook for fade in animation
 * 
 * @example
 * const ref = useFadeIn({ delay: 0.2 })
 * return <div ref={ref}>Content</div>
 */
export function useFadeIn(options: {
  duration?: number;
  delay?: number;
  ease?: keyof typeof EASING;
  opacity?: number;
} = {}) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (ref.current) {
      fadeIn(ref.current, options);
    }
  }, []);

  return ref as RefObject<HTMLElement>;
}

/**
 * Hook for slide in animation
 * 
 * @example
 * const ref = useSlideIn('left', { duration: 0.8 })
 * return <div ref={ref}>Content</div>
 */
export function useSlideIn(
  direction: "left" | "right" | "top" | "bottom" = "left",
  options: {
    duration?: number;
    delay?: number;
    ease?: keyof typeof EASING;
    distance?: number;
  } = {}
) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (ref.current) {
      slideIn(ref.current, direction, options);
    }
  }, [direction]);

  return ref as RefObject<HTMLElement>;
}

/**
 * Hook for scale animation
 * 
 * @example
 * const ref = useScaleIn({ from: 0.8, to: 1 })
 * return <div ref={ref}>Content</div>
 */
export function useScaleIn(options: {
  duration?: number;
  delay?: number;
  ease?: keyof typeof EASING;
  from?: number;
  to?: number;
} = {}) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (ref.current) {
      scaleIn(ref.current, options);
    }
  }, []);

  return ref as RefObject<HTMLElement>;
}

/**
 * Hook for scroll-triggered animation
 * 
 * @example
 * const ref = useScrollAnimation(fadeIn, { start: 'top 80%' })
 * return <div ref={ref}>Content</div>
 */
export function useScrollAnimation(
  animationFn: (el: gsap.TweenTarget, opts?: any) => gsap.core.Tween,
  options: {
    start?: string;
    end?: string;
    toggleActions?: string;
    once?: boolean;
    markers?: boolean;
  } = {}
) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (ref.current) {
      scrollAnimation(ref.current, animationFn, options);
    }

    return () => {
      cleanupScrollTriggers();
    };
  }, []);

  return ref as RefObject<HTMLElement>;
}

/**
 * Hook for parallax effect
 * 
 * @example
 * const ref = useParallax(-0.5)
 * return <div ref={ref}>Parallax Content</div>
 */
export function useParallax(
  speed: number = 0.5,
  options: {
    start?: string;
    end?: string;
  } = {}
) {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    if (ref.current) {
      parallax(ref.current, speed, options);
    }

    return () => {
      cleanupScrollTriggers();
    };
  }, [speed]);

  return ref as RefObject<HTMLElement>;
}

/**
 * Hook for managing GSAP timeline
 * 
 * @example
 * const { timeline, play, pause, reverse } = useTimeline()
 * 
 * useEffect(() => {
 *   timeline.to('.element', { x: 100, duration: 1 })
 * }, [])
 */
export function useTimeline() {
  const timelineRef = useRef<gsap.core.Timeline | null>(null);

  useEffect(() => {
    timelineRef.current = gsap.timeline();

    return () => {
      if (timelineRef.current) {
        timelineRef.current.kill();
      }
    };
  }, []);

  const play = () => {
    if (timelineRef.current) {
      timelineRef.current.play();
    }
  };

  const pause = () => {
    if (timelineRef.current) {
      timelineRef.current.pause();
    }
  };

  const reverse = () => {
    if (timelineRef.current) {
      timelineRef.current.reverse();
    }
  };

  const restart = () => {
    if (timelineRef.current) {
      timelineRef.current.restart();
    }
  };

  return {
    timeline: timelineRef.current,
    play,
    pause,
    reverse,
    restart,
  };
}

/**
 * Hook for refreshing ScrollTriggers after DOM changes
 * 
 * @example
 * const refresh = useScrollRefresh()
 * 
 * useEffect(() => {
 *   // After DOM changes
 *   refresh()
 * }, [data])
 */
export function useScrollRefresh() {
  return () => {
    refreshScrollTriggers();
  };
}

