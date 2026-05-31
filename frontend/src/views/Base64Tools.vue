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

      <el-tab-pane label="URL安全编码" name="url-safe-encode">
        <ToolSection
          input-label="输入文本"
          output-label="URL安全Base64结果"
          action-text="编码"
          :loading="urlSafeEncoding"
          @submit="urlSafeEncode"
        >
          <template #input>
            <el-input
              v-model="urlSafeEncodeInput"
              type="textarea"
              :rows="8"
              placeholder="请输入要编码的文本..."
              clearable
            />
          </template>
          <template #output>
            <el-input
              v-model="urlSafeEncodeOutput"
              type="textarea"
              :rows="8"
              readonly
              placeholder="URL安全Base64编码结果将显示在这里..."
            />
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane label="URL安全解码" name="url-safe-decode">
        <ToolSection
          input-label="输入URL安全Base64"
          output-label="解码结果"
          action-text="解码"
          :loading="urlSafeDecoding"
          @submit="urlSafeDecode"
        >
          <template #input>
            <el-input
              v-model="urlSafeDecodeInput"
              type="textarea"
              :rows="8"
              placeholder="请输入URL安全Base64字符串..."
              clearable
            />
          </template>
          <template #output>
            <el-input
              v-model="urlSafeDecodeOutput"
              type="textarea"
              :rows="8"
              readonly
              placeholder="解码结果将显示在这里..."
            />
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane label="校验" name="validate">
        <ToolSection
          input-label="输入Base64文本"
          output-label="校验结果"
          action-text="校验"
          :loading="validating"
          :has-output="false"
          @submit="validateBase64"
        >
          <template #input>
            <el-input
              v-model="validateInput"
              type="textarea"
              :rows="8"
              placeholder="请输入要校验的Base64字符串..."
              clearable
            />
          </template>
        </ToolSection>
        <div v-if="validateResult !== null" style="margin-top: 16px;">
          <el-alert
            :title="validateResult.valid ? '校验通过' : '校验失败'"
            :type="validateResult.valid ? 'success' : 'error'"
            :description="validateResult.message"
            show-icon
            :closable="false"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane label="文件编码" name="file-encode">
        <ToolSection
          input-label="选择文件"
          output-label="Base64编码结果"
          action-text="编码"
          :loading="fileEncoding"
          @submit="encodeFile"
        >
          <template #input>
            <el-upload
              ref="fileEncodeUploadRef"
              :auto-upload="false"
              :limit="1"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :file-list="fileEncodeList"
              drag
            >
              <el-icon style="font-size: 40px; color: #909399;"><UploadFilled /></el-icon>
              <div style="margin-top: 8px;">将文件拖到此处，或<em>点击上传</em></div>
            </el-upload>
          </template>
          <template #output>
            <el-input
              v-model="fileEncodeOutput"
              type="textarea"
              :rows="8"
              readonly
              placeholder="文件编码结果将显示在这里..."
            />
            <div v-if="fileEncodeInfo" style="margin-top: 12px;">
              <el-descriptions :column="3" border size="small">
                <el-descriptions-item label="文件名">{{ fileEncodeInfo.filename }}</el-descriptions-item>
                <el-descriptions-item label="MIME类型">{{ fileEncodeInfo.mime_type }}</el-descriptions-item>
                <el-descriptions-item label="文件大小">{{ fileEncodeInfo.file_size }}</el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane label="文件解码" name="file-decode">
        <ToolSection
          input-label="输入Base64编码数据"
          output-label="解码结果"
          action-text="解码并下载"
          :loading="fileDecoding"
          @submit="decodeFile"
        >
          <template #input>
            <el-input
              v-model="fileDecodeInput"
              type="textarea"
              :rows="8"
              placeholder="请输入Base64编码的文件数据..."
              clearable
            />
            <div style="margin-top: 12px;">
              <el-input
                v-model="fileDecodeFilename"
                placeholder="可选：指定下载文件名"
                clearable
              >
                <template #prepend>文件名</template>
              </el-input>
            </div>
          </template>
          <template #output>
            <div v-if="fileDecodeDownloadUrl" style="text-align: center; padding: 20px;">
              <el-link
                type="primary"
                :href="fileDecodeDownloadUrl"
                :download="fileDecodeFilename || 'decoded_file'"
                :underline="false"
              >
                <el-icon style="margin-right: 4px;"><Download /></el-icon>
                点击下载解码文件
              </el-link>
            </div>
            <div v-else>
              <el-input
                type="textarea"
                :rows="4"
                readonly
                placeholder="解码后的下载链接将显示在这里..."
              />
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>
    </el-tabs>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Key, UploadFilled, Download } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'
