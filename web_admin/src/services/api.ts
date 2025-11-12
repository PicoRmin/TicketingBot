const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const TOKEN_KEY = "imehr_token";
const PROFILE_KEY = "imehr_profile";

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

export function setProfile(profile: any) {
  if (!profile) {
    clearProfile();
    return;
  }
  localStorage.setItem(PROFILE_KEY, JSON.stringify(profile));
}

export function getStoredProfile(): any | null {
  const raw = localStorage.getItem(PROFILE_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
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
    const errorMessage = body?.detail || body?.message || res.statusText || "خطای نامشخص";
    throw new Error(errorMessage);
  }
  return res.json();
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
  } catch (error: any) {
    // Network error or CORS error
    if (error.name === "TypeError" || error.message.includes("fetch")) {
      throw new Error(
        `خطا در اتصال به سرور. لطفاً مطمئن شوید که Backend روی ${API_BASE_URL} در حال اجرا است.`
      );
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

export async function apiPatch(path: string, body: any) {
  const res = await fetchWithErrorHandling(`${API_BASE_URL}${path}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });
  return handleResponse(res);
}

export async function apiPut(path: string, body: any) {
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

export async function apiPost(path: string, body: any) {
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
    return false;
  } catch (error: any) {
    console.error("Login error:", error);
    return false;
  }
}

export { API_BASE_URL };

export async function fetchProfile() {
  return apiGet("/api/auth/me");
}

// User management API helpers
export async function fetchUsers(params: string = "") {
  const query = params ? params : "";
  return apiGet(`/api/users${query}`);
}

export async function createUserApi(body: any) {
  return apiPost("/api/users", body);
}

export async function updateUserApi(id: number, body: any) {
  return apiPut(`/api/users/${id}`, body);
}

export async function deleteUserApi(id: number) {
  return apiDelete(`/api/users/${id}`);
}
