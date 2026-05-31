<template>
  <div class="hash-tools">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><Lock /></el-icon>
          <span>哈希工具</span>
        </div>
      </template>

      <div class="tool-section">
        <div class="input-section">
          <h4>输入文本</h4>
          <el-input
            v-model="inputText"
            type="textarea"
            :rows="6"
            placeholder="请输入要生成哈希的文本..."
            clearable
          />
        </div>

        <!-- 卡片式算法选择器 -->
        <HashAlgorithmCardSelector 
          v-model="algorithm" 
          :algorithms="availableAlgorithms"
          class="algorithm-selector"
        />

        <div class="config-section">
          <el-row :gutter="20">
            <el-col :span="24">
              <div class="action-buttons">
                <el-button type="primary" @click="generateHash" :loading="generating">
                  生成哈希
                </el-button>
                <el-button @click="verifyHash" :loading="verifying">
                  验证哈希
                </el-button>
                <el-button @click="generateHMAC" :loading="generatingHMAC">
                  生成HMAC
                </el-button>
                <el-button @click="generatePasswordHash" :loading="generatingPassword">
                  生成密码哈希
                </el-button>
              </div>
            </el-col>
          </el-row>
        </div>

        <div class="output-section">
          <h4>哈希结果</h4>
          <el-input
            v-model="hashResult"
            readonly
            placeholder="哈希结果将显示在这里..."
            type="textarea"
            :rows="4"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Lock } from '@element-plus/icons-vue'
import axios from 'axios'
import HashAlgorithmCardSelector from '@/components/HashAlgorithmCardSelector.vue'

export default {
  name: 'HashTools',
  components: {
    Lock,
    HashAlgorithmCardSelector
  },
  data() {
    return {
      inputText: '',
      algorithm: 'sha256',
      hashResult: '',
      generating: false,
      verifying: false,
      generatingHMAC: false,
      generatingPassword: false,
      availableAlgorithms: []
    }
  },
  async mounted() {
    // 获取支持的算法列表
    try {
      const response = await axios.get('/api/hash-tools/algorithms')
      if (response.data.success) {
        this.availableAlgorithms = response.data.algorithms
      }
    } catch (error) {
      console.error('获取算法列表失败:', error)
    }
  },
  methods: {
    async generateHash() {
      if (!this.inputText.trim()) {
        ElMessage.warning('请输入要生成哈希的文本')
        return
      }

      this.generating = true
      try {
        const response = await axios.post('/api/hash-tools/generate', {
          text: this.inputText,
          algorithm: this.algorithm
        })

        if (response.data.success) {
          this.hashResult = response.data.hash
          ElMessage.success('哈希生成成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('哈希生成失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.generating = false
      }
    },
    async verifyHash() {
      ElMessage.info('验证哈希功能待实现')
    },
    async generateHMAC() {
      ElMessage.info('生成HMAC功能待实现')
    },
    async generatePasswordHash() {
      ElMessage.info('生成密码哈希功能待实现')
    }
  }
}
</script>

<style scoped>
.hash-tools {
  padding: 20px;
}

.tool-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-section, .output-section {
  flex: 1;
}

.input-section h4, .output-section h4 {
  margin-bottom: 10px;
  color: #333;
  font-weight: bold;
}

.config-section {
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.action-buttons .el-button {
  flex: 1;
  min-width: 120px;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-icon {
  margin-right: 8px;
  font-size: 18px;
}

.card-header span {
  font-weight: bold;
}

.algorithm-selector {
  margin-bottom: 20px;
}
</style>