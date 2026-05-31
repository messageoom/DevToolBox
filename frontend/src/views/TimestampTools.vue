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

      <el-tab-pane label="时间加减" name="add-time">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">基准时间</h4>
            <el-input
              v-model="addTimeBaseTime"
              placeholder="请输入基准时间 (时间戳或日期时间字符串)..."
              style="width: 100%; margin-bottom: 10px;"
            />
            <el-radio-group v-model="addTimeType" style="margin-bottom: 10px;">
              <el-radio label="timestamp">时间戳</el-radio>
              <el-radio label="datetime_string">日期时间字符串</el-radio>
            </el-radio-group>
            <el-input
              v-model="addTimeFormat"
              placeholder="格式字符串 (如: %Y-%m-%d %H:%M:%S)"
              style="width: 100%; margin-bottom: 15px;"
            />

            <h4 class="section-title">时间偏移量</h4>
            <div v-for="(item, index) in addTimeAdditions" :key="index" class="addition-row">
              <el-select v-model="item.unit" placeholder="选择单位" style="width: 160px;">
                <el-option label="年" value="years" />
                <el-option label="月" value="months" />
                <el-option label="周" value="weeks" />
                <el-option label="天" value="days" />
                <el-option label="小时" value="hours" />
                <el-option label="分钟" value="minutes" />
                <el-option label="秒" value="seconds" />
              </el-select>
              <el-input-number
                v-model="item.amount"
                :precision="0"
                placeholder="数量"
                style="width: 160px; margin-left: 10px;"
              />
              <el-button
                type="danger"
                :icon="Delete"
                circle
                style="margin-left: 10px;"
                @click="removeAdditionRow(index)"
                v-if="addTimeAdditions.length > 1"
              />
            </div>
            <el-button type="primary" plain @click="addAdditionRow" style="margin-top: 10px;">
              添加偏移量
            </el-button>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="addTime" :loading="addTimeLoading">
              计算
            </el-button>
          </div>
          <div class="output-section" v-if="addTimeResult">
            <h4 class="section-title">计算结果</h4>
            <el-descriptions :column="descColumn" border>
              <el-descriptions-item label="原始时间">
                {{ addTimeResult.original_time }}
              </el-descriptions-item>
              <el-descriptions-item label="结果时间戳">
                {{ addTimeResult.result_timestamp }}
              </el-descriptions-item>
              <el-descriptions-item label="结果日期时间" :span="2">
                {{ addTimeResult.result_datetime }}
              </el-descriptions-item>
            </el-descriptions>
            <h4 class="section-title" style="margin-top: 20px;">操作列表</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item
                v-for="(op, index) in addTimeResult.operations"
                :key="index"
                :label="'操作 ' + (index + 1)"
              >
                {{ op }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="批量计算" name="batch-calculate">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">批量时间输入</h4>
            <el-input
              v-model="batchBaseTimes"
              type="textarea"
              :rows="6"
              placeholder="请输入多个时间 (每行一个，支持时间戳或日期时间字符串)..."
              style="width: 100%; margin-bottom: 15px;"
            />
            <el-row :gutter="15">
              <el-col :xs="24" :sm="12" :md="6">
                <div class="field-label">操作类型</div>
                <el-select v-model="batchOperation" style="width: 100%;">
                  <el-option label="加" value="add" />
                  <el-option label="减" value="subtract" />
                </el-select>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <div class="field-label">单位</div>
                <el-select v-model="batchUnit" style="width: 100%;">
                  <el-option label="年" value="years" />
                  <el-option label="月" value="months" />
                  <el-option label="周" value="weeks" />
                  <el-option label="天" value="days" />
                  <el-option label="小时" value="hours" />
                  <el-option label="分钟" value="minutes" />
                  <el-option label="秒" value="seconds" />
                </el-select>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <div class="field-label">数量</div>
                <el-input-number
                  v-model="batchAmount"
                  :precision="0"
                  style="width: 100%;"
                />
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <div class="field-label">输入类型</div>
                <el-select v-model="batchType" style="width: 100%;">
                  <el-option label="时间戳" value="timestamp" />
                  <el-option label="日期时间字符串" value="datetime_string" />
                </el-select>
              </el-col>
            </el-row>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="batchCalculate" :loading="batchLoading">
              批量计算
            </el-button>
          </div>
          <div class="output-section" v-if="batchResults && batchResults.length > 0">
            <h4 class="section-title">计算结果</h4>
            <el-table :data="batchResults" border stripe style="width: 100%;">
              <el-table-column type="index" label="序号" width="70" align="center" />
              <el-table-column prop="original" label="原始时间" min-width="180" />
              <el-table-column prop="result_timestamp" label="结果时间戳" min-width="160" />
              <el-table-column prop="result_datetime" label="结果日期时间" min-width="200" />
            </el-table>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="格式参考" name="formats">
        <div class="tool-section">
          <div class="action-section">
            <el-button type="primary" @click="fetchFormats" :loading="formatsLoading">
              获取格式参考
            </el-button>
          </div>
          <div class="output-section" v-if="formatsList && formatsList.length > 0">
            <h4 class="section-title">日期时间格式参考</h4>
            <el-table :data="formatsList" border stripe style="width: 100%;">
              <el-table-column prop="format_name" label="格式名称" min-width="200" />
              <el-table-column prop="format_pattern" label="格式模式" min-width="300" />
            </el-table>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Clock, Delete } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'

