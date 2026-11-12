import type { FilterState } from '@/types/api';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export function buildFilterParams(filters: Partial<FilterState>, extra?: Record<string, string | number | undefined>) {
  const params = new URLSearchParams();
  if (filters.start_date) params.set('start_date', filters.start_date);
  if (filters.end_date) params.set('end_date', filters.end_date);
  if (filters.segment && filters.segment !== 'All') params.set('segment', filters.segment);
  if (filters.team_id && filters.team_id !== 'All') params.set('team_id', filters.team_id);
  if (filters.region && filters.region !== 'All') params.set('region', filters.region);
  if (filters.asset_tier && filters.asset_tier !== 'All') params.set('asset_tier', filters.asset_tier);
  if (extra) {
    Object.entries(extra).forEach(([k, v]) => {
      if (v !== undefined && v !== '' && v !== 'All') params.set(k, String(v));
    });
  }
  return params.toString();
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`API error ${res.status}: ${errText}`);
  }
  return res.json();
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`API error ${res.status}: ${errText}`);
  }
  return res.json();
}

export async function apiPatch<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`API error ${res.status}: ${errText}`);
  }
  return res.json();
}

export async function downloadBlob(path: string, method: 'GET' | 'POST', filename: string, body?: unknown) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`Download failed (${res.status})`);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
