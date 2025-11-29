import { Link, useNavigate, useLocation } from "react-router-dom";
import { FormEvent, Fragment, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { Listbox, Menu, Transition } from "@headlessui/react";
import { useTranslation } from "react-i18next";
import { motion } from "framer-motion";
import {
  getToken,
  logout,
  getStoredProfile,
  fetchProfile,
  setProfile,
  clearProfile,
} from "./services/api";
import type { AuthProfile } from "./services/api";
import logoUrl from "./assets/brand-logo.svg";
import { MobileNavigation } from "./components/MobileNavigation";
import { NotificationBell } from "./components/NotificationBell";
import { TelegramBotStatusBadge } from "./components/TelegramBotStatusBadge";
import { PageTransition } from "./components/PageTransition";
import { Sidebar } from "./components/Sidebar";
import { HamburgerMenuButton } from "./components/HamburgerMenuButton";
import { headerRevealVariants, reducedMotionVariants } from "./lib/motion";
import { useMotionPreferences } from "./hooks/useMotionPreferences";
import {
  FiHome,
  FiSettings,
  FiUsers,
  FiSlack,
  FiLayers,
  FiGrid,
  FiFileText,
  FiDatabase,
  FiMessageCircle,
  FiGlobe,
  FiCpu,
  FiSun,
  FiMoon,
} from "react-icons/fi";

export default function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const token = getToken();
  const [profile, setProfileState] = useState<AuthProfile | null>(() => getStoredProfile());
  const [isMobile, setIsMobile] = useState<boolean>(() => {
    if (typeof window === "undefined") {
      return false;
    }
    return window.innerWidth <= 900;
  });
  const [dark, setDark] = useState<boolean>(() => {
    return localStorage.getItem("imehr_dark") === "1";
  });
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false);
  const [openCategory, setOpenCategory] = useState<string | null>(null);
  const { t, i18n } = useTranslation();
  const { shouldReduceMotion } = useMotionPreferences();
  const [searchValue, setSearchValue] = useState<string>("");

  useEffect(() => {
    if (!token) {
      setProfileState(null);
      clearProfile();
      navigate("/login");
      return;
    }

    const stored = getStoredProfile();
    if (stored) {
      setProfileState(stored);
        // Redirect regular users to user dashboard
        if (stored.role === "user" && window.location.pathname.startsWith("/") && 
            !window.location.pathname.startsWith("/user-portal") && 
            !window.location.pathname.startsWith("/user-tickets") &&
            !window.location.pathname.startsWith("/user-dashboard") &&
            window.location.pathname !== "/login") {
          navigate("/user-dashboard");
        }
      return;
    }

    fetchProfile()
      .then((p: AuthProfile) => {
        setProfile(p);
        setProfileState(p);
        // Redirect regular users to user dashboard
        if (p?.role === "user" && window.location.pathname.startsWith("/") && 
            !window.location.pathname.startsWith("/user-portal") && 
            !window.location.pathname.startsWith("/user-tickets") &&
            !window.location.pathname.startsWith("/user-dashboard") &&
            window.location.pathname !== "/login") {
          navigate("/user-dashboard");
        }
      })
      .catch(() => {
        // ignore
      });
  }, [token, navigate]);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 900);
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // Close menu when clicking outside
  useEffect(() => {
    if (!openCategory) return;
    
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.nav-category')) {
        setOpenCategory(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [openCategory]);

  useEffect(() => {
    const cls = document.documentElement.classList;
    const html = document.documentElement;
    
    // Add fade transition class
    html.classList.add("fade-transition");
    
    if (dark) {
      cls.add("dark");
      localStorage.setItem("imehr_dark", "1");
    } else {
      cls.remove("dark");
      localStorage.removeItem("imehr_dark");
    }
    
    // Remove transition class after animation completes
    const timer = setTimeout(() => {
      html.classList.remove("fade-transition");
    }, 500);
    
    return () => clearTimeout(timer);
  }, [dark]);

  const handleLogout = () => {
    logout();
    setProfileState(null);
    navigate("/login");
  };

  const isAdmin = profile && ["admin", "central_admin"].includes(profile.role);
  const isCentralAdmin = profile && profile.role === "central_admin";
  const isReportManager = profile && profile.role === "report_manager";
  const isOperational = profile && ["central_admin", "admin", "branch_admin", "it_specialist"].includes(profile.role);
  const displayName = profile?.full_name || profile?.username;

  // Role labels
  const getRoleLabel = (role: string) => {
    return t(`role.${role}`, { defaultValue: role });
  };
  
  const roleLabel = profile ? getRoleLabel(profile.role) : "";
  const handleLanguageChange = (value: string) => {
    i18n.changeLanguage(value);
  };
  const handleSearchSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const value = searchValue.trim();
    if (!value) return;
    const basePath = profile?.role === "user" ? "/user-tickets" : "/tickets";
    navigate(`${basePath}?q=${encodeURIComponent(value)}`);
  };
  const versionLabel = t("layout.version", { version: "0.1.0" });
  const headerVariants = shouldReduceMotion ? reducedMotionVariants : headerRevealVariants;
  const avatarLetter = displayName ? displayName.trim().charAt(0).toUpperCase() : "؟";

  // Dashboard is standalone
  const dashboardItem = { to: "/", label: t("nav.dashboard"), icon: <FiHome />, visible: true };

  // Navigation categories with hover menus
  const navCategories = [
    {
      id: "management",
      label: t("nav.management"),
      icon: <FiLayers />,
      items: [
        { to: "/tickets", label: t("nav.tickets"), icon: <FiFileText />, visible: !isReportManager },
        { to: "/branches", label: t("nav.branches"), icon: <FiGlobe />, visible: !isReportManager },
        { to: "/departments", label: t("nav.departments"), icon: <FiLayers />, visible: isAdmin },
        { to: "/users", label: t("nav.users"), icon: <FiUsers />, visible: isAdmin },
      ].filter((item) => item.visible),
    },
    {
      id: "automation",
      label: t("nav.automation"),
      icon: <FiSlack />,
      items: [
        { to: "/automation", label: t("nav.automation"), icon: <FiSlack />, visible: isAdmin },
        { to: "/sla", label: t("nav.sla"), icon: <FiGrid />, visible: isAdmin },
        { to: "/custom-fields", label: t("nav.customFields"), icon: <FiDatabase />, visible: isAdmin },
      ].filter((item) => item.visible),
    },
    {
      id: "infrastructure",
      label: t("nav.infrastructure"),
      icon: <FiCpu />,
      items: [
        { to: "/infrastructure", label: t("nav.infrastructure"), icon: <FiCpu />, visible: isCentralAdmin },
        { to: "/assets", label: t("nav.assets"), icon: <FiGrid />, visible: isOperational },
      ].filter((item) => item.visible),
    },
    {
      id: "settings",
      label: t("nav.settings"),
      icon: <FiSettings />,
      items: [
        { to: "/settings", label: t("nav.systemSettings"), icon: <FiSettings />, visible: isCentralAdmin },
        { to: "/telegram-bot/settings", label: t("nav.telegramBotSettings"), icon: <FiMessageCircle />, visible: isAdmin },
      ].filter((item) => item.visible),
    },
  ].filter((category) => category.items.length > 0);

  type NavItem = {
    to: string;
    label: string;
    icon: ReactNode;
  };

  const userNavItems: NavItem[] = [
    { to: "/user-dashboard", label: t("nav.dashboard"), icon: <FiHome /> },
    { to: "/user-portal", label: t("nav.userPortal"), icon: <FiFileText /> },
  ];
  
  const isActivePath = (path: string) => {
    if (path === "/") {
      return location.pathname === "/";
    }
    return location.pathname.startsWith(path);
  };

  const quickActions = profile?.role === "user"
    ? [
        {
          id: "user-new",
          icon: "✨",
          label: t("layout.quickActions.userNew.title"),
          subLabel: t("layout.quickActions.userNew.subtitle"),
          to: "/user-portal",
        },
        {
          id: "user-history",
          icon: "📋",
          label: t("layout.quickActions.userHistory.title"),
          subLabel: t("layout.quickActions.userHistory.subtitle"),
          to: "/user-tickets",
        },
      ]
    : [
        {
          id: "admin-new",
          icon: "➕",
          label: t("layout.quickActions.adminNew.title"),
          subLabel: t("layout.quickActions.adminNew.subtitle"),
          to: "/tickets",
        },
        {
          id: "admin-reports",
          icon: "📈",
          label: t("layout.quickActions.reports.title"),
          subLabel: t("layout.quickActions.reports.subtitle"),
          to: "/",
        },
        {
          id: "admin-sla",
          icon: "⏱️",
          label: t("layout.quickActions.sla.title"),
          subLabel: t("layout.quickActions.sla.subtitle"),
          to: "/sla",
        },
      ];

  const isRTL = i18n.language === "fa";

  return (
    <div className="container" style={{ display: "flex", minHeight: "100vh", direction: isRTL ? "rtl" : "ltr" }}>
      {token && <Sidebar profile={profile} isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />}
      <div 
        className="main-content-wrapper"
        style={{ 
          flex: 1, 
          display: "flex", 
          flexDirection: "column",
          marginLeft: sidebarOpen && !isRTL ? "var(--sidebar-width, 280px)" : "0",
          marginRight: sidebarOpen && isRTL ? "var(--sidebar-width, 280px)" : "0",
          maxWidth: sidebarOpen ? "calc(100% - var(--sidebar-width, 280px))" : "100%",
          transition: "margin 0.3s ease, max-width 0.3s ease",
        }}
      >
      <motion.header className="app-header" variants={headerVariants} initial="hidden" animate="visible">
        <div className="header-main">
          <div className="brand-block">
            {token && (
              <HamburgerMenuButton
                isOpen={sidebarOpen}
                onClick={() => setSidebarOpen(!sidebarOpen)}
                ariaLabel={t("layout.toggleMenu") || "Toggle sidebar"}
              />
            )}
            <Link to="/" className="brand">
              <img src={logoUrl} alt="لوگوی ایرانمهر" />
              <div className="brand-text">
                <span className="brand-title">{t("brandTitle")}</span>
                <span className="brand-subtitle">{t("brandSubtitle")}</span>
              </div>
            </Link>
            <span className="version-chip">{versionLabel}</span>
          </div>

          <div className="header-utilities">
            <form className="header-search" onSubmit={handleSearchSubmit}>
              <input
                value={searchValue}
                onChange={(e) => setSearchValue(e.target.value)}
                placeholder={t("layout.searchPlaceholder")}
                aria-label={t("layout.searchPlaceholder")}
              />
              <button type="submit" className="ghost">
                {t("layout.searchCta")}
              </button>
            </form>
            <div className="utility-buttons">
              {token && isAdmin && <TelegramBotStatusBadge enabled={!!token} />}
              <button
                onClick={() => setDark((d) => !d)}
                className="icon-button"
                type="button"
                aria-label={dark ? t("actions.light") : t("actions.dark")}
                title={dark ? t("actions.light") : t("actions.dark")}
              >
                {dark ? <FiSun /> : <FiMoon />}
              </button>
              {token && <NotificationBell />}
              <Listbox value={i18n.language} onChange={handleLanguageChange}>
                <div className="language-select">
                  <Listbox.Button className="language-select__button">
                    <span>{i18n.language === "fa" ? t("actions.langFa") : t("actions.langEn")}</span>
                    <span aria-hidden="true">▾</span>
                  </Listbox.Button>
                  <Transition
                    as={Fragment}
                    leave="headless-transition-leave"
                    leaveFrom="headless-transition-from"
                    leaveTo="headless-transition-to"
                  >
                    <Listbox.Options className="language-select__options">
                      {["fa", "en"].map((lang) => (
                        <Listbox.Option
                          key={lang}
                          value={lang}
                          className={({ active }) =>
                            `language-select__option${active ? " active" : ""}`
                          }
                        >
                          {lang === "fa" ? t("actions.langFa") : t("actions.langEn")}
                        </Listbox.Option>
                      ))}
                    </Listbox.Options>
                  </Transition>
                </div>
              </Listbox>
              {token ? (
                <Menu as="div" className="user-menu">
                  <Menu.Button className="user-card">
                    <div className="avatar-ring" aria-hidden="true">
                      {avatarLetter}
                    </div>
                    <div className="user-meta">
                      <span className="user-name">{displayName}</span>
                      {roleLabel && <span className="user-role-pill">{roleLabel}</span>}
                    </div>
                    <span className="user-menu__chevron" aria-hidden="true">
                      ▾
                    </span>
                  </Menu.Button>
                  <Transition
                    as={Fragment}
                    enter="headless-transition-enter"
                    enterFrom="headless-transition-enter-from"
                    enterTo="headless-transition-enter-to"
                    leave="headless-transition-leave"
                    leaveFrom="headless-transition-from"
                    leaveTo="headless-transition-to"
                  >
                    <Menu.Items className="user-menu__items">
                      <div className="user-menu__title">{t("layout.userMenu.title")}</div>
                      <Menu.Item>
                        {({ active }) => (
                          <Link
                            to={profile?.role === "user" ? "/user-dashboard" : "/"}
                            className={`user-menu__item${active ? " active" : ""}`}
                          >
                            {t("layout.userMenu.overview")}
                          </Link>
                        )}
                      </Menu.Item>
                      <Menu.Item>
                        {({ active }) => (
                          <button
                            type="button"
                            onClick={handleLogout}
                            className={`user-menu__item danger${active ? " active" : ""}`}
                          >
                            {t("layout.userMenu.logout")}
                          </button>
                        )}
                      </Menu.Item>
                    </Menu.Items>
                  </Transition>
                </Menu>
              ) : (
                <Link to="/login">
                  <button className="ghost" type="button">
                    {t("actions.login")}
                  </button>
                </Link>
              )}
            </div>
          </div>
        </div>

          <div className="header-bottom">
          <div className="nav-scroll">
            <nav className="primary-nav">
              {/* Dashboard - standalone */}
              {profile?.role !== "user" && dashboardItem.visible && (
                <Link
                  to={dashboardItem.to}
                  className={`nav-pill${isActivePath(dashboardItem.to) ? " active" : ""}`}
                >
                  <span className="nav-pill__icon" aria-hidden="true">
                    {dashboardItem.icon}
                  </span>
                  <span className="nav-pill__label">{dashboardItem.label}</span>
                </Link>
              )}
              
              {/* Categories with hover menus */}
              {profile?.role !== "user" && navCategories.map((category) => {
                const hasActiveItem = category.items.some((item) => isActivePath(item.to));
                const isOpen = openCategory === category.id;
                return (
                  <div 
                    key={category.id} 
                    className="nav-category"
                    onMouseEnter={() => setOpenCategory(category.id)}
                    onMouseLeave={() => setOpenCategory(null)}
                  >
                    <div 
                      className={`nav-pill nav-pill--category${hasActiveItem ? " active" : ""}${isOpen ? " open" : ""}`}
                      onClick={(e) => {
                        e.preventDefault();
                        setOpenCategory(isOpen ? null : category.id);
                      }}
                      style={{ cursor: "pointer" }}
                    >
                      <span className="nav-pill__icon" aria-hidden="true">
                        {category.icon}
                      </span>
                      <span className="nav-pill__label">{category.label}</span>
                      <span className="nav-pill__chevron" aria-hidden="true">▾</span>
                    </div>
                    <div className={`nav-category-menu${isOpen ? " open" : ""}`}>
                      {category.items.map((item) => (
                        <Link
                          key={item.to}
                          to={item.to}
                          className={`nav-category-item${isActivePath(item.to) ? " active" : ""}`}
                          onClick={() => setOpenCategory(null)}
                        >
                          <span className="nav-category-item__icon">{item.icon}</span>
                          <span className="nav-category-item__label">{item.label}</span>
                        </Link>
                      ))}
                    </div>
                  </div>
                );
              })}
              
              {/* User nav items (no categories) */}
              {profile?.role === "user" && userNavItems.map((item) => (
                <Link
                  key={item.to}
                  to={item.to}
                  className={`nav-pill${isActivePath(item.to) ? " active" : ""}`}
                >
                  <span className="nav-pill__icon" aria-hidden="true">
                    {item.icon}
                  </span>
                  <span className="nav-pill__label">{item.label}</span>
                </Link>
              ))}
            </nav>
          </div>
          <div className="quick-actions">
            <div className="quick-actions-title">{t("layout.quickActions.title")}</div>
            <div className="quick-actions-grid">
              {quickActions.map((action) => (
                <Link key={action.id} to={action.to} className="quick-action-card">
                  <span className="quick-action-icon" aria-hidden="true">
                    {action.icon}
                  </span>
                  <div>
                    <div className="quick-action-label">{action.label}</div>
                    <div className="quick-action-sub">{action.subLabel}</div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </motion.header>
      <main>
        <PageTransition />
      </main>
      {isMobile && token && (
        <MobileNavigation role={profile?.role} />
      )}
      <footer className="app-footer">
        <div className="app-footer__left">{t("layout.footer")}</div>
        <div className="app-footer__right">
          <span className="app-footer__version">{versionLabel}</span>
        </div>
      </footer>
      </div>
    </div>
  );
}
