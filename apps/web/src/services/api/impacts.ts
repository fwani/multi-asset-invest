/**
 * Impacts API client (GET /api/v1/events/{id}/impacts, GET /api/v1/assets/{id}/impacts).
 */

const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export interface AssetImpactItem {
  id: number
  event_id: number
  asset_id: number
  direction: string
  strength: number | null
  computed_at: string
}

export interface AssetImpactsParams {
  from_date?: string
  to_date?: string
  limit?: number
}

export async function getEventImpacts (eventId: number): Promise<AssetImpactItem[]> {
  const res = await fetch(`${BASE}/events/${eventId}/impacts`)
  if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`)
  return res.json()
}

export async function getAssetImpacts (
  assetId: number,
  params?: AssetImpactsParams
): Promise<AssetImpactItem[]> {
  const search = new URLSearchParams()
  if (params?.from_date != null) search.set('from_date', params.from_date)
  if (params?.to_date != null) search.set('to_date', params.to_date)
  if (params?.limit != null) search.set('limit', String(params.limit))
  const qs = search.toString()
  const url = `${BASE}/assets/${assetId}/impacts${qs ? `?${qs}` : ''}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`)
  return res.json()
}
