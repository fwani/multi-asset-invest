<template>
  <div class="asset-impacts">
    <p><router-link :to="{ name: 'EventsList' }">← 이벤트 목록</router-link></p>
    <h1>자산별 영향</h1>
    <section class="filters">
      <label>자산 ID <input v-model.number="assetId" type="number" min="1" /></label>
      <label>from_date <input v-model="fromDate" type="date" /></label>
      <label>to_date <input v-model="toDate" type="date" /></label>
      <label>limit <input v-model.number="limit" type="number" min="1" max="200" /></label>
      <button type="button" @click="load">조회</button>
    </section>
    <p v-if="loading">로딩 중...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else-if="!assetId">자산 ID를 입력한 뒤 조회하세요.</p>
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
import { ref, computed, onMounted } from 'vue'
import { getAssetImpacts, type AssetImpactItem } from '@/services/api/impacts'

const assetId = ref<number>(1)
const fromDate = ref('')
const toDate = ref('')
const limit = ref(50)
const loading = ref(false)
const error = ref<string | null>(null)
const items = ref<AssetImpactItem[]>([])
const sortBy = ref<'computed_at' | 'event_id'>('computed_at')

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
    error.value = '자산 ID는 1 이상이어야 합니다.'
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

onMounted(() => { if (assetId.value >= 1) load() })
</script>

<style scoped>
.asset-impacts { padding: 1rem; }
.filters { display: flex; flex-wrap: wrap; gap: 0.5rem 1rem; align-items: center; margin-bottom: 1rem; }
.filters label { display: flex; align-items: center; gap: 0.25rem; }
table { border-collapse: collapse; }
th, td { border: 1px solid #ccc; padding: 0.25rem 0.5rem; text-align: left; }
.error { color: red; }
</style>
