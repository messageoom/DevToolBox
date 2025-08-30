<template>
  <div class="base64-tools">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><Key /></el-icon>
          <span>Base64工具</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="编码" name="encode">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入文本</h4>
              <el-input
                v-model="encodeInput"
                type="textarea"
                :rows="8"
                placeholder="请输入要编码的文本..."
                clearable
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="encodeBase64" :loading="encoding">
                编码
              </el-button>
            </div>
            <div class="output-section">
              <h4>Base64结果</h4>
              <el-input
                v-model="encodeOutput"
                type="textarea"
                :rows="8"
                readonly
                placeholder="编码结果将显示在这里..."
              />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="解码" name="decode">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入Base64</h4>
              <el-input
                v-model="decodeInput"
                type="textarea"
                :rows="8"
                placeholder="请输入Base64字符串..."
                clearable
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="decodeBase64" :loading="decoding">
                解码
              </el-button>
            </div>
            <div class="output-section">
              <h4>解码结果</h4>
              <el-input
                v-model="decodeOutput"
                type="textarea"
                :rows="8"
                readonly
                placeholder="解码结果将显示在这里..."
              />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Key } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'Base64Tools',
  components: {
    Key
  },
  data() {
    return {
      activeTab: 'encode',
      encodeInput: '',
      encodeOutput: '',
      encoding: false,
      decodeInput: '',
      decodeOutput: '',
      decoding: false
    }
  },
  methods: {
    async encodeBase64() {
      if (!this.encodeInput.trim()) {
        ElMessage.warning('请输入要编码的文本')
        return
      }

      this.encoding = true
      try {
        const response = await axios.post('/api/base64-tools/encode', {
          text: this.encodeInput
        })

        if (response.data.success) {
          this.encodeOutput = response.data.encoded
          ElMessage.success('编码成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('编码失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.encoding = false
      }
    },

    async decodeBase64() {
      if (!this.decodeInput.trim()) {
        ElMessage.warning('请输入Base64字符串')
        return
      }

      this.decoding = true
      try {
        const response = await axios.post('/api/base64-tools/decode', {
          encoded_text: this.decodeInput
        })

        if (response.data.success) {
          this.decodeOutput = response.data.decoded
          ElMessage.success('解码成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('解码失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.decoding = false
      }
    }
  }
}
</script>

<style scoped>
.base64-tools {
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

.action-section {
  text-align: center;
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
