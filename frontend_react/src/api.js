const FASTAPI_BASE_URL = import.meta.env?.VITE_FASTAPI_URL || "http://localhost:8000/api";

export async function apiRequest(endpoint, { method = "GET", body, token } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  const response = await fetch(`${FASTAPI_BASE_URL}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || data.error || "API request failed");
  }
  return data;
}
