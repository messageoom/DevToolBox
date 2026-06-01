<template>
  <ToolPage :title="$t('tools.qr.title')" :icon="Crop">
    <el-tabs v-model="activeTab" class="demo-tabs" @tab-change="handleTabChange">
      <el-tab-pane :label="$t('tools.qr.tab.generate')" name="generate">
        <div class="tool-container">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="24" :md="12">
              <el-card class="input-card">
                <template #header>
                  <div class="card-header">
                    <span>{{ $t('tools.qr.label.inputContent') }}</span>
                  </div>
                </template>
                <el-input
                  v-model="generateContent"
                  type="textarea"
                  :rows="6"
                  :placeholder="$t('tools.qr.label.qrPlaceholder')"
                ></el-input>
                <div class="config-section">
                  <el-row :gutter="20" style="margin-top: 20px;">
                    <el-col :xs="24" :sm="12" :md="12">
                      <el-form-item :label="$t('tools.qr.label.size')">
                        <el-slider v-model="qrSize" :min="100" :max="500" :step="10" show-input />
                      </el-form-item>
                    </el-col>
                    <el-col :xs="24" :sm="12" :md="12">
                      <el-form-item :label="$t('tools.qr.label.color')">
                        <el-color-picker v-model="qrColor" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="20">
                    <el-col :xs="24" :sm="12" :md="12">
                      <el-form-item :label="$t('tools.qr.label.bgColor')">
                        <el-color-picker v-model="qrBackground" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
                <el-button type="primary" @click="generateQrCode" :loading="generating">
                  {{ generating ? $t('tools.qr.label.generating') : $t('tools.qr.label.generateQr') }}
                </el-button>
              </el-card>
            </el-col>
            <el-col :xs="24" :sm="24" :md="12">
              <el-card class="output-card">
                <template #header>
                  <div class="card-header">
                    <span>{{ $t('tools.qr.label.qrResult') }}</span>
                  </div>
                </template>
                <div class="qr-result" v-if="generatedQrCode">
                  <img :src="'data:image/png;base64,' + generatedQrCode" :alt="$t('tools.qr.title')" />
                  <el-button type="success" @click="downloadQrCode" style="margin-top: 20px;">
                    {{ $t('tools.qr.label.downloadQr') }}
                  </el-button>
                </div>
                <div class="no-result" v-else>
                  <p>{{ $t('tools.qr.label.qrPlaceholder') }}</p>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.qr.tab.beautify')" name="beautify">
        <div class="tool-container">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="24" :md="12">
              <el-card class="input-card">
                <template #header>
                  <div class="card-header">
                    <span>{{ $t('tools.qr.label.uploadQr') }}</span>
                  </div>
                </template>
                <div class="upload-section">
                  <el-upload
                    class="qr-upload"
                    drag
                    action="#"
                    :auto-upload="false"
                    :show-file-list="false"
                    :on-change="handleQrUpload"
                    :multiple="false"
                    :limit="1"
                  >
                    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                    <div class="el-upload__text">
                      {{ $t('tools.qr.label.uploadDropzone') }}
                    </div>
                    <template #tip>
                      <div class="el-upload__tip">
                        {{ $t('tools.qr.label.uploadHint') }}
                      </div>
                    </template>
                  </el-upload>
                </div>

                <div class="config-section" style="margin-top: 30px;">
                  <el-row :gutter="20">
                    <el-col :xs="24" :sm="12" :md="12">
                      <el-form-item :label="$t('tools.qr.label.borderRadius')">
                        <el-slider v-model="cornerRadius" :min="0" :max="20" :step="1" show-input />
                      </el-form-item>
                    </el-col>
                    <el-col :xs="24" :sm="12" :md="12">
                      <el-form-item :label="$t('tools.qr.label.borderWidth')">
                        <el-slider v-model="borderWidth" :min="0" :max="20" :step="1" show-input />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="20">
                    <el-col :xs="24" :sm="12" :md="12">
                      <el-form-item :label="$t('tools.qr.label.borderColor')">
                        <el-color-picker v-model="borderColor" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="20">
                    <el-col :span="24">
                      <el-form-item :label="$t('tools.qr.label.logoUpload')">
                        <el-upload
                          class="logo-upload"
                          action="#"
                          :auto-upload="false"
                          :show-file-list="false"
                          :on-change="handleLogoUpload"
                        >
                          <el-button size="small" type="primary">{{ $t('tools.qr.label.selectLogo') }}</el-button>
                        </el-upload>
                        <div v-if="logoPreview" class="logo-preview">
                          <img :src="logoPreview" alt="Logo" />
                        </div>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>

                <el-button type="primary" @click="beautifyQrCode" :loading="beautifying">
                  {{ beautifying ? $t('tools.qr.label.beautifying') : $t('tools.qr.label.beautifyQr') }}
                </el-button>
              </el-card>
            </el-col>
            <el-col :xs="24" :sm="24" :md="12">
              <el-card class="output-card">
                <template #header>
                  <div class="card-header">
                    <span>{{ $t('tools.qr.label.beautifyResult') }}</span>
                  </div>
                </template>
                <div class="qr-result" v-if="beautifiedQrCode">
                  <img :src="'data:image/png;base64,' + beautifiedQrCode" :alt="$t('tools.qr.title')" />
                  <el-button type="success" @click="downloadBeautifiedQrCode" style="margin-top: 20px;">
                    {{ $t('tools.qr.label.downloadBeautified') }}
                  </el-button>
                </div>
                <div class="no-result" v-else>
                  <p>{{ $t('tools.qr.label.beautifyPlaceholder') }}</p>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>
    </el-tabs>
  </ToolPage>
