<template>
  <ToolPage :title="$t('tools.timestamp.title')" :icon="Clock">
    <el-tabs v-model="activeTab">
      <el-tab-pane :label="$t('tools.timestamp.tab.currentTime')" name="current">
        <div class="tool-section">
          <div class="action-section">
            <el-button type="primary" @click="getCurrentTimestamp" :loading="loading">
              {{ $t('tools.timestamp.label.getCurrentTimestamp') }}
            </el-button>
          </div>
          <div class="output-section" v-if="currentTimestamp">
            <h4 class="section-title">{{ $t('tools.timestamp.label.timestampInfo') }}</h4>
            <el-descriptions :column="descColumn" border>
              <el-descriptions-item :label="$t('tools.timestamp.label.timestampSeconds')">
                {{ currentTimestamp.timestamp }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.timestampMillis')">
                {{ currentTimestamp.timestamp_ms }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.isoFormat')" :span="2">
                {{ currentTimestamp.datetime }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.localTime')" :span="2">
                {{ currentTimestamp.local_time }}
              </el-descriptions-item>
            </el-descriptions>

            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(currentTimestamp.timestamp)">
                <el-icon><CopyDocument /></el-icon> Copy Timestamp
              </el-button>
              <el-button link size="small" type="primary" @click="copyText(currentTimestamp.timestamp_ms)">
                <el-icon><CopyDocument /></el-icon> Copy Timestamp (ms)
              </el-button>
              <el-button link size="small" type="primary" @click="copyText(currentTimestamp.datetime)">
                <el-icon><CopyDocument /></el-icon> Copy ISO
              </el-button>
            </div>

            <h4 class="section-title" style="margin-top: 30px;">{{ $t('tools.timestamp.label.multiTimezone') }}</h4>
            <el-alert
              :title="$t('tools.timestamp.label.currentTimezone')"
              :description="$t('tools.timestamp.label.detectedTimezone') + ': ' + currentTimestamp.current_timezone"
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

      <el-tab-pane :label="$t('tools.timestamp.tab.convertTimestamp')" name="convert">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.timestamp.label.inputTimestamp') }}</h4>
            <el-input-number
              v-model="timestampInput"
              :min="0"
              :precision="0"
              :placeholder="$t('tools.timestamp.label.inputTimestamp') + '...'"
              style="width: 100%;"
            />
            <el-radio-group v-model="timestampType" style="margin-top: 10px;">
              <el-radio label="seconds">{{ $t('tools.timestamp.label.seconds') }}</el-radio>
              <el-radio label="milliseconds">{{ $t('tools.timestamp.label.milliseconds') }}</el-radio>
            </el-radio-group>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="convertTimestamp" :loading="converting">
              {{ $t('tools.timestamp.label.convert') }}
            </el-button>
          </div>
          <div class="output-section" v-if="convertedTimestamp">
            <h4 class="section-title">{{ $t('tools.timestamp.label.convertResult') }}</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item :label="$t('tools.timestamp.label.timestampSeconds')">
                {{ convertedTimestamp.timestamp }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.timestampMillis')">
                {{ convertedTimestamp.timestamp_ms }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.isoFormat')">
                {{ convertedTimestamp.datetime }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.beijingTime')">
                {{ convertedTimestamp.formatted.beijing }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.localTime')">
                {{ convertedTimestamp.formatted.local }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.utcTime')">
                {{ convertedTimestamp.formatted.utc }}
              </el-descriptions-item>
            </el-descriptions>
            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(convertedTimestamp.timestamp)">
                <el-icon><CopyDocument /></el-icon> Copy Timestamp
              </el-button>
              <el-button link size="small" type="primary" @click="copyText(convertedTimestamp.datetime)">
                <el-icon><CopyDocument /></el-icon> Copy ISO
              </el-button>
              <el-button link size="small" type="primary" @click="copyText(convertedTimestamp.formatted.beijing)">
                <el-icon><CopyDocument /></el-icon> Copy Beijing Time
              </el-button>
              <el-button link size="small" type="primary" @click="copyText(convertedTimestamp.formatted.local)">
                <el-icon><CopyDocument /></el-icon> Copy Local Time
              </el-button>
              <el-button link size="small" type="primary" @click="copyText(convertedTimestamp.formatted.utc)">
                <el-icon><CopyDocument /></el-icon> Copy UTC Time
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.timestamp.tab.parseDatetime')" name="parse">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.timestamp.label.inputDatetime') }}</h4>
            <el-input
              v-model="datetimeString"
              :placeholder="$t('tools.timestamp.label.inputDatetime') + '...'"
              style="width: 100%; margin-bottom: 10px;"
            />
            <el-input
              v-model="formatString"
              :placeholder="$t('tools.timestamp.label.formatString') + ' (%Y-%m-%d %H:%M:%S)'"
              style="width: 100%;"
            />
          </div>
          <div class="action-section">
            <el-button type="primary" @click="parseDatetime" :loading="parsing">
              {{ $t('tools.timestamp.label.parse') }}
            </el-button>
          </div>
          <div class="output-section" v-if="parsedResult">
            <h4 class="section-title">{{ $t('tools.timestamp.label.parseResult') }}</h4>
            <el-descriptions :column="descColumn" border>
              <el-descriptions-item :label="$t('tools.timestamp.label.timestampSeconds')">
                {{ parsedResult.timestamp }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.timestampMillis')">
                {{ parsedResult.timestamp_ms }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.isoFormat')">
                {{ parsedResult.datetime }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.year')">
                {{ parsedResult.parsed.year }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.month')">
                {{ parsedResult.parsed.month }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.day')">
                {{ parsedResult.parsed.day }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.hour')">
                {{ parsedResult.parsed.hour }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.minute')">
                {{ parsedResult.parsed.minute }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.second')">
                {{ parsedResult.parsed.second }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.weekday')" :span="2">
                {{ parsedResult.parsed.weekday }} ({{ parsedResult.parsed.isoweekday }})
              </el-descriptions-item>
            </el-descriptions>
            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(parsedResult.timestamp)">
                <el-icon><CopyDocument /></el-icon> Copy Timestamp
              </el-button>
              <el-button link size="small" type="primary" @click="copyText(parsedResult.timestamp_ms)">
                <el-icon><CopyDocument /></el-icon> Copy Timestamp (ms)
              </el-button>
              <el-button link size="small" type="primary" @click="copyText(parsedResult.datetime)">
                <el-icon><CopyDocument /></el-icon> Copy ISO
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.timestamp.tab.timeOffset')" name="add-time">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.timestamp.label.baseTime') }}</h4>
            <el-input
              v-model="addTimeBaseTime"
              :placeholder="$t('tools.timestamp.label.baseTime') + '...'"
              style="width: 100%; margin-bottom: 10px;"
            />
            <el-radio-group v-model="addTimeType" style="margin-bottom: 10px;">
              <el-radio label="timestamp">{{ $t('tools.timestamp.label.timestamp') }}</el-radio>
              <el-radio label="datetime_string">{{ $t('tools.timestamp.label.datetimeString') }}</el-radio>
            </el-radio-group>
            <el-input
              v-model="addTimeFormat"
              :placeholder="$t('tools.timestamp.label.formatString') + ' (%Y-%m-%d %H:%M:%S)'"
              style="width: 100%; margin-bottom: 15px;"
            />

            <h4 class="section-title">{{ $t('tools.timestamp.label.timeOffset') }}</h4>
            <div v-for="(item, index) in addTimeAdditions" :key="index" class="addition-row">
              <el-select v-model="item.unit" :placeholder="$t('tools.timestamp.label.selectUnit')" style="width: 160px;">
                <el-option :label="$t('tools.timestamp.label.yearUnit')" value="years" />
                <el-option :label="$t('tools.timestamp.label.monthUnit')" value="months" />
                <el-option :label="$t('tools.timestamp.label.weekUnit')" value="weeks" />
                <el-option :label="$t('tools.timestamp.label.dayUnit')" value="days" />
                <el-option :label="$t('tools.timestamp.label.hourUnit')" value="hours" />
                <el-option :label="$t('tools.timestamp.label.minuteUnit')" value="minutes" />
                <el-option :label="$t('tools.timestamp.label.secondUnit')" value="seconds" />
              </el-select>
              <el-input-number
                v-model="item.amount"
                :precision="0"
                :placeholder="$t('tools.timestamp.label.amount')"
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
              {{ $t('tools.timestamp.label.addOffset') }}
            </el-button>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="addTime" :loading="addTimeLoading">
              {{ $t('tools.timestamp.label.calcResult') }}
            </el-button>
          </div>
          <div class="output-section" v-if="addTimeResult">
            <h4 class="section-title">{{ $t('tools.timestamp.label.calcResult') }}</h4>
            <el-descriptions :column="descColumn" border>
              <el-descriptions-item :label="$t('tools.timestamp.label.originalTime')">
                {{ addTimeResult.original_time }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.resultTimestamp')">
                {{ addTimeResult.result_timestamp }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timestamp.label.resultDatetime')" :span="2">
                {{ addTimeResult.result_datetime }}
              </el-descriptions-item>
            </el-descriptions>
            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(addTimeResult.result_timestamp)">
                <el-icon><CopyDocument /></el-icon> Copy Result Timestamp
              </el-button>
              <el-button link size="small" type="primary" @click="copyText(addTimeResult.result_datetime)">
                <el-icon><CopyDocument /></el-icon> Copy Result Datetime
              </el-button>
            </div>
            <h4 class="section-title" style="margin-top: 20px;">{{ $t('tools.timestamp.label.operationList') }}</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item
                v-for="(op, index) in addTimeResult.operations"
                :key="index"
                :label="$t('tools.timestamp.label.operationList') + ' ' + (index + 1)"
              >
                {{ op }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.timestamp.tab.batchCalc')" name="batch-calculate">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.timestamp.label.batchTimeInput') }}</h4>
            <el-input
              v-model="batchBaseTimes"
              type="textarea"
              :rows="6"
              :placeholder="$t('tools.timestamp.label.batchTimeInput') + '...'"
              style="width: 100%; margin-bottom: 15px;"
            />
            <el-row :gutter="15">
              <el-col :xs="24" :sm="12" :md="6">
                <div class="field-label">{{ $t('tools.timestamp.label.operationType') }}</div>
                <el-select v-model="batchOperation" style="width: 100%;">
                  <el-option :label="$t('tools.timestamp.label.addSub')" value="add" />
                  <el-option :label="$t('tools.timestamp.label.subtract')" value="subtract" />
                </el-select>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <div class="field-label">{{ $t('tools.timestamp.label.unit') }}</div>
                <el-select v-model="batchUnit" style="width: 100%;">
                  <el-option :label="$t('tools.timestamp.label.yearUnit')" value="years" />
                  <el-option :label="$t('tools.timestamp.label.monthUnit')" value="months" />
                  <el-option :label="$t('tools.timestamp.label.weekUnit')" value="weeks" />
                  <el-option :label="$t('tools.timestamp.label.dayUnit')" value="days" />
                  <el-option :label="$t('tools.timestamp.label.hourUnit')" value="hours" />
                  <el-option :label="$t('tools.timestamp.label.minuteUnit')" value="minutes" />
                  <el-option :label="$t('tools.timestamp.label.secondUnit')" value="seconds" />
                </el-select>
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <div class="field-label">{{ $t('tools.timestamp.label.amount') }}</div>
                <el-input-number
                  v-model="batchAmount"
                  :precision="0"
                  style="width: 100%;"
                />
              </el-col>
              <el-col :xs="24" :sm="12" :md="6">
                <div class="field-label">{{ $t('tools.timestamp.label.inputType') }}</div>
                <el-select v-model="batchType" style="width: 100%;">
                  <el-option :label="$t('tools.timestamp.label.timestamp')" value="timestamp" />
                  <el-option :label="$t('tools.timestamp.label.datetimeString')" value="datetime_string" />
                </el-select>
              </el-col>
            </el-row>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="batchCalculate" :loading="batchLoading">
              {{ $t('tools.timestamp.label.batchCalc') }}
            </el-button>
          </div>
          <div class="output-section" v-if="batchResults && batchResults.length > 0">
            <h4 class="section-title">{{ $t('tools.timestamp.label.calcResult') }}</h4>
            <el-table :data="batchResults" border stripe style="width: 100%;">
              <el-table-column type="index" :label="$t('tools.timestamp.label.index')" width="70" align="center" />
              <el-table-column prop="original" :label="$t('tools.timestamp.label.originalTime')" min-width="180" />
              <el-table-column prop="result_timestamp" :label="$t('tools.timestamp.label.resultTimestamp')" min-width="160" />
              <el-table-column prop="result_datetime" :label="$t('tools.timestamp.label.resultDatetime')" min-width="200" />
            </el-table>
            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(batchResults.map(r => r.result_timestamp + '  ' + r.result_datetime).join('\n'))">
                <el-icon><CopyDocument /></el-icon> Copy All Results
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.timestamp.tab.formatRef')" name="formats">
        <div class="tool-section">
          <div class="action-section">
            <el-button type="primary" @click="fetchFormats" :loading="formatsLoading">
              {{ $t('tools.timestamp.label.getFormatRef') }}
            </el-button>
          </div>
          <div class="output-section" v-if="formatsList && formatsList.length > 0">
            <h4 class="section-title">{{ $t('tools.timestamp.label.formatRefTitle') }}</h4>
            <el-table :data="formatsList" border stripe style="width: 100%;">
              <el-table-column prop="format_name" :label="$t('tools.timestamp.label.formatName')" min-width="200" />
              <el-table-column prop="format_pattern" :label="$t('tools.timestamp.label.formatPattern')" min-width="300" />
            </el-table>
            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(formatsList.map(f => f.format_name + ': ' + f.format_pattern).join('\n'))">
                <el-icon><CopyDocument /></el-icon> Copy All Formats
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Clock, CopyDocument, Delete } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'
import { useDeviceStore } from '@/stores/device.js'

export default {
  name: 'TimestampTools',
  components: {
    Clock,
    CopyDocument,
    Delete,
    ToolPage
  },
  data() {
    const deviceStore = useDeviceStore()
    return {
      deviceStore,
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
      return this.deviceStore.isMobile ? 1 : 2
    }
  },
  methods: {
    async getCurrentTimestamp() {
      this.loading = true
      try {
        const response = await axios.get('/api/timestamp-tools/current')
        if (response.data.success) {
          this.currentTimestamp = response.data
          ElMessage.success(this.$t('tools.timestamp.message.getSuccess'))
        } else {
          ElMessage.error(this.$t('tools.timestamp.message.getFail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.timestamp.message.getFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.loading = false
      }
    },

    async convertTimestamp() {
      if (this.timestampInput === null || this.timestampInput < 0) {
        ElMessage.warning(this.$t('tools.timestamp.message.inputTimestampRequired'))
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
          ElMessage.success(this.$t('tools.timestamp.message.convertSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.timestamp.message.convertFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.converting = false
      }
    },

    async parseDatetime() {
      if (!this.datetimeString) {
        ElMessage.warning(this.$t('tools.timestamp.message.inputDatetimeRequired'))
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
          ElMessage.success(this.$t('tools.timestamp.message.parseSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.timestamp.message.parseFail') + ': ' + error.response?.data?.error || error.message)
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
        ElMessage.warning(this.$t('tools.timestamp.message.inputBaseTimeRequired'))
        return
      }
      if (this.addTimeAdditions.some(item => item.amount === null || item.amount === undefined)) {
        ElMessage.warning(this.$t('tools.timestamp.message.fillAllOffsetValues'))
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
          ElMessage.success(this.$t('tools.timestamp.message.calcSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.timestamp.message.calcFail') + ': ' + error.response?.data?.error || error.message)
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
        ElMessage.warning(this.$t('tools.timestamp.message.inputAtLeastOneTime'))
        return
      }
      if (this.batchAmount === null || this.batchAmount === undefined) {
        ElMessage.warning(this.$t('tools.timestamp.message.fillAmount'))
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
          ElMessage.success(this.$t('tools.timestamp.message.batchCalcSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.timestamp.message.batchCalcFail') + ': ' + error.response?.data?.error || error.message)
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
          ElMessage.success(this.$t('tools.timestamp.message.getSuccess'))
        } else {
          ElMessage.error(this.$t('tools.timestamp.message.getFail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.timestamp.message.getFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.formatsLoading = false
      }
    },

    // 复制文本到剪贴板
    copyText(text) {
      const value = String(text)
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(value).then(() => {
          ElMessage.success(this.$t('common.copySuccess'))
        }).catch(() => {
          this._fallbackCopy(value)
        })
      } else {
        this._fallbackCopy(value)
      }
    },

    _fallbackCopy(text) {
      const textarea = document.createElement('textarea')
      textarea.value = text
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      try {
        document.execCommand('copy')
        ElMessage.success(this.$t('common.copySuccess'))
      } catch (e) {
        ElMessage.error('Copy failed')
      }
      document.body.removeChild(textarea)
    }
  }
}
</script>

<style scoped>
/* Copy button toolbar */
.field-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

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
