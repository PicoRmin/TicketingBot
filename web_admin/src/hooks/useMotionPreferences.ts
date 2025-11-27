import { useEffect, useState } from "react";

/**
 * Hook to respect prefers-reduced-motion and provide a runtime switch
 * for disabling Framer Motion animations in low-performance contexts.
 */
export function useMotionPreferences() {
  const [shouldReduceMotion, setShouldReduceMotion] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
      return;
    }

    const mediaQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    const handleChange = () => setShouldReduceMotion(mediaQuery.matches);

    handleChange();
    mediaQuery.addEventListener("change", handleChange);

    return () => mediaQuery.removeEventListener("change", handleChange);
  }, []);

  return { shouldReduceMotion };
}

