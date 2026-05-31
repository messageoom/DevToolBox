<template>
  <div class="hash-algorithm-selector">
    <div class="filter-section">
      <el-input
        v-model="searchText"
        placeholder="搜索算法..."
        clearable
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <div class="algorithm-grid">
      <el-row :gutter="12">
        <el-col
          v-for="algo in filteredAlgorithms"
          :key="algo.value"
          :xs="12"
          :sm="8"
          :md="6"
          class="algorithm-col"
        >
          <div
            :class="['algorithm-card', { active: modelValue === algo.value }]"
            @click="$emit('update:modelValue', algo.value)"
          >
            <h3 class="algorithm-name">{{ algo.label }}</h3>
            <el-tag
              :type="getTagType(algo.securityLevel)"
              size="small"
            >
              {{ algo.securityLevel }}
            </el-tag>
            <p class="algorithm-description">{{ algo.description }}</p>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { Search } from '@element-plus/icons-vue'

const ALGORITHM_DETAILS = {
  md5: { label: 'MD5', securityLevel: '低', description: '128位摘要，不推荐安全场景', type: '国际标准' },
  sha1: { label: 'SHA-1', securityLevel: '低', description: '160位摘要，已不推荐', type: '国际标准' },
  sha224: { label: 'SHA-224', securityLevel: '中', description: '224位摘要', type: '国际标准' },
  sha256: { label: 'SHA-256', securityLevel: '高', description: '256位摘要，广泛使用', type: '国际标准' },
  sha384: { label: 'SHA-384', securityLevel: '高', description: '384位摘要', type: '国际标准' },
  sha512: { label: 'SHA-512', securityLevel: '高', description: '512位摘要', type: '国际标准' },
  sha3_224: { label: 'SHA3-224', securityLevel: '高', description: 'SHA-3 224位', type: '国际标准' },
  sha3_256: { label: 'SHA3-256', securityLevel: '高', description: 'SHA-3 256位', type: '国际标准' },
  sha3_384: { label: 'SHA3-384', securityLevel: '高', description: 'SHA-3 384位', type: '国际标准' },
  sha3_512: { label: 'SHA3-512', securityLevel: '高', description: 'SHA-3 512位', type: '国际标准' },
  blake2b: { label: 'BLAKE2b', securityLevel: '高', description: '快速哈希，最多512位', type: '国际标准' },
  blake2s: { label: 'BLAKE2s', securityLevel: '高', description: '轻量哈希，最多256位', type: '国际标准' },
  sm3: { label: 'SM3', securityLevel: '高', description: '国密哈希，256位', type: '国密' },
  blake3: { label: 'BLAKE3', securityLevel: '高', description: '最新快速哈希', type: '国际标准' }
}

export default {
  name: 'HashAlgorithmCardSelector',
  components: { Search },
  props: {
    modelValue: { type: String, default: 'sha256' },
    algorithms: { type: Array, default: () => [] }
  },
  emits: ['update:modelValue'],
  data() {
    return { searchText: '' }
  },
  computed: {
    filteredAlgorithms() {
      const search = this.searchText.toLowerCase()
      return this.algorithms
        .map(name => ({ value: name, ...ALGORITHM_DETAILS[name] }))
        .filter(a => a.label && (!search || a.label.toLowerCase().includes(search) || a.value.toLowerCase().includes(search)))
    }
  },
  methods: {
    getTagType(level) {
      return level === '高' ? 'success' : level === '中' ? 'warning' : 'danger'
    }
  }
}
</script>

<style scoped>
.filter-section {
  display: flex;
  gap: var(--dt-spacing-sm);
  margin-bottom: var(--dt-spacing-md);
}

.search-input {
  max-width: 240px;
}

.algorithm-grid {
  margin-top: var(--dt-spacing-sm);
}

.algorithm-card {
  padding: var(--dt-spacing-md);
  background: var(--dt-bg-card);
  border: 2px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
  cursor: pointer;
  transition: border-color var(--dt-transition-fast), box-shadow var(--dt-transition-fast);
  text-align: center;
  margin-bottom: var(--dt-spacing-sm);
}

.algorithm-card:hover {
  border-color: var(--dt-primary);
  box-shadow: var(--dt-shadow-sm);
}

.algorithm-card.active {
  border-color: var(--dt-primary);
  background: var(--dt-primary-light);
}

.algorithm-name {
  font-size: var(--dt-font-size-base);
  font-weight: 600;
  color: var(--dt-text-primary);
  margin: 0 0 var(--dt-spacing-xs) 0;
}

.algorithm-description {
  font-size: var(--dt-font-size-xs);
  color: var(--dt-text-secondary);
  margin: var(--dt-spacing-xs) 0 0 0;
}

@media (max-width: 480px) {
  .filter-section {
    flex-direction: column;
  }
  .search-input {
    max-width: 100%;
  }
}
</style>
