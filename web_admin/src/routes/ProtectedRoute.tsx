import { ReactElement, ReactNode, useEffect, useMemo, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import {
  getToken,
  fetchProfile,
  getStoredProfile,
  setProfile,
  logout,
} from "../services/api";
import { emitError } from "../services/errorBus";

type Props = {
  children: ReactNode;
  allowedRoles?: string[];
  fallbackPath?: string;
};

type Status = "loading" | "ready" | "denied";

export default function ProtectedRoute({
  children,
  allowedRoles,
  fallbackPath = "/login",
}: Props): ReactElement {
  const [status, setStatus] = useState<Status>("loading");
  const [role, setRole] = useState<string | null>(getStoredProfile()?.role || null);
  const location = useLocation();

  const roleAllowed = useMemo(() => {
    if (!allowedRoles || !allowedRoles.length) {
      return true;
    }
    return role ? allowedRoles.includes(role) : false;
  }, [allowedRoles, role]);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setStatus("denied");
      return;
    }

    const stored = getStoredProfile();
    if (stored) {
      setRole(stored.role);
      setStatus("ready");
      return;
    }

    fetchProfile()
      .then((profile) => {
        setProfile(profile);
        setRole(profile?.role ?? null);
        setStatus("ready");
      })
      .catch(() => {
        emitError("نشست شما منقضی شده است. لطفاً دوباره وارد شوید.", 401);
        logout();
        setStatus("denied");
      });
  }, []);

  if (status === "loading") {
    return (
      <div style={{ padding: 40, textAlign: "center" }}>
        <div className="loading" style={{ marginBottom: 16 }}></div>
        <div>در حال بررسی دسترسی...</div>
      </div>
    );
  }

  if (!roleAllowed || status === "denied") {
    return (
      <Navigate
        to={fallbackPath}
        replace
        state={{ from: location.pathname }}
      />
    );
  }

  return <>{children}</>;
}