export default {
  name: 'TimestampTools',
  components: {
    Clock,
    Delete,
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
      parsedResult: null,
      // 时间加减相关
      addTimeBaseTime: '',
      addTimeType: 'timestamp',
      addTimeFormat: '%Y-%m-%d %H:%M:%S',
      addTimeAdditions: [
        { unit: 'days', amount: 1 }
      ],
      addTimeLoading: false,
      addTimeResult: null,
      // 批量计算相关
      batchBaseTimes: '',
      batchOperation: 'add',
      batchUnit: 'days',
      batchAmount: 1,
      batchType: 'timestamp',
      batchLoading: false,
      batchResults: [],
      // 格式参考相关
      formatsLoading: false,
      formatsList: []
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
    },

    // 时间加减相关方法
    addAdditionRow() {
      this.addTimeAdditions.push({ unit: 'days', amount: 1 })
    },

    removeAdditionRow(index) {
      this.addTimeAdditions.splice(index, 1)
    },

    async addTime() {
      if (!this.addTimeBaseTime) {
        ElMessage.warning('请输入基准时间')
        return
      }
      if (this.addTimeAdditions.some(item => item.amount === null || item.amount === undefined)) {
        ElMessage.warning('请填写所有偏移量数值')
        return
      }

      this.addTimeLoading = true
      try {
        const response = await axios.post('/api/timestamp-tools/add-time', {
          base_time: this.addTimeBaseTime,
          type: this.addTimeType,
          format: this.addTimeFormat,
          additions: this.addTimeAdditions.map(item => ({
            unit: item.unit,
            amount: item.amount
          }))
        })

        if (response.data.success) {
          this.addTimeResult = response.data
          ElMessage.success('计算成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('计算失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.addTimeLoading = false
      }
    },

    // 批量计算相关方法
    async batchCalculate() {
      const times = this.batchBaseTimes
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)

      if (times.length === 0) {
        ElMessage.warning('请输入至少一个时间')
        return
      }
      if (this.batchAmount === null || this.batchAmount === undefined) {
        ElMessage.warning('请填写数量')
        return
      }

      this.batchLoading = true
      try {
        const response = await axios.post('/api/timestamp-tools/batch-calculate', {
          base_times: times,
          operation: this.batchOperation,
          unit: this.batchUnit,
          amount: this.batchAmount,
          type: this.batchType
        })

        if (response.data.success) {
          this.batchResults = response.data.results
          ElMessage.success('批量计算成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('批量计算失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.batchLoading = false
      }
    },

    // 格式参考相关方法
    async fetchFormats() {
      this.formatsLoading = true
      try {
        const response = await axios.get('/api/timestamp-tools/formats')
        if (response.data.success) {
          this.formatsList = response.data.formats
          ElMessage.success('获取成功')
        } else {
          ElMessage.error('获取失败')
        }
      } catch (error) {
        ElMessage.error('获取失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.formatsLoading = false
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

/* 时间加减偏移量行样式 */
.addition-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.field-label {
  font-size: var(--dt-font-size-sm);
  color: var(--dt-text-secondary);
  margin-bottom: 5px;
}

@media (max-width: 768px) {
  .timezone-datetime {
    font-size: var(--dt-font-size-lg);
  }

  .addition-row {
    flex-wrap: wrap;
  }
}
</style>
