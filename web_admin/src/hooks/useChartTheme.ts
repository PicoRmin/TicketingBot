import { useEffect, useState } from "react";

export type ChartTheme = {
  background: string;
  surface: string;
  foreground: string;
  muted: string;
  grid: string;
  border: string;
  palette: string[];
  success: string;
  warning: string;
  danger: string;
  info: string;
};

const fallbackTheme: ChartTheme = {
  background: "#0f172a",
  surface: "#1e293b",
  foreground: "#f8fafc",
  muted: "#cbd5f5",
  grid: "rgba(148, 163, 184, 0.2)",
  border: "rgba(148, 163, 184, 0.4)",
  palette: ["#6366f1", "#22c55e", "#f97316", "#14b8a6", "#f43f5e", "#a855f7"],
  success: "#10b981",
  warning: "#f59e0b",
  danger: "#ef4444",
  info: "#0ea5e9",
};

const cssVariableNames = {
  background: "--bg-primary",
  surface: "--bg-secondary",
  foreground: "--fg-primary",
  muted: "--fg-secondary",
  grid: "--grid-color",
  border: "--border",
  primary: "--primary",
  accent: "--accent",
  success: "--success",
  warning: "--warning",
  danger: "--danger",
};

const readCssVariable = (styles: CSSStyleDeclaration, variable: string, fallback: string) => {
  const value = styles.getPropertyValue(variable);
  return value ? value.trim() : fallback;
};

const computeTheme = (): ChartTheme => {
  if (typeof window === "undefined") {
    return fallbackTheme;
  }

  const styles = getComputedStyle(document.documentElement);
  const background = readCssVariable(styles, cssVariableNames.background, fallbackTheme.background);
  const surface = readCssVariable(styles, cssVariableNames.surface, fallbackTheme.surface);
  const foreground = readCssVariable(styles, cssVariableNames.foreground, fallbackTheme.foreground);
  const muted = readCssVariable(styles, cssVariableNames.muted, fallbackTheme.muted);
  const grid = readCssVariable(styles, cssVariableNames.grid, fallbackTheme.grid);
  const border = readCssVariable(styles, cssVariableNames.border, fallbackTheme.border);
  const primary = readCssVariable(styles, cssVariableNames.primary, fallbackTheme.palette[0]);
  const accent = readCssVariable(styles, cssVariableNames.accent, fallbackTheme.palette[1]);
  const success = readCssVariable(styles, cssVariableNames.success, fallbackTheme.success);
  const warning = readCssVariable(styles, cssVariableNames.warning, fallbackTheme.warning);
  const danger = readCssVariable(styles, cssVariableNames.danger, fallbackTheme.danger);

  return {
    background,
    surface,
    foreground,
    muted,
    grid,
    border,
    palette: [primary, accent, "#f97316", "#14b8a6", "#f43f5e", "#a855f7"],
    success,
    warning,
    danger,
    info: accent,
  };
};

export function useChartTheme() {
  const [chartTheme, setChartTheme] = useState<ChartTheme>(computeTheme);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const updateTheme = () => setChartTheme(computeTheme());

    updateTheme();

    const observer = new MutationObserver(updateTheme);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class", "style"] });

    window.addEventListener("resize", updateTheme);

    return () => {
      observer.disconnect();
      window.removeEventListener("resize", updateTheme);
    };
  }, []);

  return chartTheme;
}

