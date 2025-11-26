import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { I18nextProvider } from "react-i18next";

import App from "./App";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Tickets from "./pages/Tickets";
import TicketDetail from "./pages/TicketDetail";
import "./styles.css";
import Branches from "./pages/Branches";
import Departments from "./pages/Departments";
import Automation from "./pages/Automation";
import SLAManagement from "./pages/SLAManagement";
import Users from "./pages/Users";
import Settings from "./pages/Settings";
import Infrastructure from "./pages/Infrastructure";
import UserPortal from "./pages/UserPortal";
import UserTicketDetail from "./pages/UserTicketDetail";
import UserDashboard from "./pages/UserDashboard";
import CustomFields from "./pages/CustomFields";
import { ErrorBoundary } from "./ErrorBoundary";
import ProtectedRoute from "./routes/ProtectedRoute";
import { GlobalErrorToast } from "./components/GlobalErrorToast";
import i18n from "./i18n";

const adminViewRoles = ["central_admin", "admin", "branch_admin", "it_specialist", "report_manager"];
const operationalRoles = ["central_admin", "admin", "branch_admin", "it_specialist"];
const adminRoles = ["central_admin", "admin"];
const centralRoles = ["central_admin"];
const userRoles = ["user"];

const router = createBrowserRouter(
  [
    {
      path: "/login",
      element: <Login />,
    },
    {
      path: "/",
      element: (
        <ProtectedRoute>
          <App />
        </ProtectedRoute>
      ),
      children: [
        {
          path: "/",
          element: (
            <ProtectedRoute allowedRoles={adminViewRoles}>
              <Dashboard />
            </ProtectedRoute>
          ),
        },
        {
          path: "/tickets",
          element: (
            <ProtectedRoute allowedRoles={operationalRoles}>
              <Tickets />
            </ProtectedRoute>
          ),
        },
        {
          path: "/tickets/:id",
          element: (
            <ProtectedRoute allowedRoles={operationalRoles}>
              <TicketDetail />
            </ProtectedRoute>
          ),
        },
        {
          path: "/branches",
          element: (
            <ProtectedRoute allowedRoles={["central_admin", "admin", "branch_admin"]}>
              <Branches />
            </ProtectedRoute>
          ),
        },
        {
          path: "/departments",
          element: (
            <ProtectedRoute allowedRoles={adminRoles}>
              <Departments />
            </ProtectedRoute>
          ),
        },
        {
          path: "/users",
          element: (
            <ProtectedRoute allowedRoles={adminRoles}>
              <Users />
            </ProtectedRoute>
          ),
        },
        {
          path: "/automation",
          element: (
            <ProtectedRoute allowedRoles={adminRoles}>
              <Automation />
            </ProtectedRoute>
          ),
        },
        {
          path: "/sla",
          element: (
            <ProtectedRoute allowedRoles={adminRoles}>
              <SLAManagement />
            </ProtectedRoute>
          ),
        },
        {
          path: "/settings",
          element: (
            <ProtectedRoute allowedRoles={centralRoles}>
              <Settings />
            </ProtectedRoute>
          ),
        },
        {
          path: "/infrastructure",
          element: (
            <ProtectedRoute allowedRoles={centralRoles}>
              <Infrastructure />
            </ProtectedRoute>
          ),
        },
        {
          path: "/user-portal",
          element: (
            <ProtectedRoute allowedRoles={userRoles}>
              <UserPortal />
            </ProtectedRoute>
          ),
        },
        {
          path: "/user-tickets/:id",
          element: (
            <ProtectedRoute allowedRoles={userRoles}>
              <UserTicketDetail />
            </ProtectedRoute>
          ),
        },
        {
          path: "/user-dashboard",
          element: (
            <ProtectedRoute allowedRoles={userRoles}>
              <UserDashboard />
            </ProtectedRoute>
          ),
        },
        {
          path: "/custom-fields",
          element: (
            <ProtectedRoute allowedRoles={adminRoles}>
              <CustomFields />
            </ProtectedRoute>
          ),
        },
      ],
    },
  ],
  {
    future: {
      v7_startTransition: true,
    },
  }
);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <I18nextProvider i18n={i18n}>
      <ErrorBoundary>
        <RouterProvider router={router} />
        <GlobalErrorToast />
      </ErrorBoundary>
    </I18nextProvider>
  </React.StrictMode>
);

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js")
      .catch((err) => console.warn("Service worker registration failed:", err));
  });
}

