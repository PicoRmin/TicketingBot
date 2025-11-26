import { Link, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  AutomationIcon,
  BranchIcon,
  DashboardIcon,
  HomeIcon,
  TicketIcon,
  UserPortalIcon,
} from "./icons";

type IconComponent = (props: { className?: string }) => JSX.Element;

type NavItem = {
  to: string;
  match: string;
  Icon: IconComponent;
  labelKey: string;
  roles?: string[];
};

const adminNav: NavItem[] = [
  { to: "/", match: "/", Icon: DashboardIcon, labelKey: "nav.dashboard" },
  { to: "/tickets", match: "/tickets", Icon: TicketIcon, labelKey: "nav.tickets" },
  { to: "/branches", match: "/branches", Icon: BranchIcon, labelKey: "nav.branches", roles: ["central_admin", "admin", "branch_admin"] },
  { to: "/automation", match: "/automation", Icon: AutomationIcon, labelKey: "nav.automation", roles: ["central_admin", "admin"] },
];

const reportNav: NavItem[] = [
  { to: "/", match: "/", Icon: DashboardIcon, labelKey: "nav.dashboard" },
];

const userNav: NavItem[] = [
  { to: "/user-dashboard", match: "/user-dashboard", Icon: HomeIcon, labelKey: "nav.dashboard" },
  { to: "/user-portal", match: "/user-portal", Icon: UserPortalIcon, labelKey: "nav.userPortal" },
];

const getNavItemsForRole = (role?: string | null): NavItem[] => {
  if (role === "user") {
    return userNav;
  }
  if (role === "report_manager") {
    return reportNav;
  }
  return adminNav.filter((item) => {
    if (!item.roles) {
      return true;
    }
    if (!role) {
      return false;
    }
    return item.roles.includes(role);
  });
};

export function MobileNavigation({ role }: { role?: string }) {
  const { t } = useTranslation();
  const location = useLocation();
  const items = getNavItemsForRole(role);

  if (!items.length) {
    return null;
  }

  return (
    <nav className="mobile-nav">
      {items.map((item) => {
        const active = location.pathname === item.match || location.pathname.startsWith(item.match);
        const Icon = item.Icon;
        return (
          <Link key={item.to} to={item.to} className={`mobile-nav__item${active ? " active" : ""}`}>
            <Icon className="mobile-nav__icon" />
            <span className="mobile-nav__label">{t(item.labelKey)}</span>
          </Link>
        );
      })}
    </nav>
  );
}

