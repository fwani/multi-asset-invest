<template>
  <div class="assets-list">
    <p><router-link :to="{ name: 'Home' }">← 홈</router-link></p>
    <h1>지원 자산 목록</h1>
    <section class="add-asset">
      <button type="button" @click="showAddForm = !showAddForm">
        {{ showAddForm ? '취소' : '자산 추가' }}
      </button>
      <form v-if="showAddForm" class="add-form" @submit.prevent="submitAdd">
        <label>심볼 <input v-model="form.symbol" type="text" required placeholder="e.g. AAPL" /></label>
        <label>이름 <input v-model="form.name" type="text" required placeholder="자산 이름" /></label>
        <label>유형
          <select v-model="form.asset_type" required>
            <option value="stock">주식</option>
            <option value="crypto">암호화폐</option>
            <option value="fx">외환</option>
            <option value="bond">채권</option>
            <option value="gold">금</option>
            <option value="commodity">원자재</option>
          </select>
        </label>
        <label>거래소 <input v-model="form.exchange" type="text" placeholder="선택" /></label>
        <label>통화 ID <input v-model.number="form.currency_id" type="number" placeholder="선택" /></label>
        <label>섹터 ID <input v-model.number="form.sector_id" type="number" placeholder="선택" /></label>
        <label>국가 ID <input v-model.number="form.country_id" type="number" placeholder="선택" /></label>
        <button type="submit" :disabled="addLoading">추가</button>
        <span v-if="addError" class="error">{{ addError }}</span>
      </form>
    </section>
    <section class="filters">
      <label>
        자산 유형
        <select v-model="assetType">
          <option value="">전체</option>
          <option value="stock">주식</option>
          <option value="crypto">암호화폐</option>
          <option value="fx">외환</option>
          <option value="bond">채권</option>
          <option value="gold">금</option>
          <option value="commodity">원자재</option>
        </select>
      </label>
      <label>limit <input v-model.number="limit" type="number" min="1" max="500" /></label>
      <button type="button" @click="load">조회</button>
    </section>
    <p v-if="loading">로딩 중...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <template v-else-if="data">
      <p>총 {{ data.total }}건</p>
      <table v-if="data.items.length">
        <thead>
          <tr>
            <th>ID</th>
            <th>심볼</th>
            <th>이름</th>
            <th>유형</th>
            <th>거래소</th>
            <th>자산별 영향</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="a in data.items" :key="a.id">
            <td>{{ a.id }}</td>
            <td>{{ a.symbol }}</td>
            <td>{{ a.name }}</td>
            <td>{{ a.asset_type }}</td>
            <td>{{ a.exchange ?? '-' }}</td>
            <td>
              <router-link :to="{ name: 'AssetImpacts', query: { assetId: a.id } }">
                영향 보기
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else>자산 데이터 없음</p>
    </template>
    <p v-else>조회 버튼을 눌러 목록을 불러오세요.</p>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getAssets, createAsset, type AssetListResponse, type AssetListParams } from '@/services/api/assets'

const assetType = ref('')
const limit = ref(100)
const loading = ref(false)
const error = ref<string | null>(null)
const data = ref<AssetListResponse | null>(null)

const showAddForm = ref(false)
const addLoading = ref(false)
const addError = ref<string | null>(null)
const form = reactive({
  symbol: '',
  name: '',
  asset_type: 'stock',
  exchange: '' as string,
  currency_id: null as number | null,
  sector_id: null as number | null,
  country_id: null as number | null,
})

async function load () {
  loading.value = true
  error.value = null
  try {
    const params: AssetListParams = { limit: limit.value }
    if (assetType.value) params.asset_type = assetType.value
    data.value = await getAssets(params)
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

async function submitAdd () {
  addError.value = null
  addLoading.value = true
  try {
    const num = (v: number | null) => (v != null && !Number.isNaN(v) ? v : null)
    await createAsset({
      symbol: form.symbol.trim(),
      name: form.name.trim(),
      asset_type: form.asset_type,
      exchange: form.exchange.trim() || null,
      currency_id: num(form.currency_id),
      sector_id: num(form.sector_id),
      country_id: num(form.country_id),
    })
    showAddForm.value = false
    form.symbol = ''
    form.name = ''
    form.asset_type = 'stock'
    form.exchange = ''
    form.currency_id = null
    form.sector_id = null
    form.country_id = null
    await load()
  } catch (e) {
    addError.value = e instanceof Error ? e.message : String(e)
  } finally {
    addLoading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.assets-list { padding: 1rem; }
.add-asset { margin-bottom: 1rem; }
.add-form { display: flex; flex-wrap: wrap; gap: 0.5rem 1rem; align-items: center; margin-top: 0.5rem; padding: 0.5rem; border: 1px solid #eee; }
.add-form label { display: flex; align-items: center; gap: 0.25rem; }
.filters { display: flex; flex-wrap: wrap; gap: 0.5rem 1rem; align-items: center; margin-bottom: 1rem; }
.filters label { display: flex; align-items: center; gap: 0.25rem; }
table { border-collapse: collapse; }
th, td { border: 1px solid #ccc; padding: 0.25rem 0.5rem; text-align: left; }
.error { color: red; }
</style>
