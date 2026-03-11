<template>
  <div class="crawl-sources">
    <h1>수집 소스 설정 (관리자)</h1>
    <p class="description">크롤 대상 URL·소스 이름을 등록·수정·비활성화합니다. 워커는 활성 소스만 수집합니다.</p>

    <form class="add-form" @submit.prevent="createSource">
      <label>
        base_url
        <input v-model="newItem.base_url" type="url" placeholder="https://example.com" required />
      </label>
      <label>
        source_name
        <input v-model="newItem.source_name" type="text" placeholder="소스 이름" required />
      </label>
      <label class="checkbox">
        <input v-model="newItem.is_active" type="checkbox" />
        활성
      </label>
      <button type="submit" :disabled="createLoading">추가</button>
    </form>

    <p v-if="loading">로딩 중...</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <template v-else>
      <p>총 {{ data?.total ?? 0 }}건</p>
      <table class="sources-table">
        <thead>
          <tr>
            <th>id</th>
            <th>base_url</th>
            <th>source_name</th>
            <th>활성</th>
            <th>수정</th>
            <th>삭제</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in data?.items" :key="s.id">
            <td>{{ s.id }}</td>
            <td>{{ s.base_url }}</td>
            <td>{{ s.source_name }}</td>
            <td>
              <button
                type="button"
                class="toggle"
                :disabled="updateLoading === s.id"
                @click="toggleActive(s)"
              >
                {{ s.is_active ? 'ON' : 'OFF' }}
              </button>
            </td>
            <td>
              <button type="button" @click="startEdit(s)">수정</button>
            </td>
            <td>
              <button type="button" class="danger" :disabled="deleteLoading === s.id" @click="deleteSource(s.id)">
                삭제
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </template>

    <div v-if="editing" class="edit-modal">
      <h3>수정</h3>
      <form @submit.prevent="submitEdit">
        <label>base_url <input v-model="editForm.base_url" type="url" required /></label>
        <label>source_name <input v-model="editForm.source_name" type="text" required /></label>
        <label class="checkbox"><input v-model="editForm.is_active" type="checkbox" /> 활성</label>
        <div class="actions">
          <button type="submit" :disabled="editLoading">저장</button>
          <button type="button" @click="editing = null">취소</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import {
  getCrawlSources,
  createCrawlSource,
  updateCrawlSource,
  deleteCrawlSource,
  type CrawlSourceItem,
  type CrawlSourceListResponse,
} from '@/services/api/crawlSources'

const loading = ref(false)
const error = ref<string | null>(null)
const data = ref<CrawlSourceListResponse | null>(null)

const newItem = reactive({ base_url: '', source_name: '', is_active: true })
const createLoading = ref(false)
const updateLoading = ref<number | null>(null)
const deleteLoading = ref<number | null>(null)
const editing = ref<CrawlSourceItem | null>(null)
const editForm = reactive({ base_url: '', source_name: '', is_active: true })
const editLoading = ref(false)

async function load () {
  loading.value = true
  error.value = null
  try {
    data.value = await getCrawlSources({ limit: 100 })
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loading.value = false
  }
}

async function createSource () {
  createLoading.value = true
  error.value = null
  try {
    await createCrawlSource({
      base_url: newItem.base_url,
      source_name: newItem.source_name,
      is_active: newItem.is_active,
    })
    newItem.base_url = ''
    newItem.source_name = ''
    newItem.is_active = true
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    createLoading.value = false
  }
}

function startEdit (s: CrawlSourceItem) {
  editing.value = s
  editForm.base_url = s.base_url
  editForm.source_name = s.source_name
  editForm.is_active = s.is_active
}

async function submitEdit () {
  if (!editing.value) return
  editLoading.value = true
  error.value = null
  try {
    await updateCrawlSource(editing.value.id, {
      base_url: editForm.base_url,
      source_name: editForm.source_name,
      is_active: editForm.is_active,
    })
    editing.value = null
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    editLoading.value = false
  }
}

async function toggleActive (s: CrawlSourceItem) {
  updateLoading.value = s.id
  error.value = null
  try {
    await updateCrawlSource(s.id, { is_active: !s.is_active })
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    updateLoading.value = null
  }
}

async function deleteSource (id: number) {
  deleteLoading.value = id
  error.value = null
  try {
    await deleteCrawlSource(id)
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    deleteLoading.value = null
  }
}

onMounted(load)
</script>

<style scoped>
.crawl-sources { padding: 1rem; }
.description { color: #666; margin-bottom: 1rem; }
.add-form { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; align-items: flex-end; }
.add-form label { display: flex; flex-direction: column; }
.add-form .checkbox { flex-direction: row; align-items: center; }
.error { color: red; }
.sources-table { width: 100%; border-collapse: collapse; }
.sources-table th, .sources-table td { border: 1px solid #ddd; padding: 0.5rem; text-align: left; }
.sources-table th { background: #f5f5f5; }
.toggle { font-size: 0.85rem; }
.danger { color: #c00; }
.edit-modal { position: fixed; inset: 0; background: rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; }
.edit-modal form { background: #fff; padding: 1.5rem; border-radius: 8px; min-width: 320px; }
.edit-modal label { display: block; margin-bottom: 0.5rem; }
.edit-modal input[type="text"], .edit-modal input[type="url"] { width: 100%; }
.edit-modal .checkbox { display: flex; align-items: center; }
.edit-modal .actions { margin-top: 1rem; display: flex; gap: 0.5rem; }
</style>
