import { SVGProps } from "react";

type IconProps = SVGProps<SVGSVGElement>;

const baseProps = {
  width: 24,
  height: 24,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.8,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

function createIcon(paths: JSX.Element[]) {
  return function Icon(props: IconProps) {
    return (
      <svg {...baseProps} {...props}>
        {paths}
      </svg>
    );
  };
}

export const HomeIcon = createIcon([
  <path key="1" d="M3 10.5 12 3l9 7.5" />,
  <path key="2" d="M5 9.5V21h14V9.5" />,
  <path key="3" d="M9.5 21v-6h5v6" />,
]);

export const DashboardIcon = createIcon([
  <path key="1" d="M4 4h6.5v7H4z" />,
  <path key="2" d="M13.5 4H20v4.5h-6.5z" />,
  <path key="3" d="M13.5 10.5H20V20h-6.5z" />,
  <path key="4" d="M4 13.5h6.5V20H4z" />,
]);

export const TicketIcon = createIcon([
  <path key="1" d="M4 7h16v4a2 2 0 0 0 0 4v4H4v-4a2 2 0 0 0 0-4z" />,
  <path key="2" d="M9 7v10" />,
  <path key="3" d="M15 7v10" />,
]);

export const BranchIcon = createIcon([
  <path key="1" d="M12 3v18" />,
  <path key="2" d="M6 9h12" />,
  <path key="3" d="M6 15h12" />,
  <circle key="4" cx="6" cy="9" r="2.2" />,
  <circle key="5" cx="18" cy="15" r="2.2" />,
]);

export const AutomationIcon = createIcon([
  <circle key="1" cx="12" cy="12" r="3.2" />,
  <path key="2" d="M4 12h2.5" />,
  <path key="3" d="M17.5 12H20" />,
  <path key="4" d="M6.5 6.5 8 8" />,
  <path key="5" d="M16 16l1.5 1.5" />,
  <path key="6" d="M6.5 17.5 8 16" />,
  <path key="7" d="M16 8l1.5-1.5" />,
]);

export const UserPortalIcon = createIcon([
  <circle key="1" cx="12" cy="8" r="3" />,
  <path key="2" d="M5 19c1.8-3 4-4.5 7-4.5s5.2 1.5 7 4.5" />,
  <path key="3" d="M4 5h4" />,
  <path key="4" d="M16 5h4" />,
]);

export const BellIcon = createIcon([
  <path key="1" d="M6 10a6 6 0 0 1 12 0c0 5 1.5 6.5 1.5 6.5H4.5S6 15 6 10" />,
  <path key="2" d="M9.5 19a2.5 2.5 0 0 0 5 0" />,
]);

