/**
 * Assets API client (GET /api/v1/assets, GET /api/v1/assets/{id}) FR-018.
 */

const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export interface AssetListItem {
  id: number
  symbol: string
  name: string
  asset_type: string
  currency_id: number | null
  exchange: string | null
  sector_id: number | null
  country_id: number | null
}

export interface AssetListResponse {
  items: AssetListItem[]
  total: number
}

export interface AssetDetail {
  id: number
  symbol: string
  name: string
  asset_type: string
  currency_id: number | null
  exchange: string | null
  sector_id: number | null
  country_id: number | null
}

export interface AssetListParams {
  asset_type?: string
  limit?: number
}

export interface AssetCreateParams {
  symbol: string
  name: string
  asset_type: string
  currency_id?: number | null
  exchange?: string | null
  sector_id?: number | null
  country_id?: number | null
}

export async function getAssets (params?: AssetListParams): Promise<AssetListResponse> {
  const search = new URLSearchParams()
  if (params?.asset_type != null) search.set('asset_type', params.asset_type)
  if (params?.limit != null) search.set('limit', String(params.limit))
  const qs = search.toString()
  const url = `${BASE}/assets${qs ? `?${qs}` : ''}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`)
  return res.json()
}

export async function getAsset (id: number): Promise<AssetDetail> {
  const res = await fetch(`${BASE}/assets/${id}`)
  if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`)
  return res.json()
}

export async function createAsset (params: AssetCreateParams): Promise<AssetDetail> {
  const res = await fetch(`${BASE}/assets`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      symbol: params.symbol,
      name: params.name,
      asset_type: params.asset_type,
      currency_id: params.currency_id ?? null,
      exchange: params.exchange ?? null,
      sector_id: params.sector_id ?? null,
      country_id: params.country_id ?? null,
    }),
  })
  if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`)
  return res.json()
}
