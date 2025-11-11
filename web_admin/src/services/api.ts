const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || "http://localhost:8000";

const TOKEN_KEY = "imehr_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function logout() {
  localStorage.removeItem(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
  return !!getToken();
}

export async function apiGet(path: string) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {})
    }
  });
  if (!res.ok) {
    const body = await safeJson(res);
    throw new Error(body?.detail || res.statusText);
  }
  return res.json();
}

export async function apiPatch(path: string, body: any) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {})
    },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const data = await safeJson(res);
    throw new Error(data?.detail || res.statusText);
  }
  return res.json();
}

export async function apiUploadFile(path: string, formData: FormData) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {})
    },
    body: formData
  });
  if (!res.ok) {
    const data = await safeJson(res);
    throw new Error(data?.detail || res.statusText);
  }
  return res.json();
}

export async function apiPost(path: string, body: any) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(getToken() ? { Authorization: `Bearer ${getToken()}` } : {})
    },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const data = await safeJson(res);
    throw new Error(data?.detail || res.statusText);
  }
  return res.json();
}

export async function login(username: string, password: string) {
  const form = new URLSearchParams();
  form.append("username", username);
  form.append("password", password);

  const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form.toString()
  });

  if (!res.ok) {
    return false;
  }
  const data = await res.json();
  if (data?.access_token) {
    setToken(data.access_token);
    return true;
  }
  return false;
}

async function safeJson(res: Response) {
  try {
    return await res.json();
  } catch {
    return null;
  }
}

export { API_BASE_URL };

