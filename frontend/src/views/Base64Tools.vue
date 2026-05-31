<template>
  <ToolPage title="Base64工具" :icon="Key">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="编码" name="encode">
        <ToolSection
          input-label="输入文本"
          output-label="Base64结果"
          action-text="编码"
          :loading="encoding"
          @submit="encodeBase64"
        >
          <template #input>
            <el-input
              v-model="encodeInput"
              type="textarea"
              :rows="8"
              placeholder="请输入要编码的文本..."
              clearable
            />
          </template>
          <template #output>
            <el-input
              v-model="encodeOutput"
              type="textarea"
              :rows="8"
              readonly
              placeholder="编码结果将显示在这里..."
            />
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane label="解码" name="decode">
        <ToolSection
          input-label="输入Base64"
          output-label="解码结果"
          action-text="解码"
          :loading="decoding"
          @submit="decodeBase64"
        >
          <template #input>
            <el-input
              v-model="decodeInput"
              type="textarea"
              :rows="8"
              placeholder="请输入Base64字符串..."
              clearable
            />
          </template>
          <template #output>
            <el-input
              v-model="decodeOutput"
              type="textarea"
              :rows="8"
              readonly
              placeholder="解码结果将显示在这里..."
            />
          </template>
        </ToolSection>
      </el-tab-pane>
    </el-tabs>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Key } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'
import ToolSection from '@/components/ToolSection.vue'

export default {
  name: 'Base64Tools',
  components: {
    Key,
    ToolPage,
    ToolSection
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
