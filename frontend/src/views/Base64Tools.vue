<template>
  <ToolPage :title="$t('tools.base64.title')" :icon="Key">
    <el-tabs v-model="activeTab">
      <el-tab-pane :label="$t('tools.base64.tab.encode')" name="encode">
        <ToolSection
          :input-label="$t('tools.base64.label.inputText')"
          :output-label="$t('tools.base64.label.base64Result')"
          :action-text="$t('tools.base64.action.encode')"
          :loading="encoding"
          @submit="encodeBase64"
        >
          <template #input>
            <el-input
              v-model="encodeInput"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.base64.placeholder.inputText')"
              clearable
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="encodeInput">
                {{ encodeInput.length }} {{ $t('tools.base64.stats.chars') }} · {{ lineCount(encodeInput) }} {{ $t('tools.base64.stats.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('encode')">{{ $t('tools.base64.action.sample') }}</el-button>
                <el-button link size="small" v-if="encodeInput || encodeOutput" @click="encodeInput = ''; encodeOutput = ''">{{ $t('tools.base64.action.clear') }}</el-button>
              </div>
            </div>
          </template>
          <template #output>
            <el-input
              v-model="encodeOutput"
              type="textarea"
              :rows="8"
              readonly
              :placeholder="$t('tools.base64.placeholder.encodeResult')"
            />
            <div class="field-toolbar" v-if="encodeOutput">
              <span class="field-stats">
                {{ encodeOutput.length }} {{ $t('tools.base64.stats.chars') }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(encodeOutput)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.base64.action.copy') }}
              </el-button>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.base64.tab.decode')" name="decode">
        <ToolSection
          :input-label="$t('tools.base64.label.inputBase64')"
          :output-label="$t('tools.base64.label.decodeResult')"
          :action-text="$t('tools.base64.action.decode')"
          :loading="decoding"
          @submit="decodeBase64"
        >
          <template #input>
            <el-input
              v-model="decodeInput"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.base64.placeholder.inputBase64')"
              clearable
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="decodeInput">
                {{ decodeInput.length }} {{ $t('tools.base64.stats.chars') }} · {{ lineCount(decodeInput) }} {{ $t('tools.base64.stats.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('decode')">{{ $t('tools.base64.action.sample') }}</el-button>
                <el-button link size="small" v-if="decodeInput || decodeOutput" @click="decodeInput = ''; decodeOutput = ''">{{ $t('tools.base64.action.clear') }}</el-button>
              </div>
            </div>
          </template>
          <template #output>
            <el-input
              v-model="decodeOutput"
              type="textarea"
              :rows="8"
              readonly
              :placeholder="$t('tools.base64.placeholder.decodeResult')"
            />
            <div class="field-toolbar" v-if="decodeOutput">
              <span class="field-stats">
                {{ decodeOutput.length }} {{ $t('tools.base64.stats.chars') }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(decodeOutput)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.base64.action.copy') }}
              </el-button>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.base64.tab.urlSafeEncode')" name="url-safe-encode">
        <ToolSection
          :input-label="$t('tools.base64.label.inputText')"
          :output-label="$t('tools.base64.label.urlSafeBase64Result')"
          :action-text="$t('tools.base64.action.encode')"
          :loading="urlSafeEncoding"
          @submit="urlSafeEncode"
        >
          <template #input>
            <el-input
              v-model="urlSafeEncodeInput"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.base64.placeholder.inputText')"
              clearable
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="urlSafeEncodeInput">
                {{ urlSafeEncodeInput.length }} {{ $t('tools.base64.stats.chars') }} · {{ lineCount(urlSafeEncodeInput) }} {{ $t('tools.base64.stats.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('urlSafeEncode')">{{ $t('tools.base64.action.sample') }}</el-button>
                <el-button link size="small" v-if="urlSafeEncodeInput || urlSafeEncodeOutput" @click="urlSafeEncodeInput = ''; urlSafeEncodeOutput = ''">{{ $t('tools.base64.action.clear') }}</el-button>
              </div>
            </div>
          </template>
          <template #output>
            <el-input
              v-model="urlSafeEncodeOutput"
              type="textarea"
              :rows="8"
              readonly
              :placeholder="$t('tools.base64.placeholder.urlSafeEncodeResult')"
            />
            <div class="field-toolbar" v-if="urlSafeEncodeOutput">
              <span class="field-stats">
                {{ urlSafeEncodeOutput.length }} {{ $t('tools.base64.stats.chars') }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(urlSafeEncodeOutput)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.base64.action.copy') }}
              </el-button>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.base64.tab.urlSafeDecode')" name="url-safe-decode">
        <ToolSection
          :input-label="$t('tools.base64.label.inputUrlSafeBase64')"
          :output-label="$t('tools.base64.label.decodeResult')"
          :action-text="$t('tools.base64.action.decode')"
          :loading="urlSafeDecoding"
          @submit="urlSafeDecode"
        >
          <template #input>
            <el-input
              v-model="urlSafeDecodeInput"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.base64.placeholder.inputUrlSafeBase64')"
              clearable
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="urlSafeDecodeInput">
                {{ urlSafeDecodeInput.length }} {{ $t('tools.base64.stats.chars') }} · {{ lineCount(urlSafeDecodeInput) }} {{ $t('tools.base64.stats.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('urlSafeDecode')">{{ $t('tools.base64.action.sample') }}</el-button>
                <el-button link size="small" v-if="urlSafeDecodeInput || urlSafeDecodeOutput" @click="urlSafeDecodeInput = ''; urlSafeDecodeOutput = ''">{{ $t('tools.base64.action.clear') }}</el-button>
              </div>
            </div>
          </template>
          <template #output>
            <el-input
              v-model="urlSafeDecodeOutput"
              type="textarea"
              :rows="8"
              readonly
              :placeholder="$t('tools.base64.placeholder.decodeResult')"
            />
            <div class="field-toolbar" v-if="urlSafeDecodeOutput">
              <span class="field-stats">
                {{ urlSafeDecodeOutput.length }} {{ $t('tools.base64.stats.chars') }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(urlSafeDecodeOutput)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.base64.action.copy') }}
              </el-button>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.base64.tab.validate')" name="validate">
        <ToolSection
          :input-label="$t('tools.base64.label.inputBase64Text')"
          :output-label="$t('tools.base64.label.validateResult')"
          :action-text="$t('tools.base64.action.validate')"
          :loading="validating"
          :has-output="false"
          @submit="validateBase64"
        >
          <template #input>
            <el-input
              v-model="validateInput"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.base64.placeholder.inputValidateBase64')"
              clearable
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="validateInput">
                {{ validateInput.length }} {{ $t('tools.base64.stats.chars') }} · {{ lineCount(validateInput) }} {{ $t('tools.base64.stats.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('validate')">{{ $t('tools.base64.action.sample') }}</el-button>
                <el-button link size="small" v-if="validateInput || validateResult !== null" @click="validateInput = ''; validateResult = null">{{ $t('tools.base64.action.clear') }}</el-button>
              </div>
            </div>
          </template>
        </ToolSection>
        <div v-if="validateResult !== null" style="margin-top: 16px;">
          <el-alert
            :title="validateResult.valid ? $t('tools.base64.message.validatePass') : $t('tools.base64.message.validateFail')"
            :type="validateResult.valid ? 'success' : 'error'"
            :description="validateResult.message"
            show-icon
            :closable="false"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.base64.tab.fileEncode')" name="file-encode">
        <ToolSection
          :input-label="$t('tools.base64.label.selectFile')"
          :output-label="$t('tools.base64.label.fileEncodeResult')"
          :action-text="$t('tools.base64.action.fileEncode')"
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
              <div style="margin-top: 8px;">{{ $t('tools.base64.placeholder.fileDropzone') }}</div>
            </el-upload>
          </template>
          <template #output>
            <el-input
              v-model="fileEncodeOutput"
              type="textarea"
              :rows="8"
              readonly
              :placeholder="$t('tools.base64.placeholder.fileEncodeResult')"
            />
            <div class="field-toolbar" v-if="fileEncodeOutput">
              <span class="field-stats">
                {{ fileEncodeOutput.length }} {{ $t('tools.base64.stats.chars') }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(fileEncodeOutput)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.base64.action.copy') }}
              </el-button>
            </div>
            <div v-if="fileEncodeInfo" style="margin-top: 12px;">
              <el-descriptions :column="3" border size="small">
                <el-descriptions-item :label="$t('tools.base64.label.fileName')">{{ fileEncodeInfo.filename }}</el-descriptions-item>
                <el-descriptions-item :label="$t('tools.base64.label.mimeType')">{{ fileEncodeInfo.mime_type }}</el-descriptions-item>
                <el-descriptions-item :label="$t('tools.base64.label.fileSize')">{{ fileEncodeInfo.file_size }}</el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.base64.tab.fileDecode')" name="file-decode">
        <ToolSection
          :input-label="$t('tools.base64.label.inputBase64File')"
          :output-label="$t('tools.base64.label.decodeFileResult')"
          :action-text="$t('tools.base64.action.fileDecode')"
          :loading="fileDecoding"
          @submit="decodeFile"
        >
          <template #input>
            <el-input
              v-model="fileDecodeInput"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.base64.placeholder.inputBase64File')"
              clearable
            />
            <div style="margin-top: 12px;">
              <el-input
                v-model="fileDecodeFilename"
                :placeholder="$t('tools.base64.placeholder.outputFileName')"
                clearable
              >
                <template #prepend>{{ $t('tools.base64.label.fileName') }}</template>
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
                {{ $t('tools.base64.message.clickDownloadDecodedFile') }}
              </el-link>
            </div>
            <div v-else>
              <el-input
                type="textarea"
                :rows="4"
                readonly
                :placeholder="$t('tools.base64.placeholder.fileDecodeResult')"
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
import { Key, UploadFilled, Download, CopyDocument } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'
import ToolSection from '@/components/ToolSection.vue'
import { useDeviceStore } from '@/stores/device.js'

const SAMPLES = {
  encode: 'Hello, DevToolBox! 你好，开发者工具箱！',
  decode: 'SGVsbG8sIERldlRvb2xCb3ghIOS9oOWlvuW4ruWKoOS4iuS8gOWFuOS6i++8gQ==',
  urlSafeEncode: 'Hello, DevToolBox! This is a test with special chars: +/=',
  urlSafeDecode: 'SGVsbG8sIERldlRvb2xCb3ghIFRoaXMgaXMgYSB0ZXN0IHdpdGggc3BlY2lhbCBjaGFyczogKy89',
  validate: 'SGVsbG8gV29ybGQ='
}

export default {
  name: 'Base64Tools',
  components: {
    Key,
    UploadFilled,
    Download,
    CopyDocument,
    ToolPage,
    ToolSection
  },
  data() {
    const deviceStore = useDeviceStore()
    return {
      deviceStore,
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
    lineCount(text) {
      if (!text) return 0
      return text.split('\n').length
    },

    async copyText(text) {
      try {
        await navigator.clipboard.writeText(text)
        ElMessage.success(this.$t('tools.base64.message.copied'))
      } catch {
        const ta = document.createElement('textarea')
        ta.value = text
        ta.style.position = 'fixed'
        ta.style.opacity = '0'
        document.body.appendChild(ta)
        ta.select()
        document.execCommand('copy')
        document.body.removeChild(ta)
        ElMessage.success(this.$t('tools.base64.message.copied'))
      }
    },

    loadSample(tab) {
      const sample = SAMPLES[tab]
      if (!sample) return
      switch (tab) {
        case 'encode': this.encodeInput = sample; break
        case 'decode': this.decodeInput = sample; break
        case 'urlSafeEncode': this.urlSafeEncodeInput = sample; break
        case 'urlSafeDecode': this.urlSafeDecodeInput = sample; break
        case 'validate': this.validateInput = sample; break
      }
    },

    async encodeBase64() {
      if (!this.encodeInput.trim()) {
        ElMessage.warning(this.$t('tools.base64.message.inputTextRequired'))
        return
      }

      this.encoding = true
      try {
        const response = await axios.post('/api/base64-tools/encode', {
          text: this.encodeInput
        })

        if (response.data.success) {
          this.encodeOutput = response.data.encoded
          ElMessage.success(this.$t('tools.base64.message.encodeSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.base64.message.encodeFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.encoding = false
      }
    },

    async decodeBase64() {
      if (!this.decodeInput.trim()) {
        ElMessage.warning(this.$t('tools.base64.message.inputBase64Required'))
        return
      }

      this.decoding = true
      try {
        const response = await axios.post('/api/base64-tools/decode', {
          encoded_text: this.decodeInput
        })

        if (response.data.success) {
          this.decodeOutput = response.data.decoded
          ElMessage.success(this.$t('tools.base64.message.urlSafeDecodeSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.base64.message.urlSafeDecodeFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.decoding = false
      }
    },

    async urlSafeEncode() {
      if (!this.urlSafeEncodeInput.trim()) {
        ElMessage.warning(this.$t('tools.base64.message.inputTextRequired'))
        return
      }

      this.urlSafeEncoding = true
      try {
        const response = await axios.post('/api/base64-tools/url-safe/encode', {
          text: this.urlSafeEncodeInput
        })

        if (response.data.success) {
          this.urlSafeEncodeOutput = response.data.encoded
          ElMessage.success(this.$t('tools.base64.message.urlSafeEncodeSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.base64.message.urlSafeEncodeFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.urlSafeEncoding = false
      }
    },

    async urlSafeDecode() {
      if (!this.urlSafeDecodeInput.trim()) {
        ElMessage.warning(this.$t('tools.base64.message.inputBase64Required'))
        return
      }

      this.urlSafeDecoding = true
      try {
        const response = await axios.post('/api/base64-tools/url-safe/decode', {
          encoded_text: this.urlSafeDecodeInput
        })

        if (response.data.success) {
          this.urlSafeDecodeOutput = response.data.decoded
          ElMessage.success(this.$t('tools.base64.message.urlSafeDecodeSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.base64.message.urlSafeDecodeFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.urlSafeDecoding = false
      }
    },

    async validateBase64() {
      if (!this.validateInput.trim()) {
        ElMessage.warning(this.$t('tools.base64.message.inputValidateRequired'))
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
            message: response.data.message || this.$t('tools.base64.message.validBase64')
          }
          ElMessage.success(this.$t('tools.base64.message.validatePass'))
        } else {
          this.validateResult = {
            valid: false,
            message: response.data.error || this.$t('tools.base64.message.invalidBase64')
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
        ElMessage.warning(this.$t('tools.base64.message.selectFileRequired'))
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
          ElMessage.success(this.$t('tools.base64.message.fileEncodeSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.base64.message.fileEncodeFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.fileEncoding = false
      }
    },

    async decodeFile() {
      if (!this.fileDecodeInput.trim()) {
        ElMessage.warning(this.$t('tools.base64.message.inputBase64FileRequired'))
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
          ElMessage.success(this.$t('tools.base64.message.fileDecodeSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.base64.message.fileDecodeFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.fileDecoding = false
      }
    }
  }
}
</script>

<style scoped>
.field-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6px;
  min-height: 24px;
}

.field-stats {
  font-size: 12px;
  color: var(--dt-text-tertiary, #909399);
  line-height: 24px;
}

.toolbar-actions {
  display: flex;
  gap: 4px;
}

@media (max-width: 768px) {
  .el-form-item :deep(.el-form-item__label) { width: auto !important; min-width: 60px; }
  .el-form-item :deep(.el-form-item__content) { flex: 1; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; margin-left: 0 !important; margin-top: 8px; }
}
</style>
