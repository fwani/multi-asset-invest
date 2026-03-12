<template>
  <div class="asset-impacts">
    <p>
      <router-link :to="{ name: 'EventsList' }">← 이벤트 목록</router-link>
      <router-link :to="{ name: 'AssetsList' }" class="assets-link">지원 자산 목록</router-link>
    </p>
    <h1>자산별 영향</h1>
    <section class="filters">
      <label>
        자산 선택
        <select v-model.number="assetId" @change="load">
          <option :value="0">자산 선택</option>
          <option v-for="a in assetOptions" :key="a.id" :value="a.id">
            {{ a.symbol }} ({{ a.name }}) [{{ a.asset_type }}]
          </option>
        </select>
      </label>
      <label>자산 ID 직접 입력 <input v-model.number="assetId" type="number" min="0" placeholder="선택 또는 입력" /></label>
      <label>from_date <input v-model="fromDate" type="date" /></label>
      <label>to_date <input v-model="toDate" type="date" /></label>
      <label>limit <input v-model.number="limit" type="number" min="1" max="200" /></label>
      <button type="button" @click="load">조회</button>
      <div class="recalc-trigger">
        <button
          type="button"
          :disabled="recalcLoading"
          @click="triggerRecalc"
        >
          {{ recalcLoading ? '등록 중…' : '영향도 재분석' }}
        </button>
        <span v-if="recalcMessage" class="recalc-message">{{ recalcMessage }}</span>
        <span v-if="recalcError" class="recalc-error">{{ recalcError }}</span>
      </div>
    </section>
    <p v-if="loading">로딩 중...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="!assetId">자산을 선택하거나 ID를 입력한 뒤 조회하세요.</p>
    <p v-else-if="!items.length">영향 데이터 없음</p>
    <template v-else>
      <p>정렬: <button type="button" @click="sortBy = 'computed_at'">{{ sortBy === 'computed_at' ? '계산 시각 ▼' : '계산 시각' }}</button>
        <button type="button" @click="sortBy = 'event_id'">{{ sortBy === 'event_id' ? '이벤트 ID ▼' : '이벤트 ID' }}</button></p>
      <table>
        <thead>
          <tr>
            <th>이벤트 ID</th>
            <th>방향</th>
            <th>강도</th>
            <th>계산 시각</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="imp in sortedItems" :key="imp.id">
            <td><router-link :to="{ name: 'EventDetail', params: { id: imp.event_id } }">{{ imp.event_id }}</router-link></td>
            <td>{{ imp.direction }}</td>
            <td>{{ imp.strength ?? '-' }}</td>
            <td>{{ formatDate(imp.computed_at) }}</td>
          </tr>
        </tbody>
      </table>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getAssetImpacts, type AssetImpactItem } from '@/services/api/impacts'
import { getAssets, type AssetListItem } from '@/services/api/assets'
import { triggerWorker } from '@/services/api/worker'

const route = useRoute()
const assetId = ref<number>(0)
const assetOptions = ref<AssetListItem[]>([])
const fromDate = ref('')
const toDate = ref('')
const limit = ref(50)
const loading = ref(false)
const error = ref<string | null>(null)
const items = ref<AssetImpactItem[]>([])
const sortBy = ref<'computed_at' | 'event_id'>('computed_at')
const recalcLoading = ref(false)
const recalcMessage = ref<string | null>(null)
const recalcError = ref<string | null>(null)

async function loadAssetOptions () {
  try {
    const res = await getAssets({ limit: 500 })
    assetOptions.value = res.items
  } catch {
    assetOptions.value = []
  }
}

const sortedItems = computed(() => {
  const list = [...items.value]
  if (sortBy.value === 'computed_at') {
    list.sort((a, b) => new Date(b.computed_at).getTime() - new Date(a.computed_at).getTime())
  } else {
    list.sort((a, b) => b.event_id - a.event_id)
  }
  return list
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
  if (!assetId.value || assetId.value < 1) {
    items.value = []
    error.value = null
    return
  }
  loading.value = true
  error.value = null
  try {
    const params: { from_date?: string; to_date?: string; limit?: number } = { limit: limit.value }
    if (fromDate.value) params.from_date = fromDate.value
    if (toDate.value) params.to_date = toDate.value
    items.value = await getAssetImpacts(assetId.value, params)
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

async function triggerRecalc () {
  recalcLoading.value = true
  recalcMessage.value = null
  recalcError.value = null
  try {
    const body: { job_type: 'recalc_impacts'; from_date?: string; to_date?: string; limit?: number } = {
      job_type: 'recalc_impacts',
      limit: 200,
    }
    if (fromDate.value) body.from_date = fromDate.value
    if (toDate.value) body.to_date = toDate.value
    const res = await triggerWorker(body)
    const n = res.enqueued_count
    recalcMessage.value = n != null
      ? `${n}개 이벤트에 대한 재분석이 대기열에 등록되었습니다.`
      : '재분석이 대기열에 등록되었습니다.'
    setTimeout(() => { recalcMessage.value = null }, 5000)
  } catch (e) {
    recalcError.value = e instanceof Error ? e.message : String(e)
    setTimeout(() => { recalcError.value = null }, 5000)
  } finally {
    recalcLoading.value = false
  }
}

onMounted(async () => {
  await loadAssetOptions()
  const q = route.query.assetId
  if (q != null) {
    const id = typeof q === 'string' ? parseInt(q, 10) : Number(q)
    if (!isNaN(id) && id >= 1) {
      assetId.value = id
      await load()
    }
  } else if (assetId.value >= 1) {
    await load()
  }
})

watch(() => route.query.assetId, (q) => {
  if (q != null) {
    const id = typeof q === 'string' ? parseInt(q, 10) : Number(q)
    if (!isNaN(id) && id >= 1) assetId.value = id
  }
})
</script>

<style scoped>
.asset-impacts { padding: 1rem; }
.filters { display: flex; flex-wrap: wrap; gap: 0.5rem 1rem; align-items: center; margin-bottom: 1rem; }
.filters label { display: flex; align-items: center; gap: 0.25rem; }
table { border-collapse: collapse; }
th, td { border: 1px solid #ccc; padding: 0.25rem 0.5rem; text-align: left; }
.error { color: red; }
.assets-link { margin-left: 1rem; }
.recalc-trigger { display: flex; align-items: center; gap: 0.5rem; }
.recalc-trigger button:disabled { opacity: 0.7; cursor: not-allowed; }
.recalc-message { color: green; }
.recalc-error { color: red; }
</style>
