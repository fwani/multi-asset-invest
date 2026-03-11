/**
 * Events API client (GET /api/v1/events, GET /api/v1/events/{id}).
 */

const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export interface EventListItem {
  id: number
  event_type: string
  country_id: number | null
  actor: string | null
  impact_type: string | null
  occurred_at: string
  source_summary: string | null
  confidence: number | null
  extracted_at: string
}

export interface EventListResponse {
  items: EventListItem[]
  total: number
}

export interface NewsSource {
  id: number
  source: string
  url: string | null
  title: string | null
}

export interface EventDetail {
  id: number
  event_type: string
  country_id: number | null
  actor: string | null
  impact_type: string | null
  occurred_at: string
  source_summary: string | null
  confidence: number | null
  extracted_at: string
  source: NewsSource | null
  metadata_?: Record<string, unknown> | null
}

export interface EventListParams {
  type?: string
  country?: number
  from_date?: string
  to_date?: string
  limit?: number
  offset?: number
}

export async function getEvents (params?: EventListParams): Promise<EventListResponse> {
  const search = new URLSearchParams()
  if (params?.type != null) search.set('type', params.type)
  if (params?.country != null) search.set('country', String(params.country))
  if (params?.from_date != null) search.set('from_date', params.from_date)
  if (params?.to_date != null) search.set('to_date', params.to_date)
  if (params?.limit != null) search.set('limit', String(params.limit))
  if (params?.offset != null) search.set('offset', String(params.offset))
  const qs = search.toString()
  const url = `${BASE}/events${qs ? `?${qs}` : ''}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`)
  return res.json()
}

export async function getEvent (id: number): Promise<EventDetail> {
  const res = await fetch(`${BASE}/events/${id}`)
  if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`)
  return res.json()
}
