import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
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
import { ErrorBoundary } from "./ErrorBoundary";

const router = createBrowserRouter([
  {
    path: "/login",
    element: <Login />,
  },
  {
    path: "/",
    element: <App />,
    children: [
      { path: "/", element: <Dashboard /> },
      { path: "/tickets", element: <Tickets /> },
      { path: "/tickets/:id", element: <TicketDetail /> },
      { path: "/branches", element: <Branches /> },
      { path: "/departments", element: <Departments /> },
      { path: "/users", element: <Users /> },
      { path: "/automation", element: <Automation /> },
      { path: "/sla", element: <SLAManagement /> },
      { path: "/settings", element: <Settings /> },
      { path: "/infrastructure", element: <Infrastructure /> },
      { path: "/user-portal", element: <UserPortal /> },
      { path: "/user-tickets/:id", element: <UserTicketDetail /> },
      { path: "/user-dashboard", element: <UserDashboard /> }
    ]
  }
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <RouterProvider router={router} />
    </ErrorBoundary>
  </React.StrictMode>
);

