import { emitError } from "./errorBus";

const API_BASE_URL = (import.meta as { env?: { VITE_API_BASE_URL?: string } }).env?.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const SESSION_EXPIRED_MESSAGE = "نشست شما منقضی شده است. لطفاً دوباره وارد شوید.";
const NETWORK_ERROR_MESSAGE = `خطا در اتصال به سرور. لطفاً مطمئن شوید که Backend روی ${API_BASE_URL} در حال اجرا است.`;

const TOKEN_KEY = "imehr_token";
const PROFILE_KEY = "imehr_profile";

export type UserRole =
  | "central_admin"
  | "admin"
  | "branch_admin"
  | "it_specialist"
  | "report_manager"
  | "user";

export type AuthProfile = {
  id: number;
  username: string;
  full_name?: string | null;
  role: UserRole;
  email?: string | null;
  branch_id?: number | null;
  department_id?: number | null;
  language?: string | null;
  avatar_url?: string | null;
};

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  clearProfile();
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

export function setProfile(profile: AuthProfile | null) {
  if (!profile) {
    clearProfile();
    return;
  }
  localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
}

export function getStoredProfile(): AuthProfile | null {
  const raw = localStorage.getItem(PROFILE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as AuthProfile;
  } catch {
    return null;
  }
}

export function clearProfile() {
  localStorage.removeItem(PROFILE_KEY);
}

async function safeJson(res: Response) {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await safeJson(res);
    let errorMessage = body?.detail || body?.message || res.statusText || "خطای نامشخص";
    if (res.status === 401) {
      errorMessage = SESSION_EXPIRED_MESSAGE;
      logout();
    }
    emitError(errorMessage, res.status);
    throw new Error(errorMessage);
  }
  try {
    return await res.json();
  } catch {
    // در برخی DELETE ها بدنه‌ای نداریم
    return undefined as T;
  }
}

async function fetchWithErrorHandling(
  url: string,
  options: RequestInit = {}
): Promise<Response> {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...(options.headers || {}),
        ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {}),
      },
    });
    return response;
  } catch (error) {
    // Network error or CORS error
    if (error instanceof Error && (error.name === "TypeError" || error.message.includes("fetch"))) {
      emitError(NETWORK_ERROR_MESSAGE);
      throw new Error(NETWORK_ERROR_MESSAGE);
    }
    throw error;
  }
}

export async function apiGet(path: string) {
  const res = await fetchWithErrorHandling(`${API_BASE_URL}${path}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return handleResponse(res);
}

export async function apiPatch(path: string, body: Record<string, unknown>) {
  const res = await fetchWithErrorHandling(`${API_BASE_URL}${path}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

export async function apiPut(path: string, body: Record<string, unknown>) {
  const res = await fetchWithErrorHandling(`${API_BASE_URL}${path}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

export async function apiUploadFile(path: string, formData: FormData) {
  const res = await fetchWithErrorHandling(`${API_BASE_URL}${path}`, {
    method: "POST",
    body: formData,
  });
  return handleResponse(res);
}

export async function apiPost(path: string, body: Record<string, unknown>) {
  const res = await fetchWithErrorHandling(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

export async function apiDelete(path: string) {
  const res = await fetchWithErrorHandling(`${API_BASE_URL}${path}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await safeJson(res);
    const errorMessage = body?.detail || body?.message || res.statusText || "خطای نامشخص";
    emitError(errorMessage, res.status);
    if (res.status === 401) {
      logout();
    }
    throw new Error(errorMessage);
  }
  return true;
}

export async function login(username: string, password: string) {
  const form = new URLSearchParams();
  form.append("username", username);
  form.append("password", password);

  try {
    const res = await fetchWithErrorHandling(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });

    if (!res.ok) {
      const body = await safeJson(res);
      const errorMessage = body?.detail || "نام کاربری یا رمز عبور نادرست است.";
      emitError(errorMessage, res.status);
      return false;
    }
    const data = await res.json();
    if (data?.access_token) {
      setToken(data.access_token);
      try {
        const profile = await fetchProfile();
        setProfile(profile);
      } catch (error) {
        console.warn("Failed to fetch profile after login", error);
      }
      return true;
    }
    emitError("پاسخ نامعتبر از سرور دریافت شد.");
    return false;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "خطای ناشناخته در فرآیند ورود";
    emitError(errorMessage);
    return false;
  }
}

export { API_BASE_URL };

export async function fetchProfile() {
  return apiGet("/api/auth/me") as Promise<AuthProfile>;
}

// User management API helpers
export async function fetchUsers(params: string = "") {
  const query = params ? params : "";
  return apiGet(`/api/users${query}`);
}

export async function createUserApi(body: Record<string, unknown>) {
  return apiPost("/api/users", body);
}

export async function updateUserApi(id: number, body: Record<string, unknown>) {
  return apiPut(`/api/users/${id}`, body);
}

export async function deleteUserApi(id: number) {
  return apiDelete(`/api/users/${id}`);
}
