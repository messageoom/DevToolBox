<template>
  <div class="algorithm-card-selector">
    <!-- 搜索和筛选区域 -->
    <div class="filter-section">
      <el-input
        v-model="searchText"
        :placeholder="$t('tools.crypto.algorithmSelector.searchPlaceholder')"
        clearable
        class="search-input"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <div class="filters">
        <span class="filter-label">{{ $t('tools.crypto.algorithmSelector.securityLevel') }}</span>
        <el-checkbox-group v-model="securityLevels" class="filter-group">
          <el-checkbox label="High">{{ $t('tools.crypto.algorithmSelector.levelHigh') }}</el-checkbox>
          <el-checkbox label="Medium">{{ $t('tools.crypto.algorithmSelector.levelMedium') }}</el-checkbox>
          <el-checkbox label="Low">{{ $t('tools.crypto.algorithmSelector.levelLow') }}</el-checkbox>
        </el-checkbox-group>
        
        <span class="filter-label">{{ $t('tools.crypto.algorithmSelector.type') }}</span>
        <el-checkbox-group v-model="algorithmTypes" class="filter-group">
          <el-checkbox label="International">{{ $t('tools.crypto.algorithmSelector.international') }}</el-checkbox>
          <el-checkbox label="National">{{ $t('tools.crypto.algorithmSelector.national') }}</el-checkbox>
        </el-checkbox-group>
      </div>
    </div>

    <!-- 算法分类标签 -->
    <div class="category-tabs">
      <el-tabs v-model="activeCategory" @tab-change="onCategoryChange">
        <el-tab-pane 
          v-for="category in categories" 
          :key="category.value" 
          :label="$t(category.labelKey)" 
          :name="category.value"
        />
      </el-tabs>
    </div>

    <!-- 算法卡片网格 -->
    <div class="algorithm-grid">
      <el-row :gutter="20">
        <el-col 
          v-for="algorithm in filteredAlgorithms" 
          :key="algorithm.value" 
          :span="8" 
          class="algorithm-col"
        >
          <el-card 
            :class="['algorithm-card', { 'active': selectedAlgorithm === algorithm.value }]"
            @click="selectAlgorithm(algorithm.value)"
          >
            <div class="card-content">
              <div class="icon-wrapper">
                <el-icon class="algorithm-icon" :size="32">
                  <component :is="algorithm.icon" />
                </el-icon>
              </div>
              <div class="algorithm-info">
                <h3 class="algorithm-name">{{ $t(algorithm.labelKey) }}</h3>
                <div class="algorithm-tags">
                  <el-tag 
                    :type="getSecurityLevelTagType(algorithm.securityLevel)" 
                    size="small"
                    class="tag"
                  >
                    {{ $t('tools.crypto.algorithmSelector.securityLevel') }}{{ $t('tools.crypto.algorithmSelector.level' + algorithm.securityLevel) }}
                  </el-tag>
                  <el-tag 
                    type="info" 
                    size="small"
                    class="tag"
                  >
                    {{ $t('tools.crypto.algorithmSelector.type' + algorithm.type) }}
                  </el-tag>
                </div>
                <p class="algorithm-description">{{ $t(algorithm.descriptionKey) }}</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import {
  Lock,
  Unlock,
  Key,
  Link,
  Timer,
  Document,
  Files,
  Crop,
  Search
} from '@element-plus/icons-vue'

