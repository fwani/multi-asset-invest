/**
 * Crawl sources API client (FR-002-2). GET/POST/PATCH/DELETE /api/v1/crawl-sources.
 */

const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export interface CrawlSourceItem {
  id: number
  base_url: string
  source_name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CrawlSourceListResponse {
  items: CrawlSourceItem[]
  total: number
}

export interface CrawlSourceCreate {
  base_url: string
  source_name: string
  is_active?: boolean
}

export interface CrawlSourceUpdate {
  base_url?: string
  source_name?: string
  is_active?: boolean
}

export async function getCrawlSources (params?: {
  is_active?: boolean
  limit?: number
  offset?: number
}): Promise<CrawlSourceListResponse> {
  const search = new URLSearchParams()
  if (params?.is_active != null) search.set('is_active', String(params.is_active))
  if (params?.limit != null) search.set('limit', String(params.limit))
  if (params?.offset != null) search.set('offset', String(params.offset))
  const qs = search.toString()
  const url = `${BASE}/crawl-sources${qs ? `?${qs}` : ''}`
  const res = await fetch(url)
  if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`)
  return res.json()
}

export async function getCrawlSource (id: number): Promise<CrawlSourceItem> {
  const res = await fetch(`${BASE}/crawl-sources/${id}`)
  if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`)
  return res.json()
}

export async function createCrawlSource (body: CrawlSourceCreate): Promise<CrawlSourceItem> {
  const res = await fetch(`${BASE}/crawl-sources`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`)
  return res.json()
}

export async function updateCrawlSource (id: number, body: CrawlSourceUpdate): Promise<CrawlSourceItem> {
  const res = await fetch(`${BASE}/crawl-sources/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`)
  return res.json()
}

export async function deleteCrawlSource (id: number): Promise<void> {
  const res = await fetch(`${BASE}/crawl-sources/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error(await res.text() || `HTTP ${res.status}`)
}
