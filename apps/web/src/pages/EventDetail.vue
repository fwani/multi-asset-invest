<template>
  <div class="event-detail">
    <p><router-link :to="{ name: 'EventsList' }">← 목록</router-link></p>
    <p v-if="loading">로딩 중...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <template v-else-if="event">
      <h1>이벤트 #{{ event.id }}</h1>
      <dl>
        <dt>event_type</dt>
        <dd>{{ event.event_type }}</dd>
        <dt>country_id</dt>
        <dd>{{ event.country_id ?? '-' }}</dd>
        <dt>actor</dt>
        <dd>{{ event.actor ?? '-' }}</dd>
        <dt>impact_type</dt>
        <dd>{{ event.impact_type ?? '-' }}</dd>
        <dt>occurred_at</dt>
        <dd>{{ formatDate(event.occurred_at) }}</dd>
        <dt>extracted_at</dt>
        <dd>{{ formatDate(event.extracted_at) }}</dd>
        <dt>confidence</dt>
        <dd>{{ event.confidence ?? '-' }}</dd>
        <dt>source_summary</dt>
        <dd>{{ event.source_summary ?? '-' }}</dd>
      </dl>
      <section v-if="event.source" class="source">
        <h2>출처 (뉴스)</h2>
        <dl>
          <dt>source</dt>
          <dd>{{ event.source.source }}</dd>
          <dt>title</dt>
          <dd>{{ event.source.title ?? '-' }}</dd>
          <dt>url</dt>
          <dd><a :href="event.source.url ?? '#'" target="_blank" rel="noopener">{{ event.source.url ?? '-' }}</a></dd>
        </dl>
      </section>
      <section class="impacts">
        <h2>자산 영향</h2>
        <p v-if="impactsLoading">로딩 중...</p>
        <p v-else-if="impactsError" class="error">{{ impactsError }}</p>
        <p v-else-if="!impacts.length">영향 데이터 없음</p>
        <table v-else>
          <thead>
            <tr>
              <th>자산 ID</th>
              <th>방향</th>
              <th>강도</th>
              <th>계산 시각</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="imp in impacts" :key="imp.id">
              <td>{{ imp.asset_id }}</td>
              <td>{{ imp.direction }}</td>
              <td>{{ imp.strength ?? '-' }}</td>
              <td>{{ formatDate(imp.computed_at) }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getEvent, type EventDetail as T } from '@/services/api/events'
import { getEventImpacts, type AssetImpactItem } from '@/services/api/impacts'

const route = useRoute()
const loading = ref(false)
const error = ref<string | null>(null)
const event = ref<T | null>(null)
const impacts = ref<AssetImpactItem[]>([])
const impactsLoading = ref(false)
const impactsError = ref<string | null>(null)

const id = computed(() => Number(route.params.id))

function formatDate (iso: string): string {
  if (!iso) return '-'
  try {
    return new Date(iso).toLocaleString('ko-KR')
  } catch {
    return iso
  }
}

async function load () {
  if (!id.value || Number.isNaN(id.value)) {
    error.value = 'Invalid id'
    return
  }
  loading.value = true
  error.value = null
  try {
    event.value = await getEvent(id.value)
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

async function loadImpacts () {
  if (!id.value || Number.isNaN(id.value)) return
  impactsLoading.value = true
  impactsError.value = null
  try {
    impacts.value = await getEventImpacts(id.value)
  } catch (e) {
    impactsError.value = e instanceof Error ? e.message : String(e)
  } finally {
    impactsLoading.value = false
  }
}

onMounted(load)
watch(id, () => { load(); loadImpacts() }, { immediate: false })
onMounted(loadImpacts)
</script>

<style scoped>
.event-detail { padding: 1rem; }
dl { display: grid; grid-template-columns: auto 1fr; gap: 0.25rem 1rem; }
dt { font-weight: 600; }
.source { margin-top: 1.5rem; }
.impacts { margin-top: 1.5rem; }
.impacts table { border-collapse: collapse; }
.impacts th, .impacts td { border: 1px solid #ccc; padding: 0.25rem 0.5rem; text-align: left; }
.error { color: red; }
</style>
