<template>
  <ToolPage title="二维码工具" :icon="Crop">
    <el-tabs v-model="activeTab" class="demo-tabs" @tab-change="handleTabChange">
      <el-tab-pane label="二维码生成" name="generate">
        <div class="tool-container">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="24" :md="12">
              <el-card class="input-card">
                <template #header>
                  <div class="card-header">
                    <span>输入内容</span>
                  </div>
                </template>
                <el-input
                  v-model="generateContent"
                  type="textarea"
                  :rows="6"
                  placeholder="请输入要生成二维码的内容，如网址、文本等"
                ></el-input>
                <div class="config-section">
                  <el-row :gutter="20" style="margin-top: 20px;">
                    <el-col :xs="24" :sm="12" :md="12">
                      <el-form-item label="尺寸">
                        <el-slider v-model="qrSize" :min="100" :max="500" :step="10" show-input />
                      </el-form-item>
                    </el-col>
                    <el-col :xs="24" :sm="12" :md="12">
                      <el-form-item label="颜色">
                        <el-color-picker v-model="qrColor" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="20">
                    <el-col :xs="24" :sm="12" :md="12">
                      <el-form-item label="背景色">
                        <el-color-picker v-model="qrBackground" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>
                <el-button type="primary" @click="generateQrCode" :loading="generating">
                  {{ generating ? '生成中...' : '生成二维码' }}
                </el-button>
              </el-card>
            </el-col>
            <el-col :xs="24" :sm="24" :md="12">
              <el-card class="output-card">
                <template #header>
                  <div class="card-header">
                    <span>二维码结果</span>
                  </div>
                </template>
                <div class="qr-result" v-if="generatedQrCode">
                  <img :src="'data:image/png;base64,' + generatedQrCode" alt="二维码" />
                  <el-button type="success" @click="downloadQrCode" style="margin-top: 20px;">
                    下载二维码
                  </el-button>
                </div>
                <div class="no-result" v-else>
                  <p>请在左侧输入内容并点击生成按钮</p>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-tab-pane>

      <el-tab-pane label="二维码美化" name="beautify">
        <div class="tool-container">
          <el-row :gutter="20">
            <el-col :xs="24" :sm="24" :md="12">
              <el-card class="input-card">
                <template #header>
                  <div class="card-header">
                    <span>上传二维码</span>
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
                      将二维码图片拖到此处，或 <em>点击上传</em>
                    </div>
                    <template #tip>
                      <div class="el-upload__tip">
                        请上传需要美化的二维码图片，支持PNG、JPG格式
                      </div>
                    </template>
                  </el-upload>
                </div>

                <div class="config-section" style="margin-top: 30px;">
                  <el-row :gutter="20">
                    <el-col :xs="24" :sm="12" :md="12">
                      <el-form-item label="圆角半径">
                        <el-slider v-model="cornerRadius" :min="0" :max="20" :step="1" show-input />
                      </el-form-item>
                    </el-col>
                    <el-col :xs="24" :sm="12" :md="12">
                      <el-form-item label="边框宽度">
                        <el-slider v-model="borderWidth" :min="0" :max="20" :step="1" show-input />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="20">
                    <el-col :xs="24" :sm="12" :md="12">
                      <el-form-item label="边框颜色">
                        <el-color-picker v-model="borderColor" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="20">
                    <el-col :span="24">
                      <el-form-item label="Logo上传">
                        <el-upload
                          class="logo-upload"
                          action="#"
                          :auto-upload="false"
                          :show-file-list="false"
                          :on-change="handleLogoUpload"
                        >
                          <el-button size="small" type="primary">选择Logo</el-button>
                        </el-upload>
                        <div v-if="logoPreview" class="logo-preview">
                          <img :src="logoPreview" alt="Logo预览" />
                        </div>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </div>

                <el-button type="primary" @click="beautifyQrCode" :loading="beautifying">
                  {{ beautifying ? '美化中...' : '美化二维码' }}
                </el-button>
              </el-card>
            </el-col>
            <el-col :xs="24" :sm="24" :md="12">
              <el-card class="output-card">
                <template #header>
                  <div class="card-header">
                    <span>美化结果</span>
                  </div>
                </template>
                <div class="qr-result" v-if="beautifiedQrCode">
                  <img :src="'data:image/png;base64,' + beautifiedQrCode" alt="美化后的二维码" />
                  <el-button type="success" @click="downloadBeautifiedQrCode" style="margin-top: 20px;">
                    下载美化后的二维码
                  </el-button>
                </div>
                <div class="no-result" v-else>
                  <p>请上传二维码图片并设置美化参数</p>
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
        ElMessage.warning('请输入要生成二维码的内容')
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
          ElMessage.success('二维码生成成功')
        } else {
          ElMessage.error(result.error || '生成失败')
        }
      } catch (error) {
        ElMessage.error('生成二维码时出错: ' + error.message)
      } finally {
        this.generating = false
      }
    },

    async beautifyQrCode() {
      if (!this.uploadedQrCode) {
        ElMessage.warning('请先上传二维码图片')
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
          ElMessage.success('二维码美化成功')
        } else {
          ElMessage.error(result.error || '美化失败')
        }
      } catch (error) {
        ElMessage.error('美化二维码时出错: ' + error.message)
      } finally {
        this.beautifying = false
      }
    },

    handleQrUpload(file) {
      if (!file || !file.raw) {
        ElMessage.error('文件上传失败：无效的文件对象')
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
          ElMessage.success('二维码上传成功')
        }
        img.onerror = () => {
          ElMessage.error('图片加载失败')
        }
        img.src = e.target.result
      }
      reader.onerror = () => {
        ElMessage.error('文件读取失败')
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
