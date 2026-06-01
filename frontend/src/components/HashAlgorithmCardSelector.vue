<template>
  <div class="hash-algorithm-selector">
    <div class="filter-section">
      <el-input
        v-model="searchText"
        :placeholder="$t('tools.hash.algorithmSelector.searchPlaceholder')"
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
    algorithmDetails() {
      return {
        md5: { label: 'MD5', securityLevel: this.$t('tools.hash.algorithmSelector.securityLow'), description: this.$t('tools.hash.algorithmSelector.descMd5'), type: this.$t('tools.hash.algorithmSelector.typeInternational') },
        sha1: { label: 'SHA-1', securityLevel: this.$t('tools.hash.algorithmSelector.securityLow'), description: this.$t('tools.hash.algorithmSelector.descSha1'), type: this.$t('tools.hash.algorithmSelector.typeInternational') },
        sha224: { label: 'SHA-224', securityLevel: this.$t('tools.hash.algorithmSelector.securityMedium'), description: this.$t('tools.hash.algorithmSelector.descSha224'), type: this.$t('tools.hash.algorithmSelector.typeInternational') },
        sha256: { label: 'SHA-256', securityLevel: this.$t('tools.hash.algorithmSelector.securityHigh'), description: this.$t('tools.hash.algorithmSelector.descSha256'), type: this.$t('tools.hash.algorithmSelector.typeInternational') },
        sha384: { label: 'SHA-384', securityLevel: this.$t('tools.hash.algorithmSelector.securityHigh'), description: this.$t('tools.hash.algorithmSelector.descSha384'), type: this.$t('tools.hash.algorithmSelector.typeInternational') },
        sha512: { label: 'SHA-512', securityLevel: this.$t('tools.hash.algorithmSelector.securityHigh'), description: this.$t('tools.hash.algorithmSelector.descSha512'), type: this.$t('tools.hash.algorithmSelector.typeInternational') },
        sha3_224: { label: 'SHA3-224', securityLevel: this.$t('tools.hash.algorithmSelector.securityHigh'), description: this.$t('tools.hash.algorithmSelector.descSha3_224'), type: this.$t('tools.hash.algorithmSelector.typeInternational') },
        sha3_256: { label: 'SHA3-256', securityLevel: this.$t('tools.hash.algorithmSelector.securityHigh'), description: this.$t('tools.hash.algorithmSelector.descSha3_256'), type: this.$t('tools.hash.algorithmSelector.typeInternational') },
        sha3_384: { label: 'SHA3-384', securityLevel: this.$t('tools.hash.algorithmSelector.securityHigh'), description: this.$t('tools.hash.algorithmSelector.descSha3_384'), type: this.$t('tools.hash.algorithmSelector.typeInternational') },
        sha3_512: { label: 'SHA3-512', securityLevel: this.$t('tools.hash.algorithmSelector.securityHigh'), description: this.$t('tools.hash.algorithmSelector.descSha3_512'), type: this.$t('tools.hash.algorithmSelector.typeInternational') },
        blake2b: { label: 'BLAKE2b', securityLevel: this.$t('tools.hash.algorithmSelector.securityHigh'), description: this.$t('tools.hash.algorithmSelector.descBlake2b'), type: this.$t('tools.hash.algorithmSelector.typeInternational') },
        blake2s: { label: 'BLAKE2s', securityLevel: this.$t('tools.hash.algorithmSelector.securityHigh'), description: this.$t('tools.hash.algorithmSelector.descBlake2s'), type: this.$t('tools.hash.algorithmSelector.typeInternational') },
        sm3: { label: 'SM3', securityLevel: this.$t('tools.hash.algorithmSelector.securityHigh'), description: this.$t('tools.hash.algorithmSelector.descSm3'), type: this.$t('tools.hash.algorithmSelector.typeNational') },
        blake3: { label: 'BLAKE3', securityLevel: this.$t('tools.hash.algorithmSelector.securityHigh'), description: this.$t('tools.hash.algorithmSelector.descBlake3'), type: this.$t('tools.hash.algorithmSelector.typeInternational') }
      }
    },
    filteredAlgorithms() {
      const search = this.searchText.toLowerCase()
      return this.algorithms
        .map(name => ({ value: name, ...this.algorithmDetails[name] }))
        .filter(a => a.label && (!search || a.label.toLowerCase().includes(search) || a.value.toLowerCase().includes(search)))
    }
  },
  methods: {
    getTagType(level) {
      const high = this.$t('tools.hash.algorithmSelector.securityHigh')
      const medium = this.$t('tools.hash.algorithmSelector.securityMedium')
      return level === high ? 'success' : level === medium ? 'warning' : 'danger'
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
