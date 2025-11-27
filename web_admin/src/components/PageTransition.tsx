import { AnimatePresence, motion } from "framer-motion";
import { Outlet, useLocation } from "react-router-dom";
import { pageTransitionVariants, reducedMotionVariants } from "../lib/motion";
import { useMotionPreferences } from "../hooks/useMotionPreferences";

export function PageTransition() {
  const location = useLocation();
  const { shouldReduceMotion } = useMotionPreferences();
  const variants = shouldReduceMotion ? reducedMotionVariants : pageTransitionVariants;

  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.section
        key={location.pathname}
        variants={variants}
        initial="initial"
        animate="enter"
        exit="exit"
        style={{ height: "100%" }}
      >
        <Outlet />
      </motion.section>
    </AnimatePresence>
  );
}

