<template>
  <ToolPage title="UUID生成器" :icon="Key">
    <el-tabs v-model="activeTab">
      <!-- 生成UUID -->
      <el-tab-pane label="生成UUID" name="generate">
        <div class="tool-section">
          <div class="config-row">
            <div class="config-item">
              <div class="field-label">版本</div>
              <el-select v-model="version" style="width: 100%;">
                <el-option label="UUID v1 (基于时间)" :value="1" />
                <el-option label="UUID v3 (基于MD5)" :value="3" />
                <el-option label="UUID v4 (随机)" :value="4" />
                <el-option label="UUID v5 (基于SHA-1)" :value="5" />
              </el-select>
            </div>
            <div class="config-item">
              <div class="field-label">数量</div>
              <el-input-number
                v-model="count"
                :min="1"
                :max="100"
                style="width: 100%;"
              />
            </div>
            <div class="config-item config-switch">
              <div class="field-label">大写</div>
              <el-switch v-model="uppercase" />
            </div>
          </div>

          <div class="config-row" v-if="version === 3 || version === 5">
            <div class="config-item">
              <div class="field-label">命名空间</div>
              <el-select v-model="namespace" style="width: 100%;">
                <el-option label="DNS" value="DNS" />
                <el-option label="URL" value="URL" />
                <el-option label="OID" value="OID" />
                <el-option label="X500" value="X500" />
              </el-select>
            </div>
            <div class="config-item" style="flex: 2;">
              <div class="field-label">名称</div>
              <el-input
                v-model="name"
                placeholder="请输入名称 (v3/v5 必填)"
                clearable
              />
            </div>
          </div>

          <div class="action-section">
            <el-button type="primary" @click="generateUUIDs" :loading="generating">
              生成
            </el-button>
          </div>

          <div class="output-section" v-if="generatedUUIDs.length > 0">
            <div class="result-header">
              <h4 class="section-title">生成结果 ({{ generatedUUIDs.length }} 个)</h4>
              <el-button size="small" type="primary" plain @click="copyAll">
                复制全部
              </el-button>
            </div>
            <div class="uuid-list">
              <div class="uuid-item" v-for="(item, index) in generatedUUIDs" :key="index">
                <span class="uuid-text">{{ item }}</span>
                <el-button size="small" text @click="copySingle(item)">
                  复制
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- 验证UUID -->
      <el-tab-pane label="验证UUID" name="validate">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">UUID字符串</h4>
            <el-input
              v-model="validateInput"
              placeholder="请输入UUID字符串，如: 550e8400-e29b-41d4-a716-446655440000"
              clearable
              @keyup.enter="validateUUID"
            />
          </div>

          <div class="action-section">
            <el-button type="primary" @click="validateUUID" :loading="validating">
              验证
            </el-button>
          </div>

          <div class="output-section" v-if="validateResult !== null">
            <el-alert
              :title="validateResult.valid ? '有效的UUID' : '无效的UUID'"
              :type="validateResult.valid ? 'success' : 'error'"
              :description="validateResult.valid
                ? `版本: v${validateResult.version} | 变体: ${validateResult.variant}`
                : '输入的字符串不是有效的UUID格式'"
              show-icon
            />
            <el-descriptions
              v-if="validateResult.valid"
              :column="descColumn"
              border
              style="margin-top: 16px;"
            >
              <el-descriptions-item label="版本">
                v{{ validateResult.version }}
              </el-descriptions-item>
              <el-descriptions-item label="变体">
                {{ validateResult.variant }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </el-tab-pane>

      <!-- 解析UUID -->
      <el-tab-pane label="解析UUID" name="parse">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">UUID字符串</h4>
            <el-input
              v-model="parseInput"
              placeholder="请输入UUID字符串，如: 550e8400-e29b-41d4-a716-446655440000"
              clearable
              @keyup.enter="parseUUID"
            />
          </div>

          <div class="action-section">
            <el-button type="primary" @click="parseUUID" :loading="parsing">
              解析
            </el-button>
          </div>

          <div class="output-section" v-if="parseResult">
            <h4 class="section-title">解析结果</h4>
            <el-descriptions :column="descColumn" border>
              <el-descriptions-item label="UUID">
                {{ parseResult.uuid }}
              </el-descriptions-item>
              <el-descriptions-item label="版本">
                v{{ parseResult.version }}
              </el-descriptions-item>
              <el-descriptions-item label="变体">
                {{ parseResult.variant }}
              </el-descriptions-item>
              <el-descriptions-item label="time_low">
                {{ parseResult.fields.time_low }}
              </el-descriptions-item>
              <el-descriptions-item label="time_mid">
                {{ parseResult.fields.time_mid }}
              </el-descriptions-item>
              <el-descriptions-item label="time_hi_version">
                {{ parseResult.fields.time_hi_version }}
              </el-descriptions-item>
              <el-descriptions-item label="clock_seq_hi_variant">
                {{ parseResult.fields.clock_seq_hi_variant }}
              </el-descriptions-item>
              <el-descriptions-item label="clock_seq_low">
                {{ parseResult.fields.clock_seq_low }}
              </el-descriptions-item>
              <el-descriptions-item label="node">
                {{ parseResult.fields.node }}
              </el-descriptions-item>
            </el-descriptions>

            <!-- v1 extra fields -->
            <template v-if="parseResult.version === 1 && parseResult.time !== undefined">
              <h4 class="section-title" style="margin-top: 20px;">UUID v1 详细信息</h4>
              <el-descriptions :column="descColumn" border>
                <el-descriptions-item label="时间戳">
                  {{ parseResult.time }}
                </el-descriptions-item>
                <el-descriptions-item label="时间 (UTC)" v-if="parseResult.time_as_datetime">
                  {{ parseResult.time_as_datetime }}
                </el-descriptions-item>
                <el-descriptions-item label="MAC地址">
                  {{ parseResult.mac_address }}
                </el-descriptions-item>
                <el-descriptions-item label="时钟序列">
                  {{ parseResult.clock_seq }}
                </el-descriptions-item>
              </el-descriptions>
            </template>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Key } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'

