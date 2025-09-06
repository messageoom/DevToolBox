<template>
  <div class="algorithm-card-selector">
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

    <!-- 算法分类标签 -->
    <div class="category-tabs">
      <el-tabs v-model="activeCategory" @tab-change="onCategoryChange">
        <el-tab-pane 
          v-for="category in categories" 
          :key="category.value" 
          :label="category.label" 
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
      securityLevels: ['高', '中', '低'],
      algorithmTypes: ['国际标准', '国密'],
      categories: [
        { label: '非对称加密', value: 'asymmetric' },
        { label: '对称加密', value: 'symmetric' },
        { label: '哈希算法', value: 'hash' }
      ],
      algorithmDetails: {
        // 非对称加密算法
        'RSA': {
          label: 'RSA',
          description: '经典的公钥加密算法，广泛用于数据加密和数字签名',
          icon: 'Key',
          securityLevel: '高',
          type: '国际标准'
        },
        'ECC': {
          label: 'ECC',
          description: '椭圆曲线加密算法，提供与RSA相当的安全性但密钥更短',
          icon: 'Lock',
          securityLevel: '高',
          type: '国际标准'
        },
        'Ed25519': {
          label: 'Ed25519',
          description: '高效的数字签名算法，基于扭曲爱德华曲线',
          icon: 'Document',
          securityLevel: '高',
          type: '国际标准'
        },
        'SM2': {
          label: 'SM2',
          description: '国家商用密码算法，用于数字签名和密钥交换',
          icon: 'Key',
          securityLevel: '高',
          type: '国密'
        },
        
        // 对称加密算法
        'AES': {
          label: 'AES',
          description: '高级加密标准，广泛使用的对称加密算法',
          icon: 'Unlock',
          securityLevel: '高',
          type: '国际标准'
        },
        'ChaCha20': {
          label: 'ChaCha20',
          description: '高性能流加密算法，适用于移动设备',
          icon: 'Link',
          securityLevel: '高',
          type: '国际标准'
        },
        'SM4': {
          label: 'SM4',
          description: '国家商用密码算法，分组密码算法',
          icon: 'Unlock',
          securityLevel: '高',
          type: '国密'
        },
        
        // 哈希算法
        'MD5': {
          label: 'MD5',
          description: '消息摘要算法5，128位哈希函数',
          icon: 'Document',
          securityLevel: '低',
          type: '国际标准'
        },
        'SHA1': {
          label: 'SHA1',
          description: '安全哈希算法1，160位哈希函数',
          icon: 'Lock',
          securityLevel: '低',
          type: '国际标准'
        },
        'SHA256': {
          label: 'SHA256',
          description: 'SHA-2系列哈希函数，256位输出',
          icon: 'Key',
          securityLevel: '高',
          type: '国际标准'
        },
        'SHA3_256': {
          label: 'SHA3-256',
          description: 'SHA-3系列哈希函数，256位输出',
          icon: 'Key',
          securityLevel: '高',
          type: '国际标准'
        },
        'SM3': {
          label: 'SM3',
          description: '国家商用密码算法，256位密码杂凑算法',
          icon: 'Lock',
          securityLevel: '高',
          type: '国密'
        },
        'BLAKE3': {
          label: 'BLAKE3',
          description: '现代哈希函数，性能优异且安全',
          icon: 'Document',
          securityLevel: '高',
          type: '国际标准'
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
.algorithm-card-selector {
  width: 100%;
}

.filter-section {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

html.dark .filter-section {
  background-color: #2d2d2d;
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

html.dark .filter-label {
  color: #e5eaf3;
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

html.dark .algorithm-card:hover {
  box-shadow: 0 4px 12px rgba(255, 255, 255, 0.15);
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

html.dark .algorithm-name {
  color: #e5eaf3;
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

html.dark .algorithm-description {
  color: #a3a6ad;
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