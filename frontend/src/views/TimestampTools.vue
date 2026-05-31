<template>
  <ToolPage title="时间戳工具" :icon="Clock">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="当前时间" name="current">
        <div class="tool-section">
          <div class="action-section">
            <el-button type="primary" @click="getCurrentTimestamp" :loading="loading">
              获取当前时间戳
            </el-button>
          </div>
          <div class="output-section" v-if="currentTimestamp">
            <h4 class="section-title">时间戳信息</h4>
            <el-descriptions :column="descColumn" border>
              <el-descriptions-item label="时间戳(秒)">
                {{ currentTimestamp.timestamp }}
              </el-descriptions-item>
              <el-descriptions-item label="时间戳(毫秒)">
                {{ currentTimestamp.timestamp_ms }}
              </el-descriptions-item>
              <el-descriptions-item label="ISO格式" :span="2">
                {{ currentTimestamp.datetime }}
              </el-descriptions-item>
              <el-descriptions-item label="本地时间" :span="2">
                {{ currentTimestamp.local_time }}
              </el-descriptions-item>
            </el-descriptions>

            <h4 class="section-title" style="margin-top: 30px;">多时区时间</h4>
            <el-alert
              title="当前时区信息"
              :description="`检测到的当前时区: ${currentTimestamp.current_timezone}`"
              type="info"
              style="margin-bottom: 20px;"
              show-icon
            />

            <el-row :gutter="20">
              <el-col :xs="24" :sm="24" :md="12" v-for="(timezone, key) in currentTimestamp.timezones" :key="key">
                <el-card :class="{'current-timezone-card': key === 'local'}" style="margin-bottom: 15px;">
                  <template #header>
                    <div class="timezone-header">
                      <span class="timezone-name">{{ timezone.name }}</span>
                      <el-tag size="small" type="info">{{ timezone.offset }}</el-tag>
                    </div>
                  </template>
                  <div class="timezone-content">
                    <div class="timezone-datetime">{{ timezone.datetime }}</div>
                    <div class="timezone-info">{{ timezone.timezone }}</div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="转换时间戳" name="convert">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">输入时间戳</h4>
            <el-input-number
              v-model="timestampInput"
              :min="0"
              :precision="0"
              placeholder="请输入时间戳..."
              style="width: 100%;"
            />
            <el-radio-group v-model="timestampType" style="margin-top: 10px;">
              <el-radio label="seconds">秒</el-radio>
              <el-radio label="milliseconds">毫秒</el-radio>
            </el-radio-group>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="convertTimestamp" :loading="converting">
              转换
            </el-button>
          </div>
          <div class="output-section" v-if="convertedTimestamp">
            <h4 class="section-title">转换结果</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="时间戳(秒)">
                {{ convertedTimestamp.timestamp }}
              </el-descriptions-item>
              <el-descriptions-item label="时间戳(毫秒)">
                {{ convertedTimestamp.timestamp_ms }}
              </el-descriptions-item>
              <el-descriptions-item label="ISO格式">
                {{ convertedTimestamp.datetime }}
              </el-descriptions-item>
              <el-descriptions-item label="北京时间">
                {{ convertedTimestamp.formatted.beijing }}
              </el-descriptions-item>
              <el-descriptions-item label="本地时间">
                {{ convertedTimestamp.formatted.local }}
              </el-descriptions-item>
              <el-descriptions-item label="UTC时间">
                {{ convertedTimestamp.formatted.utc }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="解析日期时间" name="parse">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">输入日期时间字符串</h4>
            <el-input
              v-model="datetimeString"
              placeholder="请输入日期时间字符串..."
              style="width: 100%; margin-bottom: 10px;"
            />
            <el-input
              v-model="formatString"
              placeholder="格式字符串 (如: %Y-%m-%d %H:%M:%S)"
              style="width: 100%;"
            />
          </div>
          <div class="action-section">
            <el-button type="primary" @click="parseDatetime" :loading="parsing">
              解析
            </el-button>
          </div>
          <div class="output-section" v-if="parsedResult">
            <h4 class="section-title">解析结果</h4>
            <el-descriptions :column="descColumn" border>
              <el-descriptions-item label="时间戳(秒)">
                {{ parsedResult.timestamp }}
              </el-descriptions-item>
              <el-descriptions-item label="时间戳(毫秒)">
                {{ parsedResult.timestamp_ms }}
              </el-descriptions-item>
              <el-descriptions-item label="ISO格式">
                {{ parsedResult.datetime }}
              </el-descriptions-item>
              <el-descriptions-item label="年">
                {{ parsedResult.parsed.year }}
              </el-descriptions-item>
              <el-descriptions-item label="月">
                {{ parsedResult.parsed.month }}
              </el-descriptions-item>
              <el-descriptions-item label="日">
                {{ parsedResult.parsed.day }}
              </el-descriptions-item>
              <el-descriptions-item label="时">
                {{ parsedResult.parsed.hour }}
              </el-descriptions-item>
              <el-descriptions-item label="分">
                {{ parsedResult.parsed.minute }}
              </el-descriptions-item>
              <el-descriptions-item label="秒">
                {{ parsedResult.parsed.second }}
              </el-descriptions-item>
              <el-descriptions-item label="星期" :span="2">
                {{ parsedResult.parsed.weekday }} ({{ parsedResult.parsed.isoweekday }})
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Clock } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'