</template>

<script>
import { UploadFilled, Crop } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'

export default {
  name: 'QrTools',
  components: {
    UploadFilled,
    Crop,
    ToolPage
  },
  data() {
    return {
      activeTab: 'generate',
      // 生成二维码相关数据
      generateContent: '',
      qrSize: 300,
      qrColor: '#000000',
      qrBackground: '#FFFFFF',
      generatedQrCode: '',
      generating: false,

      // 美化二维码相关数据
      uploadedQrCode: '',
      beautifiedQrCode: '',
      beautifying: false,
      cornerRadius: 0,
      borderWidth: 0,
      borderColor: '#000000',
      logoPreview: '',
      logoBase64: ''
    }
  },
  methods: {
    handleTabChange(tab) {
      this.activeTab = tab
    },

    async generateQrCode() {
      if (!this.generateContent) {
        ElMessage.warning(this.$t('tools.qr.message.inputContentRequired'))
        return
      }

      this.generating = true
      try {
        const response = await axios.post('/api/qr-tools/generate', {
          content: this.generateContent,
          size: this.qrSize,
          color: this.qrColor,
          background: this.qrBackground
        })

        const result = response.data
        if (result.success) {
          this.generatedQrCode = result.qr_code
          ElMessage.success(this.$t('tools.qr.message.generateSuccess'))
        } else {
          ElMessage.error(result.error || this.$t('tools.qr.message.generateFail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.qr.message.generateError') + error.message)
      } finally {
        this.generating = false
      }
    },

    async beautifyQrCode() {
      if (!this.uploadedQrCode) {
        ElMessage.warning(this.$t('tools.qr.message.uploadQrRequired'))
        return
      }

      this.beautifying = true
      try {
        const response = await axios.post('/api/qr-tools/beautify', {
          qr_code: this.uploadedQrCode,
          border_color: this.borderColor,
          border_width: this.borderWidth,
          corner_radius: this.cornerRadius,
          logo: this.logoBase64 || undefined
        })

        const result = response.data
        if (result.success) {
          this.beautifiedQrCode = result.beautified_qr_code
          ElMessage.success(this.$t('tools.qr.message.beautifySuccess'))
        } else {
          ElMessage.error(result.error || this.$t('tools.qr.message.beautifyFail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.qr.message.beautifyError') + error.message)
      } finally {
        this.beautifying = false
      }
    },

    handleQrUpload(file) {
      if (!file || !file.raw) {
        ElMessage.error(this.$t('tools.qr.message.invalidFileObject'))
        return
      }

      const reader = new FileReader()
      reader.onload = (e) => {
        const img = new Image()
        img.onload = () => {
          const canvas = document.createElement('canvas')
          const ctx = canvas.getContext('2d')
          canvas.width = img.width
          canvas.height = img.height
          ctx.drawImage(img, 0, 0)

          this.uploadedQrCode = canvas.toDataURL('image/png').split(',')[1]
          ElMessage.success(this.$t('tools.qr.message.uploadSuccess'))
        }
        img.onerror = () => {
          ElMessage.error(this.$t('tools.qr.message.imageLoadFail'))
        }
        img.src = e.target.result
      }
      reader.onerror = () => {
        ElMessage.error(this.$t('tools.qr.message.fileReadFail'))
      }
      reader.readAsDataURL(file.raw)
    },

    handleLogoUpload(file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        this.logoPreview = e.target.result
        this.logoBase64 = e.target.result.split(',')[1]
      }
      reader.readAsDataURL(file.raw)
    },

    downloadQrCode() {
      this.downloadImage(this.generatedQrCode, 'qrcode.png')
    },

    downloadBeautifiedQrCode() {
      this.downloadImage(this.beautifiedQrCode, 'beautified_qrcode.png')
    },

    downloadImage(base64Data, filename) {
      const link = document.createElement('a')
      link.href = 'data:image/png;base64,' + base64Data
      link.download = filename
      link.click()
    }
  }
}
</script>

<style scoped>
.tool-container {
  margin-top: 20px;
}

.input-card,
.output-card {
  height: 100%;
}

.card-header {
  font-weight: 600;
}

.qr-result {
  text-align: center;
}

.qr-result img {
  max-width: 100%;
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-sm);
}

.no-result {
  text-align: center;
  color: var(--dt-text-secondary);
  padding: 40px 0;
}

.logo-preview {
  margin-top: var(--dt-spacing-sm);
}

.logo-preview img {
  max-width: 100px;
  max-height: 100px;
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-sm);
}

@media (max-width: 768px) {
  .tool-container {
    margin-top: var(--dt-spacing-sm);
  }

  .input-card,
  .output-card {
    margin-bottom: var(--dt-spacing-md);
  }
}
</style>
