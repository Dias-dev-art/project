const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface Scan {
  id: number;
  repo_full_name: string;
  pr_number: number;
  head_sha: string;
  status: string;
  created_at: string;
}

export async function fetchScans(): Promise<Scan[]> {
  const res = await fetch(`${API_URL}/api/v1/scans`);
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}
