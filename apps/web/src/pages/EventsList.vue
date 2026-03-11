<template>
  <div class="events-list">
    <h1>이벤트 목록</h1>

    <div class="worker-trigger">
      <button
        type="button"
        :disabled="triggerLoading"
        @click="runCrawl"
      >
        {{ triggerLoading ? '실행 중…' : '수동 크롤 실행' }}
      </button>
      <router-link to="/crawl-sources" class="crawl-sources-link">수집 소스 설정</router-link>
      <span v-if="triggerMessage" class="trigger-message">{{ triggerMessage }}</span>
      <span v-if="triggerError" class="trigger-error">{{ triggerError }}</span>
    </div>

    <form class="filters" @submit.prevent="load">
      <label>
        유형
        <input v-model="filters.type" type="text" placeholder="event_type" />
      </label>
      <label>
        국가 ID
        <input v-model.number="filters.country" type="number" placeholder="country_id" />
      </label>
      <label>
        from_date
        <input v-model="filters.from_date" type="datetime-local" />
      </label>
      <label>
        to_date
        <input v-model="filters.to_date" type="datetime-local" />
      </label>
      <label>
        limit
        <input v-model.number="filters.limit" type="number" min="1" max="200" />
      </label>
      <button type="submit">조회</button>
    </form>

    <p v-if="loading">로딩 중...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <template v-else>
      <p>총 {{ data?.total ?? 0 }}건</p>
      <ul class="items">
        <li v-for="e in data?.items" :key="e.id" class="item">
          <router-link :to="{ name: 'EventDetail', params: { id: e.id } }">
            [{{ e.event_type }}] {{ e.source_summary?.slice(0, 60) ?? '-' }}
            ({{ formatDate(e.occurred_at) }})
          </router-link>
        </li>
      </ul>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getEvents, type EventListResponse, type EventListParams } from '@/services/api/events'
import { triggerWorker } from '@/services/api/worker'

const loading = ref(false)
const error = ref<string | null>(null)
const data = ref<EventListResponse | null>(null)

const triggerLoading = ref(false)
const triggerMessage = ref<string | null>(null)
const triggerError = ref<string | null>(null)

const filters = reactive<EventListParams>({
  type: '',
  country: undefined,
  from_date: undefined,
  to_date: undefined,
  limit: 50,
  offset: 0,
})

function formatDate (iso: string): string {
  if (!iso) return '-'
  try {
    return new Date(iso).toLocaleString('ko-KR')
  } catch {
    return iso
  }
}

async function load () {
  loading.value = true
  error.value = null
  try {
    const params: EventListParams = {
      limit: filters.limit ?? 50,
      offset: filters.offset ?? 0,
    }
    if (filters.type) params.type = filters.type
    if (filters.country != null) params.country = filters.country
    if (filters.from_date) params.from_date = filters.from_date
    if (filters.to_date) params.to_date = filters.to_date
    data.value = await getEvents(params)
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

async function runCrawl () {
  triggerLoading.value = true
  triggerMessage.value = null
  triggerError.value = null
  try {
    const res = await triggerWorker({ job_type: 'crawl_and_extract' })
    triggerMessage.value = res.message ?? '작업이 대기열에 등록되었습니다.'
    setTimeout(() => { triggerMessage.value = null }, 5000)
    await load()
  } catch (e) {
    triggerError.value = e instanceof Error ? e.message : String(e)
    setTimeout(() => { triggerError.value = null }, 5000)
  } finally {
    triggerLoading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.events-list { padding: 1rem; }
.worker-trigger { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; }
.worker-trigger button:disabled { opacity: 0.7; cursor: not-allowed; }
.crawl-sources-link { margin-left: 0.5rem; }
.trigger-message { color: green; }
.trigger-error { color: red; }
.filters { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; align-items: flex-end; }
.filters label { display: flex; flex-direction: column; }
.filters input { margin-top: 0.25rem; }
.error { color: red; }
.items { list-style: none; padding: 0; }
.item { margin: 0.5rem 0; }
.item a { color: inherit; }
</style>