export default {
  name: 'TimestampTools',
  components: {
    Clock,
    ToolPage
  },
  data() {
    return {
      activeTab: 'current',
      loading: false,
      currentTimestamp: null,
      timestampInput: null,
      timestampType: 'seconds',
      converting: false,
      convertedTimestamp: null,
      // 解析日期时间相关
      datetimeString: '',
      formatString: '%Y-%m-%d %H:%M:%S',
      parsing: false,
      parsedResult: null
    }
  },
  computed: {
    descColumn() {
      return window.innerWidth <= 768 ? 1 : 2
    }
  },
  methods: {
    async getCurrentTimestamp() {
      this.loading = true
      try {
        const response = await axios.get('/api/timestamp-tools/current')
        if (response.data.success) {
          this.currentTimestamp = response.data
          ElMessage.success('获取成功')
        } else {
          ElMessage.error('获取失败')
        }
      } catch (error) {
        ElMessage.error('获取失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.loading = false
      }
    },

    async convertTimestamp() {
      if (this.timestampInput === null || this.timestampInput < 0) {
        ElMessage.warning('请输入有效的时间戳')
        return
      }

      this.converting = true
      try {
        const response = await axios.post('/api/timestamp-tools/convert', {
          timestamp: this.timestampInput,
          type: this.timestampType
        })

        if (response.data.success) {
          this.convertedTimestamp = response.data
          ElMessage.success('转换成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('转换失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.converting = false
      }
    },

    async parseDatetime() {
      if (!this.datetimeString) {
        ElMessage.warning('请输入日期时间字符串')
        return
      }

      this.parsing = true
      try {
        const response = await axios.post('/api/timestamp-tools/parse', {
          datetime_string: this.datetimeString,
          format: this.formatString
        })

        if (response.data.success) {
          this.parsedResult = response.data
          ElMessage.success('解析成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('解析失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.parsing = false
      }
    }
  }
}
</script>

<style scoped>
/* 时区相关样式 */
.timezone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.timezone-name {
  font-weight: 600;
  font-size: var(--dt-font-size-base);
  color: var(--dt-text-primary);
}

.timezone-content {
  text-align: center;
}

.timezone-datetime {
  font-size: var(--dt-font-size-xl);
  font-weight: 600;
  color: var(--dt-primary);
  margin-bottom: var(--dt-spacing-sm);
}

.timezone-info {
  font-size: var(--dt-font-size-xs);
  color: var(--dt-text-secondary);
}

.current-timezone-card {
  border: 2px solid var(--dt-success) !important;
  background: linear-gradient(135deg, #f0f9ff 0%, #e6fffa 100%);
}

.current-timezone-card .timezone-datetime {
  color: var(--dt-success);
}

.current-timezone-card .timezone-name {
  color: var(--dt-success);
}

@media (max-width: 768px) {
  .timezone-datetime {
    font-size: var(--dt-font-size-lg);
  }
}
</style>