export default {
  name: 'AlgorithmCardSelector',
  components: {
    Lock,
    Unlock,
    Key,
    Link,
    Timer,
    Document,
    Files,
    Crop,
    Search
  },
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    category: {
      type: String,
      default: 'asymmetric'
    },
    algorithms: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['update:modelValue', 'category-change'],
  data() {
    return {
      activeCategory: this.category,
      searchText: '',
      securityLevels: ['High', 'Medium', 'Low'],
      algorithmTypes: ['International', 'National'],
      categories: [
        { labelKey: 'tools.crypto.algorithmSelector.categoryAsymmetric', value: 'asymmetric' },
        { labelKey: 'tools.crypto.algorithmSelector.categorySymmetric', value: 'symmetric' },
        { labelKey: 'tools.crypto.algorithmSelector.categoryHash', value: 'hash' }
      ],
      algorithmDetails: {
        'RSA': {
          labelKey: 'tools.crypto.algorithmSelector.rsaLabel',
          descriptionKey: 'tools.crypto.algorithmSelector.rsaDesc',
          icon: 'Key',
          securityLevel: 'High',
          type: 'International'
        },
        'ECC': {
          labelKey: 'tools.crypto.algorithmSelector.eccLabel',
          descriptionKey: 'tools.crypto.algorithmSelector.eccDesc',
          icon: 'Lock',
          securityLevel: 'High',
          type: 'International'
        },
        'Ed25519': {
          labelKey: 'tools.crypto.algorithmSelector.ed25519Label',
          descriptionKey: 'tools.crypto.algorithmSelector.ed25519Desc',
          icon: 'Document',
          securityLevel: 'High',
          type: 'International'
        },
        'SM2': {
          labelKey: 'tools.crypto.algorithmSelector.sm2Label',
          descriptionKey: 'tools.crypto.algorithmSelector.sm2Desc',
          icon: 'Key',
          securityLevel: 'High',
          type: 'National'
        },
        'AES': {
          labelKey: 'tools.crypto.algorithmSelector.aesLabel',
          descriptionKey: 'tools.crypto.algorithmSelector.aesDesc',
          icon: 'Unlock',
          securityLevel: 'High',
          type: 'International'
        },
        'ChaCha20': {
          labelKey: 'tools.crypto.algorithmSelector.chacha20Label',
          descriptionKey: 'tools.crypto.algorithmSelector.chacha20Desc',
          icon: 'Link',
          securityLevel: 'High',
          type: 'International'
        },
        'SM4': {
          labelKey: 'tools.crypto.algorithmSelector.sm4Label',
          descriptionKey: 'tools.crypto.algorithmSelector.sm4Desc',
          icon: 'Unlock',
          securityLevel: 'High',
          type: 'National'
        },
        'MD5': {
          labelKey: 'tools.crypto.algorithmSelector.md5Label',
          descriptionKey: 'tools.crypto.algorithmSelector.md5Desc',
          icon: 'Document',
          securityLevel: 'Low',
          type: 'International'
        },
        'SHA1': {
          labelKey: 'tools.crypto.algorithmSelector.sha1Label',
          descriptionKey: 'tools.crypto.algorithmSelector.sha1Desc',
          icon: 'Lock',
          securityLevel: 'Low',
          type: 'International'
        },
        'SHA256': {
          labelKey: 'tools.crypto.algorithmSelector.sha256Label',
          descriptionKey: 'tools.crypto.algorithmSelector.sha256Desc',
          icon: 'Key',
          securityLevel: 'High',
          type: 'International'
        },
        'SHA3_256': {
          labelKey: 'tools.crypto.algorithmSelector.sha3_256Label',
          descriptionKey: 'tools.crypto.algorithmSelector.sha3_256Desc',
          icon: 'Key',
          securityLevel: 'High',
          type: 'International'
        },
        'SM3': {
          labelKey: 'tools.crypto.algorithmSelector.sm3Label',
          descriptionKey: 'tools.crypto.algorithmSelector.sm3Desc',
          icon: 'Lock',
          securityLevel: 'High',
          type: 'National'
        },
        'BLAKE3': {
          labelKey: 'tools.crypto.algorithmSelector.blake3Label',
          descriptionKey: 'tools.crypto.algorithmSelector.blake3Desc',
          icon: 'Document',
          securityLevel: 'High',
          type: 'International'
        }
      }
    }
  },
  computed: {
    filteredAlgorithms() {
      console.log('AlgorithmCardSelector - algorithms prop:', this.algorithms)
      console.log('AlgorithmCardSelector - activeCategory:', this.activeCategory)
      const algorithmsInCategory = this.algorithms[this.activeCategory] || []
      console.log('AlgorithmCardSelector - algorithmsInCategory:', algorithmsInCategory)
      
      const filtered = algorithmsInCategory
        .filter(algo => this.algorithmDetails[algo])
        .filter(algo => {
          const algorithm = this.algorithmDetails[algo];

          if (this.searchText &&
              !this.$t(algorithm.labelKey).toLowerCase().includes(this.searchText.toLowerCase()) &&
              !this.$t(algorithm.descriptionKey).toLowerCase().includes(this.searchText.toLowerCase())) {
            return false;
          }
          
          // 安全级别过滤
          if (this.securityLevels.length > 0 && 
              !this.securityLevels.includes(algorithm.securityLevel)) {
            return false;
          }
          
          // 算法类型过滤
          if (this.algorithmTypes.length > 0 && 
              !this.algorithmTypes.includes(algorithm.type)) {
            return false;
          }
          
          return true;
        })
        .map(algo => ({
          value: algo,
          ...this.algorithmDetails[algo]
        }))
      
      console.log('AlgorithmCardSelector - filtered algorithms:', filtered)
      return filtered
    },
    selectedAlgorithm: {
      get() {
        return this.modelValue
      },
      set(value) {
        this.$emit('update:modelValue', value)
      }
    }
  },
  methods: {
    onCategoryChange(category) {
      this.activeCategory = category
      this.$emit('category-change', category)
    },
    selectAlgorithm(algorithm) {
      this.selectedAlgorithm = algorithm
    },
    getSecurityLevelTagType(securityLevel) {
      switch (securityLevel) {
        case 'High': return 'success';
        case 'Medium': return 'warning';
        case 'Low': return 'danger';
        default: return '';
      }
    }
  }
}
</script>

<style scoped>
.algorithm-card-selector {
  width: 100%;
}

.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.search-input {
  width: 300px;
  margin-bottom: 15px;
}

.filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.filter-label {
  font-weight: bold;
  color: #333;
}

.filter-group {
  display: flex;
  gap: 10px;
}

.category-tabs {
  margin-bottom: 20px;
}

.algorithm-grid {
  width: 100%;
}

.algorithm-col {
  margin-bottom: 20px;
}

.algorithm-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
}

.algorithm-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.algorithm-card.active {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px 10px;
}

.icon-wrapper {
  margin-bottom: 15px;
}

.algorithm-icon {
  color: #409eff;
}

.algorithm-name {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.algorithm-tags {
  display: flex;
  justify-content: center;
  gap: 5px;
  margin-bottom: 10px;
}

.algorithm-description {
  margin: 0;
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .algorithm-col {
    flex: 0 0 50%;
    max-width: 50%;
  }
  
  .filters {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>