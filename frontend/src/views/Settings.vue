<template>
  <ToolPage title="Settings" :icon="Setting">
    <el-tabs v-model="activeTab" class="settings-tabs">
      <!-- Security Center -->
      <el-tab-pane label="安全中心" name="security">
        <div class="settings-section">
          <h3 class="section-title">访问令牌</h3>
          <div class="token-card">
            <div class="token-status">
              <span class="label">状态</span>
              <el-tag :type="config.security?.token_enabled ? 'success' : 'info'">
                {{ config.security?.token_enabled ? '已启用' : '已禁用' }}
              </el-tag>
            </div>
            <div class="token-url" v-if="config.security?.has_token">
              <span class="label">访问地址</span>
              <div class="url-row">
                <el-input :model-value="tokenUrl" readonly size="large">
                  <template #suffix>
                    <el-button link @click="copyToClipboard(tokenUrl)">
                      <el-icon><DocumentCopy /></el-icon>
                    </el-button>
                  </template>
                </el-input>
              </div>
            </div>
            <div class="token-actions">
              <el-popconfirm title="刷新后旧 Token 将失效，确定？" @confirm="refreshToken">
                <template #reference>
                  <el-button type="danger" plain :loading="refreshing">刷新 Token</el-button>
                </template>
              </el-popconfirm>
              <el-button
                :type="config.security?.token_enabled ? 'warning' : 'success'"
                plain
                @click="toggleToken"
              >
                {{ config.security?.token_enabled ? '禁用 Token' : '启用 Token' }}
              </el-button>
            </div>
          </div>
        </div>

        <div class="settings-section">
          <h3 class="section-title">临时令牌</h3>
          <p class="section-desc">生成临时访问令牌，可分享给他人限时使用。</p>
          <div class="temp-token-form">
            <el-input v-model="tempTokenForm.label" placeholder="标签（如：同事小王）" style="width: 200px" />
            <el-select v-model="tempTokenForm.expires_minutes" style="width: 160px">
              <el-option label="30 分钟" :value="30" />
              <el-option label="1 小时" :value="60" />
              <el-option label="6 小时" :value="360" />
              <el-option label="24 小时" :value="1440" />
              <el-option label="7 天" :value="10080" />
            </el-select>
            <el-button type="primary" @click="createTempToken" :loading="creatingTemp">生成</el-button>
          </div>
          <el-table :data="tempTokens" empty-text="暂无临时令牌" stripe style="margin-top: 16px">
            <el-table-column prop="label" label="标签" width="150" />
            <el-table-column label="Token" width="200">
              <template #default="{ row }">
                <code class="token-code">{{ row.token }}</code>
              </template>
            </el-table-column>
            <el-table-column label="过期时间" width="180">
              <template #default="{ row }">
                {{ formatTime(row.expires_at) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="isExpired(row.expires_at) ? 'danger' : 'success'" size="small">
                  {{ isExpired(row.expires_at) ? '已过期' : '有效' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button link type="primary" @click="copyToClipboard(buildTokenUrl(row.token))">复制</el-button>
                <el-popconfirm title="确定删除？" @confirm="deleteTempToken(row.token)">
                  <template #reference>
                    <el-button link type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <!-- Storage -->
      <el-tab-pane label="存储配置" name="storage">
        <div class="settings-section">
          <h3 class="section-title">文件存储</h3>
          <el-form label-width="140px" label-position="left">
            <el-form-item label="文件保存目录">
              <el-input v-model="storageForm.upload_dir" placeholder="uploads" />
            </el-form-item>
            <el-form-item label="单文件最大大小">
              <div class="slider-row">
                <el-slider v-model="storageForm.max_file_size_mb" :min="1" :max="100" :step="1" style="flex: 1" />
                <span class="slider-value">{{ storageForm.max_file_size_mb }} MB</span>
              </div>
            </el-form-item>
            <el-form-item label="自动清理天数">
              <el-input-number v-model="storageForm.auto_cleanup_days" :min="0" :max="365" :step="1" />
              <span class="form-hint">0 = 不自动清理</span>
            </el-form-item>
          </el-form>
          <el-button type="primary" @click="saveStorage" :loading="saving">保存配置</el-button>

          <div class="storage-stats" v-if="status.disk_usage_bytes !== undefined">
            <h4>当前存储</h4>
            <div class="stat-row">
              <span>文件数量：<strong>{{ status.file_count }}</strong></span>
              <span>磁盘占用：<strong>{{ formatBytes(status.disk_usage_bytes) }}</strong></span>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Network -->
      <el-tab-pane label="网络配置" name="network">
        <div class="settings-section">
          <h3 class="section-title">网络设置</h3>
          <el-alert type="info" :closable="false" show-icon style="margin-bottom: 20px">
            网络配置修改后需要重启应用才能生效。
          </el-alert>
          <el-form label-width="140px" label-position="left">
            <el-form-item label="监听端口">
              <el-input-number v-model="networkForm.port" :min="1024" :max="65535" />
            </el-form-item>
            <el-form-item label="绑定地址">
              <el-select v-model="networkForm.host" style="width: 240px">
                <el-option label="仅本机 (127.0.0.1)" value="127.0.0.1" />
                <el-option label="所有接口 (0.0.0.0)" value="0.0.0.0" />
              </el-select>
            </el-form-item>
          </el-form>
          <el-button type="primary" @click="saveNetwork" :loading="saving">保存配置</el-button>
        </div>
      </el-tab-pane>

      <!-- About -->
      <el-tab-pane label="关于" name="about">
        <div class="settings-section">
          <div class="about-card">
            <div class="about-logo">
              <span class="logo-icon">DT</span>
            </div>
            <h2 class="about-title">DevToolBox</h2>
            <p class="about-version">v{{ status.version || '-' }}</p>
            <p class="about-desc">本地优先的开发者工具箱，所有数据在本地处理，不上传、不外发。</p>
          </div>

          <el-descriptions :column="1" border style="margin-top: 24px">
            <el-descriptions-item label="运行时长">{{ formatUptime(status.uptime_seconds) }}</el-descriptions-item>
            <el-descriptions-item label="Python 版本">{{ status.python_version || '-' }}</el-descriptions-item>
            <el-descriptions-item label="操作系统">{{ status.platform || '-' }}</el-descriptions-item>
            <el-descriptions-item label="项目地址">
              <a href="https://github.com/messageoom/DevToolBox" target="_blank" class="link">
                github.com/messageoom/DevToolBox
              </a>
            </el-descriptions-item>
            <el-descriptions-item label="开源协议">MIT License</el-descriptions-item>
          </el-descriptions>
        </div>
      </el-tab-pane>
    </el-tabs>
  </ToolPage>
</template>

<script>
import { defineComponent } from 'vue'
import { ElMessage } from 'element-plus'
import { Setting, DocumentCopy } from '@element-plus/icons-vue'
import ToolPage from '@/components/ToolPage.vue'
import axios from 'axios'

export default defineComponent({
  name: 'Settings',
  components: { ToolPage, Setting, DocumentCopy },
  data() {
    return {
      activeTab: 'security',
      config: { security: {}, storage: {}, network: {} },
      status: {},
      refreshing: false,
      saving: false,
      creatingTemp: false,
      tokenUrl: '',
      tempTokenForm: { label: '', expires_minutes: 60 },
      storageForm: { upload_dir: 'uploads', max_file_size_mb: 50, auto_cleanup_days: 0 },
      networkForm: { port: 5000, host: '0.0.0.0' },
    }
  },
  computed: {
    tempTokens() {
      return (this.config.security?.temp_tokens || []).map(t => ({
        ...t,
        _expired: this.isExpired(t.expires_at)
      }))
    }
  },
  mounted() {
    this.loadConfig()
    this.loadStatus()
  },
  methods: {
    async loadConfig() {
      try {
        const res = await axios.get('/api/settings/config')
        if (res.data.success) {
          this.config = res.data.config
          this.storageForm = { ...res.data.config.storage }
          this.networkForm = { ...res.data.config.network }

          // Build token URL
          const port = res.data.config.network?.port || 5000
          if (res.data.config.security?.has_token) {
            this.tokenUrl = `http://127.0.0.1:${port}/?token=***`
          }
        }
      } catch (e) {
        ElMessage.error('Failed to load config')
      }
    },
    async loadStatus() {
      try {
        const res = await axios.get('/api/settings/status')
        if (res.data.success) {
          this.status = res.data.status
        }
      } catch (e) { /* ignore */ }
    },
    async refreshToken() {
      this.refreshing = true
      try {
        const res = await axios.post('/api/settings/security/token')
        if (res.data.success) {
          this.tokenUrl = res.data.token_url
          ElMessage.success('Token 已刷新')
          this.loadConfig()
        }
      } catch (e) {
        ElMessage.error('刷新失败')
      } finally {
        this.refreshing = false
      }
    },
    async toggleToken() {
      const enabled = !this.config.security?.token_enabled
      try {
        const res = await axios.post('/api/settings/config', {
          security: { token_enabled: enabled }
        })
        if (res.data.success) {
          ElMessage.success(enabled ? 'Token 已启用' : 'Token 已禁用')
          this.loadConfig()
        }
      } catch (e) {
        ElMessage.error('操作失败')
      }
    },
    async createTempToken() {
      if (!this.tempTokenForm.label.trim()) {
        ElMessage.warning('请输入标签')
        return
      }
      this.creatingTemp = true
      try {
        const res = await axios.post('/api/settings/security/temp-token', this.tempTokenForm)
        if (res.data.success) {
          ElMessage.success('临时令牌已生成')
          this.tempTokenForm.label = ''
          this.loadConfig()
        }
      } catch (e) {
        ElMessage.error('生成失败')
      } finally {
        this.creatingTemp = false
      }
    },
    async deleteTempToken(token) {
      try {
        const res = await axios.delete(`/api/settings/security/temp-token/${token}`)
        if (res.data.success) {
          ElMessage.success('已删除')
          this.loadConfig()
        }
      } catch (e) {
        ElMessage.error('删除失败')
      }
    },
    async saveStorage() {
      this.saving = true
      try {
        const res = await axios.post('/api/settings/config', { storage: this.storageForm })
        if (res.data.success) {
          ElMessage.success('存储配置已保存')
        }
      } catch (e) {
        ElMessage.error('保存失败')
      } finally {
        this.saving = false
      }
    },
    async saveNetwork() {
      this.saving = true
      try {
        const res = await axios.post('/api/settings/config', { network: this.networkForm })
        if (res.data.success) {
          ElMessage.success('网络配置已保存，重启后生效')
        }
      } catch (e) {
        ElMessage.error('保存失败')
      } finally {
        this.saving = false
      }
    },
    copyToClipboard(text) {
      navigator.clipboard.writeText(text).then(() => {
        ElMessage.success('已复制到剪贴板')
      }).catch(() => {
        ElMessage.error('复制失败')
      })
    },
    buildTokenUrl(token) {
      const port = this.config.network?.port || 5000
      return `http://127.0.0.1:${port}/?token=${token}`
    },
    isExpired(expiresAt) {
      return new Date(expiresAt) < new Date()
    },
    formatTime(isoStr) {
      if (!isoStr) return '-'
      const d = new Date(isoStr)
      return d.toLocaleString('zh-CN')
    },
    formatUptime(seconds) {
      if (!seconds) return '-'
      const h = Math.floor(seconds / 3600)
      const m = Math.floor((seconds % 3600) / 60)
      const s = seconds % 60
      if (h > 0) return `${h} 小时 ${m} 分 ${s} 秒`
      if (m > 0) return `${m} 分 ${s} 秒`
      return `${s} 秒`
    },
    formatBytes(bytes) {
      if (!bytes) return '0 B'
      const units = ['B', 'KB', 'MB', 'GB']
      let i = 0
      let val = bytes
      while (val >= 1024 && i < units.length - 1) { val /= 1024; i++ }
      return `${val.toFixed(1)} ${units[i]}`
    }
  }
})
</script>

<style scoped>
.settings-tabs {
  margin-top: 8px;
}

.settings-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--dt-text-primary);
  margin: 0 0 16px 0;
}

.section-desc {
  font-size: 13px;
  color: var(--dt-text-secondary);
  margin: -8px 0 16px 0;
}

/* Token Card */
.token-card {
  background: var(--dt-bg-section);
  border: 1px solid var(--dt-border-light);
  border-radius: 12px;
  padding: 20px;
}

.token-status, .token-url {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.token-status .label, .token-url .label {
  font-size: 13px;
  color: var(--dt-text-secondary);
  min-width: 70px;
}

.url-row {
  flex: 1;
}

.token-actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}

/* Temp Token Form */
.temp-token-form {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.token-code {
  font-family: 'SF Mono', 'Consolas', monospace;
  font-size: 12px;
  background: var(--dt-bg-hover);
  padding: 2px 6px;
  border-radius: 4px;
}

/* Storage */
.slider-row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.slider-value {
  font-size: 13px;
  color: var(--dt-text-secondary);
  min-width: 60px;
  text-align: right;
}

.form-hint {
  font-size: 12px;
  color: var(--dt-text-secondary);
  margin-left: 8px;
}

.storage-stats {
  margin-top: 24px;
  padding: 16px;
  background: var(--dt-bg-section);
  border-radius: 8px;
}

.storage-stats h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.stat-row {
  display: flex;
  gap: 24px;
  font-size: 13px;
  color: var(--dt-text-secondary);
}

/* About */
.about-card {
  text-align: center;
  padding: 32px 0;
}

.about-logo {
  margin-bottom: 16px;
}

.logo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  border-radius: 18px;
  background: var(--dt-primary);
  color: white;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -1px;
}

.about-title {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--dt-text-primary);
}

.about-version {
  font-size: 14px;
  color: var(--dt-text-secondary);
  margin: 4px 0 12px;
}

.about-desc {
  font-size: 14px;
  color: var(--dt-text-secondary);
  max-width: 400px;
  margin: 0 auto;
}

.link {
  color: var(--dt-primary);
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