import ToolSection from '@/components/ToolSection.vue'

export default {
  name: 'Base64Tools',
  components: {
    Key,
    UploadFilled,
    Download,
    ToolPage,
    ToolSection
  },
  data() {
    return {
      activeTab: 'encode',
      // Encode / Decode
      encodeInput: '',
      encodeOutput: '',
      encoding: false,
      decodeInput: '',
      decodeOutput: '',
      decoding: false,
      // URL Safe Encode
      urlSafeEncodeInput: '',
      urlSafeEncodeOutput: '',
      urlSafeEncoding: false,
      // URL Safe Decode
      urlSafeDecodeInput: '',
      urlSafeDecodeOutput: '',
      urlSafeDecoding: false,
      // Validate
      validateInput: '',
      validating: false,
      validateResult: null,
      // File Encode
      fileEncodeList: [],
      fileEncodeFile: null,
      fileEncodeOutput: '',
      fileEncodeInfo: null,
      fileEncoding: false,
      // File Decode
      fileDecodeInput: '',
      fileDecodeFilename: '',
      fileDecodeDownloadUrl: '',
      fileDecoding: false
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
    },

    async urlSafeEncode() {
      if (!this.urlSafeEncodeInput.trim()) {
        ElMessage.warning('请输入要编码的文本')
        return
      }

      this.urlSafeEncoding = true
      try {
        const response = await axios.post('/api/base64-tools/url-safe/encode', {
          text: this.urlSafeEncodeInput
        })

        if (response.data.success) {
          this.urlSafeEncodeOutput = response.data.encoded
          ElMessage.success('URL安全编码成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('URL安全编码失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.urlSafeEncoding = false
      }
    },

    async urlSafeDecode() {
      if (!this.urlSafeDecodeInput.trim()) {
        ElMessage.warning('请输入URL安全Base64字符串')
        return
      }

      this.urlSafeDecoding = true
      try {
        const response = await axios.post('/api/base64-tools/url-safe/decode', {
          encoded_text: this.urlSafeDecodeInput
        })

        if (response.data.success) {
          this.urlSafeDecodeOutput = response.data.decoded
          ElMessage.success('URL安全解码成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('URL安全解码失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.urlSafeDecoding = false
      }
    },

    async validateBase64() {
      if (!this.validateInput.trim()) {
        ElMessage.warning('请输入要校验的Base64字符串')
        return
      }

      this.validating = true
      try {
        const response = await axios.post('/api/base64-tools/validate', {
          text: this.validateInput
        })

        if (response.data.valid) {
          this.validateResult = {
            valid: true,
            message: response.data.message || '输入的文本是有效的Base64编码'
          }
          ElMessage.success('校验通过')
        } else {
          this.validateResult = {
            valid: false,
            message: response.data.error || '输入的文本不是有效的Base64编码'
          }
        }
      } catch (error) {
        this.validateResult = {
          valid: false,
          message: error.response?.data?.error || error.message
        }
      } finally {
        this.validating = false
      }
    },

    handleFileChange(file) {
      this.fileEncodeFile = file.raw
    },

    handleFileRemove() {
      this.fileEncodeFile = null
      this.fileEncodeOutput = ''
      this.fileEncodeInfo = null
    },

    async encodeFile() {
      if (!this.fileEncodeFile) {
        ElMessage.warning('请先选择要编码的文件')
        return
      }

      this.fileEncoding = true
      try {
        const formData = new FormData()
        formData.append('file', this.fileEncodeFile)

        const response = await axios.post('/api/base64-tools/encode-file', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        if (response.data.success) {
          this.fileEncodeOutput = response.data.encoded
          this.fileEncodeInfo = {
            filename: response.data.filename,
            mime_type: response.data.mime_type,
            file_size: response.data.file_size
          }
          ElMessage.success('文件编码成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('文件编码失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.fileEncoding = false
      }
    },

    async decodeFile() {
      if (!this.fileDecodeInput.trim()) {
        ElMessage.warning('请输入Base64编码的文件数据')
        return
      }

      this.fileDecoding = true
      try {
        const response = await axios.post('/api/base64-tools/decode-file', {
          encoded_data: this.fileDecodeInput,
          filename: this.fileDecodeFilename || undefined
        })

        if (response.data.success) {
          this.fileDecodeDownloadUrl = response.data.download_url
          ElMessage.success('文件解码成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('文件解码失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.fileDecoding = false
      }
    }
  }
}
</script>
