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

        <div class="config-section">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-select v-model="algorithm" placeholder="选择哈希算法">
                <el-option label="MD5" value="md5" />
                <el-option label="SHA-1" value="sha1" />
                <el-option label="SHA-256" value="sha256" />
                <el-option label="SHA-384" value="sha384" />
                <el-option label="SHA-512" value="sha512" />
              </el-select>
            </el-col>
            <el-col :span="12">
              <el-button type="primary" @click="generateHash" :loading="generating" style="width: 100%;">
                生成哈希
              </el-button>
            </el-col>
          </el-row>
        </div>

        <div class="output-section">
          <h4>哈希结果</h4>
          <el-input
            v-model="hashResult"
            readonly
            placeholder="哈希结果将显示在这里..."
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

export default {
  name: 'HashTools',
  components: {
    Lock
  },
  data() {
    return {
      inputText: '',
      algorithm: 'sha256',
      hashResult: '',
      generating: false
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
        ElMessage.error('哈希生成失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.generating = false
      }
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
</style>
