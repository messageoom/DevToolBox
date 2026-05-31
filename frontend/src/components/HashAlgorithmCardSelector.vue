<template>
  <div class="hash-algorithm-card-selector">
    <!-- 搜索和筛选区域 -->
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
      
      <div class="filters">
        <span class="filter-label">安全级别:</span>
        <el-checkbox-group v-model="securityLevels" class="filter-group">
          <el-checkbox label="高">高</el-checkbox>
          <el-checkbox label="中">中</el-checkbox>
          <el-checkbox label="低">低</el-checkbox>
        </el-checkbox-group>
        
        <span class="filter-label">类型:</span>
        <el-checkbox-group v-model="algorithmTypes" class="filter-group">
          <el-checkbox label="国际标准">国际标准</el-checkbox>
          <el-checkbox label="国密">国密</el-checkbox>
        </el-checkbox-group>
      </div>
    </div>

    <!-- 算法卡片网格 -->
    <div class="algorithm-grid">
      <el-row :gutter="20">
        <el-col 
          v-for="algorithm in filteredAlgorithms" 
          :key="algorithm.value" 
          :span="6" 
          class="algorithm-col"
        >
          <el-card 
            :class="['algorithm-card', { 'active': selectedAlgorithm === algorithm.value }]"
            @click="selectAlgorithm(algorithm.value)"
          >
            <div class="card-content">
              <h3 class="algorithm-name">{{ algorithm.label }}</h3>
              <div class="algorithm-tags">
                <el-tag 
                  :type="getSecurityLevelTagType(algorithm.securityLevel)" 
                  size="small"
                  class="tag"
                >
                  安全级别{{ algorithm.securityLevel }}
                </el-tag>
                <el-tag 
                  type="info" 
                  size="small"
                  class="tag"
                >
                  {{ algorithm.type }}
                </el-tag>
              </div>
              <p class="algorithm-description">{{ algorithm.description }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { Search } from '@element-plus/icons-vue'

export default {
  name: 'HashAlgorithmCardSelector',
  components: {
    Search
  },
  props: {
    modelValue: {
      type: String,
      default: 'sha256'
    },
    algorithms: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue'],
  data() {
    return {
      searchText: '',
      securityLevels: ['高', '中', '低'],
      algorithmTypes: ['国际标准', '国密'],
      algorithmDetails: {
        'md5': {
          label: 'MD5',
          description: '消息摘要算法5，128位哈希函数',
          securityLevel: '低',
          type: '国际标准'
        },
        'sha1': {
          label: 'SHA-1',
          description: '安全哈希算法1，160位哈希函数',
          securityLevel: '低',
          type: '国际标准'
        },
        'sha224': {
          label: 'SHA-224',
          description: 'SHA-2系列哈希函数，224位输出',
          securityLevel: '中',
          type: '国际标准'
        },
        'sha256': {
          label: 'SHA-256',
          description: 'SHA-2系列哈希函数，256位输出',
          securityLevel: '高',
          type: '国际标准'
        },
        'sha384': {
          label: 'SHA-384',
          description: 'SHA-2系列哈希函数，384位输出',
          securityLevel: '高',
          type: '国际标准'
        },
        'sha512': {
          label: 'SHA-512',
          description: 'SHA-2系列哈希函数，512位输出',
          securityLevel: '高',
          type: '国际标准'
        },
        'sha3_224': {
          label: 'SHA3-224',
          description: 'SHA-3系列哈希函数，224位输出',
          securityLevel: '中',
          type: '国际标准'
        },
        'sha3_256': {
          label: 'SHA3-256',
          description: 'SHA-3系列哈希函数，256位输出',
          securityLevel: '高',
          type: '国际标准'
        },
        'sha3_384': {
          label: 'SHA3-384',
          description: 'SHA-3系列哈希函数，384位输出',
          securityLevel: '高',
          type: '国际标准'
        },
        'sha3_512': {
          label: 'SHA3-512',
          description: 'SHA-3系列哈希函数，512位输出',
          securityLevel: '高',
          type: '国际标准'
        },
        'blake2b': {
          label: 'BLAKE2b',
          description: 'BLAKE2b哈希函数，优化的哈希算法',
          securityLevel: '高',
          type: '国际标准'
        },
        'blake2s': {
          label: 'BLAKE2s',
          description: 'BLAKE2s哈希函数，适用于32位平台',
          securityLevel: '高',
          type: '国际标准'
        },
        'sm3': {
          label: 'SM3',
          description: '国家商用密码算法，256位密码杂凑算法',
          securityLevel: '高',
          type: '国密'
        },
        'blake3': {
          label: 'BLAKE3',
          description: '现代哈希函数，性能优异且安全',
          securityLevel: '高',
          type: '国际标准'
        }
      }
    }
  },
  computed: {
    filteredAlgorithms() {
      return this.algorithms
        .filter(algo => this.algorithmDetails[algo]) // 只显示有详细信息的算法
        .filter(algo => {
          const algorithm = this.algorithmDetails[algo];
          
          // 搜索过滤
          if (this.searchText && 
              !algorithm.label.toLowerCase().includes(this.searchText.toLowerCase()) &&
              !algorithm.description.toLowerCase().includes(this.searchText.toLowerCase())) {
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
    selectAlgorithm(algorithm) {
      this.selectedAlgorithm = algorithm
    },
    getSecurityLevelTagType(securityLevel) {
      switch (securityLevel) {
        case '高': return 'success';
        case '中': return 'warning';
        case '低': return 'danger';
        default: return '';
      }
    }
  }
}
</script>

<style scoped>
.hash-algorithm-card-selector {
  width: 100%;
  margin-bottom: 20px;
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
  padding: 15px;
}

.algorithm-name {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  text-align: center;
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
  text-align: center;
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