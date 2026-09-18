const BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
export async function api<T>(path: string): Promise<T> {
  const response = await fetch(`${BASE}${path}`);
  if (!response.ok) throw new Error(`API ${response.status}: ${await response.text()}`);
  return response.json() as Promise<T>;
}