export default {
  name: 'UuidTools',
  components: {
    Key,
    ToolPage
  },
  data() {
    return {
      activeTab: 'generate',
      // Generate
      version: 4,
      count: 1,
      uppercase: false,
      namespace: 'DNS',
      name: '',
      generating: false,
      generatedUUIDs: [],
      // Validate
      validateInput: '',
      validating: false,
      validateResult: null,
      // Parse
      parseInput: '',
      parsing: false,
      parseResult: null
    }
  },
  computed: {
    descColumn() {
      return window.innerWidth <= 768 ? 1 : 2
    }
  },
  methods: {
    async generateUUIDs() {
      if ((this.version === 3 || this.version === 5) && !this.name.trim()) {
        ElMessage.warning('v3 和 v5 版本需要输入名称')
        return
      }

      this.generating = true
      try {
        const payload = {
          version: this.version,
          count: this.count,
          uppercase: this.uppercase
        }
        if (this.version === 3 || this.version === 5) {
          payload.namespace = this.namespace
          payload.name = this.name
        }

        const response = await axios.post('/api/uuid-tools/generate', payload)

        if (response.data.success) {
          this.generatedUUIDs = response.data.uuids
          ElMessage.success(`成功生成 ${response.data.count} 个 UUID`)
        } else {
          ElMessage.error(response.data.error || '生成失败')
        }
      } catch (error) {
        ElMessage.error('生成失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.generating = false
      }
    },

    copySingle(text) {
      navigator.clipboard.writeText(text).then(() => {
        ElMessage.success('已复制到剪贴板')
      })
    },

    copyAll() {
      const text = this.generatedUUIDs.join('\n')
      navigator.clipboard.writeText(text).then(() => {
        ElMessage.success('已复制全部 UUID 到剪贴板')
      })
    },

    async validateUUID() {
      if (!this.validateInput.trim()) {
        ElMessage.warning('请输入UUID字符串')
        return
      }

      this.validating = true
      try {
        const response = await axios.post('/api/uuid-tools/validate', {
          uuid_str: this.validateInput.trim()
        })

        if (response.data.success) {
          this.validateResult = response.data
        } else {
          ElMessage.error(response.data.error || '验证失败')
        }
      } catch (error) {
        ElMessage.error('验证失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.validating = false
      }
    },

    async parseUUID() {
      if (!this.parseInput.trim()) {
        ElMessage.warning('请输入UUID字符串')
        return
      }

      this.parsing = true
      try {
        const response = await axios.post('/api/uuid-tools/parse', {
          uuid_str: this.parseInput.trim()
        })

        if (response.data.success) {
          this.parseResult = response.data
          ElMessage.success('解析成功')
        } else {
          ElMessage.error(response.data.error || '解析失败')
        }
      } catch (error) {
        ElMessage.error('解析失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.parsing = false
      }
    }
  }
}
</script>

<style scoped>
.config-row {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.config-item {
  flex: 1;
  min-width: 140px;
}

.config-switch {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  min-width: 80px;
}

.field-label {
  font-size: var(--dt-font-size-sm, 13px);
  color: var(--dt-text-secondary, #909399);
  margin-bottom: 6px;
}

.action-section {
  margin: 16px 0;
}

.output-section {
  margin-top: 20px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.uuid-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.uuid-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--dt-bg-section, #f5f7fa);
  border-radius: 6px;
  border: 1px solid var(--dt-border-lighter, #ebeef5);
  transition: background 0.2s;
}

.uuid-item:hover {
  background: var(--dt-bg-hover, #ecf5ff);
}

.uuid-text {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: var(--dt-font-size-base, 14px);
  color: var(--dt-text-primary, #303133);
  word-break: break-all;
}

.section-title {
  font-size: var(--dt-font-size-base, 14px);
  font-weight: 600;
  color: var(--dt-text-primary, #303133);
  margin: 0 0 8px 0;
}

@media (max-width: 768px) {
  .config-row {
    flex-direction: column;
    gap: 12px;
  }

  .config-item {
    min-width: 100%;
  }

  .uuid-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }
}
</style>
