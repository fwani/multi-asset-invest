/**
 * Worker trigger API client (POST /api/v1/worker/trigger).
 * 수동 크롤·파이프라인 트리거.
 */

const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export interface WorkerTriggerRequest {
  job_type?: 'crawl_and_extract' | 'event_created'
  event_id?: number
}

export interface WorkerTriggerResponse {
  ok: boolean
  job_type: string
  message: string
}

export async function triggerWorker (body?: WorkerTriggerRequest): Promise<WorkerTriggerResponse> {
  const res = await fetch(`${BASE}/worker/trigger`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `HTTP ${res.status}`)
  }
  return res.json()
}
