<script setup>
import { ref, computed, toValue, watchEffect, onMounted } from 'vue'
import { useData, withBase } from 'vitepress'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  paramsPath: {
    type: String,
    default: ''
  }
})

const { lang } = useData()
const search = ref('')
const internalData = ref([])
const loading = ref(false)
const error = ref(null)

const loadData = async () => {
  const path = toValue(props.paramsPath)
  
  if (path) {
    loading.value = true
    error.value = null
    try {
      // Add .json extension if missing
      const fullPath = path.endsWith('.json') ? path : `${path}.json`
      
      if (typeof window !== 'undefined') {
          // Client-side fetch
          const res = await fetch(withBase(`/metadata/params/${fullPath}`))
          if (!res.ok) {
            throw new Error(`Failed to load params: ${res.status} ${res.statusText}`)
          }
          const json = await res.json()
          internalData.value = json.params || []
      } else {
          // SSR build time: try to read file directly using fs
          // This block is only executed in Node.js environment during build
          try {
              // Dynamic import to avoid bundling fs in client build
              const fs = await import('fs')
              const p = await import('path')
              // Assume we are in doc root during build (e.g. e:\develop\bio_analyse\doc)
              // The params are in public/metadata/params relative to doc root
              const filePath = p.resolve(process.cwd(), 'public/metadata/params', fullPath)
              if (fs.existsSync(filePath)) {
                  const content = fs.readFileSync(filePath, 'utf-8')
                  const json = JSON.parse(content)
                  internalData.value = json.params || []
              }
          } catch (ssrError) {
              // Ignore SSR errors, client will fetch
          }
      }
    } catch (e) {
      console.error(`Error loading params from ${path}:`, e)
      error.value = e
      internalData.value = []
    } finally {
      loading.value = false
    }
  } else {
    // If no path provided, use data prop
    internalData.value = props.data || []
  }
}

// Initial load
if (typeof window === 'undefined') {
    // SSR: execute immediately
    loadData()
} else {
    // Client: execute on mount to avoid hydration mismatch if possible, 
    // or use watchEffect to be reactive
    watchEffect(() => {
        loadData()
    })
}

const currentLang = computed(() => {
  return (lang.value || '').startsWith('zh') ? 'zh' : 'en'
})

const filteredParams = computed(() => {
  if (!search.value) return internalData.value
  const query = search.value.toLowerCase()
  return internalData.value.filter(param => {
    const name = param.name || ''
    const alias = param.alias || ''
    
    let desc = ''
    if (param.description) {
      if (typeof param.description === 'object') {
        desc = param.description[currentLang.value] || param.description.en || ''
      } else {
        desc = String(param.description)
      }
    }
    
    return name.toLowerCase().includes(query) || 
           alias.toLowerCase().includes(query) || 
           desc.toLowerCase().includes(query)
  })
})

const labels = computed(() => {
  return currentLang.value === 'zh' 
    ? { name: '参数名', type: '类型', required: '必填', default: '默认值', description: '描述', search: '搜索参数...', loading: '加载中...', error: '加载失败' }
    : { name: 'Name', type: 'Type', required: 'Required', default: 'Default', description: 'Description', search: 'Search params...', loading: 'Loading...', error: 'Failed to load' }
})
</script>

<template>
  <div class="param-table-container">
    <div v-if="loading" class="loading-state">{{ labels.loading }}</div>
    <div v-else-if="error" class="error-state">{{ labels.error }}: {{ error.message }}</div>
    
    <template v-else>
      <div class="search-box" v-if="internalData.length > 0">
        <input 
          v-model="search" 
          type="text" 
          :placeholder="labels.search"
          class="search-input"
        />
      </div>
      
      <div class="table-wrapper" v-if="internalData.length > 0">
        <table class="param-table">
          <thead>
            <tr>
              <th width="20%">{{ labels.name }}</th>
              <th width="15%">{{ labels.type }}</th>
              <th width="10%">{{ labels.required }}</th>
              <th width="15%">{{ labels.default }}</th>
              <th width="40%">{{ labels.description }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(param, index) in filteredParams" :key="index">
              <td>
                <div class="param-name">{{ param.name }}</div>
                <div v-if="param.alias" class="param-alias">alias: {{ param.alias }}</div>
              </td>
              <td><code>{{ param.type }}</code></td>
              <td>
                <span v-if="param.required" class="badge required">Yes</span>
                <span v-else class="badge optional">No</span>
              </td>
              <td>
                <code v-if="param.default !== undefined && param.default !== null && param.default !== 'None'">{{ param.default }}</code>
                <span v-else>-</span>
              </td>
              <td class="description">
                {{ param.description ? (param.description[currentLang] || param.description.en || param.description) : '-' }}
              </td>
            </tr>
            <tr v-if="filteredParams.length === 0">
              <td colspan="5" class="no-data">No parameters found</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="no-data-state">
        No parameters available.
      </div>
    </template>
  </div>
</template>

<style scoped>
.param-table-container {
  margin: 1rem 0;
}
.loading-state, .error-state, .no-data-state {
  padding: 1rem;
  color: var(--vp-c-text-2);
  font-style: italic;
}
.error-state {
  color: var(--vp-c-danger);
}
.search-box {
  margin-bottom: 1rem;
}
.search-input {
  width: 100%;
  max-width: 300px;
  padding: 0.5rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg-alt);
  color: var(--vp-c-text-1);
}
.table-wrapper {
  overflow-x: auto;
}
.param-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9em;
}
.param-table th, .param-table td {
  border: 1px solid var(--vp-c-divider);
  padding: 0.75rem;
  text-align: left;
}
.param-table th {
  background: var(--vp-c-bg-alt);
  font-weight: 600;
}
.param-name {
  font-weight: 600;
  color: var(--vp-c-brand);
}
.param-alias {
  font-size: 0.85em;
  color: var(--vp-c-text-2);
  margin-top: 0.25rem;
}
.badge {
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8em;
  font-weight: 600;
}
.badge.required {
  background: var(--vp-c-danger-soft);
  color: var(--vp-c-danger-text);
}
.badge.optional {
  background: var(--vp-c-default-soft);
  color: var(--vp-c-text-2);
}
code {
  background: var(--vp-c-bg-alt);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: var(--vp-font-family-mono);
  font-size: 0.9em;
}
.description {
  white-space: pre-wrap;
}
.no-data {
  text-align: center;
  color: var(--vp-c-text-2);
  padding: 2rem !important;
}
</style>
