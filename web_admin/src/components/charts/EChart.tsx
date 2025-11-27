import { memo } from "react";
import ReactEChartsCore from "echarts-for-react/lib/core";
import * as echarts from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import {
  BarChart,
  LineChart,
  PieChart,
  RadarChart,
  ScatterChart,
  GaugeChart,
} from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  DatasetComponent,
  TransformComponent,
  DataZoomComponent,
  ToolboxComponent,
  VisualMapComponent,
} from "echarts/components";
import { LabelLayout, UniversalTransition } from "echarts/features";
import type { EChartsOption } from "echarts";

echarts.use([
  BarChart,
  LineChart,
  PieChart,
  RadarChart,
  ScatterChart,
  GaugeChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  DatasetComponent,
  TransformComponent,
  DataZoomComponent,
  ToolboxComponent,
  VisualMapComponent,
  CanvasRenderer,
  LabelLayout,
  UniversalTransition,
]);

type EChartProps = {
  option: EChartsOption;
  height?: number;
  loading?: boolean;
  testId?: string;
  ariaLabel?: string;
};

const baseLoadingOption = {
  text: "در حال بارگذاری داده‌ها...",
  color: "#6366f1",
  textColor: "#94a3b8",
  maskColor: "rgba(15, 23, 42, 0.35)",
};

function EChartComponent({ option, height = 320, loading = false, testId, ariaLabel }: EChartProps) {
  return (
    <div style={{ width: "100%", height }}>
      <ReactEChartsCore
        aria-label={ariaLabel}
        role="img"
        echarts={echarts}
        option={option}
        notMerge
        lazyUpdate
        style={{ width: "100%", height: "100%" }}
        showLoading={loading}
        loadingOption={baseLoadingOption}
        data-testid={testId}
      />
    </div>
  );
}

export const EChart = memo(EChartComponent);

