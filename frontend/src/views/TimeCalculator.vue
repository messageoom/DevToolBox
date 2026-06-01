<template>
  <ToolPage :title="$t('tools.timeCalc.title')" :icon="Calendar">
    <el-tabs v-model="activeTab">
      <el-tab-pane :label="$t('tools.timeCalc.tab.timeCalc')" name="calculate">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.timeCalc.label.baseTime') }}</h4>
            <el-input-number
              v-model="baseTimestamp"
              :min="0"
              :precision="0"
              :placeholder="$t('tools.timeCalc.label.baseTime') + '...'"
              style="width: 100%; margin-bottom: 10px;"
            />
            <el-row :gutter="10">
              <el-col :xs="24" :sm="8" :md="8">
                <el-select v-model="calcOperation" :placeholder="$t('tools.timeCalc.label.operation')" style="width: 100%;">
                  <el-option :label="$t('tools.timeCalc.label.add')" value="add"></el-option>
                  <el-option :label="$t('tools.timeCalc.label.subtract')" value="subtract"></el-option>
                </el-select>
              </el-col>
              <el-col :xs="24" :sm="8" :md="8">
                <el-input-number
                  v-model="calcAmount"
                  :min="1"
                  :precision="0"
                  :placeholder="$t('tools.timeCalc.label.amount')"
                  style="width: 100%;"
                />
              </el-col>
              <el-col :xs="24" :sm="8" :md="8">
                <el-select v-model="calcUnit" :placeholder="$t('tools.timeCalc.label.unit')" style="width: 100%;">
                  <el-option :label="$t('tools.timeCalc.label.seconds')" value="seconds"></el-option>
                  <el-option :label="$t('tools.timeCalc.label.minutes')" value="minutes"></el-option>
                  <el-option :label="$t('tools.timeCalc.label.hours')" value="hours"></el-option>
                  <el-option :label="$t('tools.timeCalc.label.days')" value="days"></el-option>

                </el-select>
              </el-col>
            </el-row>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="calculateTime" :loading="calculating">
              {{ $t('tools.timeCalc.label.calc') }}
            </el-button>
          </div>
          <div class="output-section" v-if="calculatedResult">
            <h4 class="section-title">{{ $t('tools.timeCalc.label.calcResult') }}</h4>
            <el-descriptions :column="1" border>
              <el-descriptions-item :label="$t('tools.timeCalc.label.originalTimestamp')">
                {{ calculatedResult.original_timestamp }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.originalTime')">
                {{ calculatedResult.original_datetime }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.resultTimestamp')">
                {{ calculatedResult.result_timestamp }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.resultTime')">
                {{ calculatedResult.result_datetime }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.timeDiffSeconds')">
                {{ calculatedResult.difference_seconds }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.operation')">
                {{ calculatedResult.operation }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.timeCalc.tab.timeDiff')" name="difference">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.timeCalc.label.timeRange') }}</h4>
            <el-row :gutter="10">
              <el-col :xs="24" :sm="12" :md="12">
                <el-input
                  v-model="startTime"
                  :placeholder="$t('tools.timeCalc.label.startTime')"
                  style="width: 100%;"
                />
              </el-col>
              <el-col :xs="24" :sm="12" :md="12">
                <el-input
                  v-model="endTime"
                  :placeholder="$t('tools.timeCalc.label.endTime')"
                  style="width: 100%;"
                />
              </el-col>
            </el-row>
            <el-radio-group v-model="timeType" style="margin-top: 10px;">
              <el-radio label="timestamp">{{ $t('tools.timeCalc.label.timestamp') }}</el-radio>
              <el-radio label="datetime_string">{{ $t('tools.timeCalc.label.datetimeString') }}</el-radio>
            </el-radio-group>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="calculateDifference" :loading="diffCalculating">
              {{ $t('tools.timeCalc.label.calcDiff') }}
            </el-button>
          </div>
          <div class="output-section" v-if="timeDifference">
            <h4 class="section-title">{{ $t('tools.timeCalc.label.timeDiffResult') }}</h4>
            <el-descriptions :column="descColumn" border>
              <el-descriptions-item :label="$t('tools.timeCalc.label.startTime')">
                {{ timeDifference.start_time }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.endTime')">
                {{ timeDifference.end_time }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.totalSeconds')">
                {{ timeDifference.difference.total_seconds }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.days')">
                {{ timeDifference.difference.days }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.hours')">
                {{ timeDifference.difference.hours }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.minutes')">
                {{ timeDifference.difference.minutes }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.seconds')">
                {{ timeDifference.difference.seconds }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.humanReadable')" :span="2">
                {{ timeDifference.difference.human_readable }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.direction')" :span="2">
                {{ timeDifference.direction === 'positive' ? $t('tools.timeCalc.label.forward') : $t('tools.timeCalc.label.backward') }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.timeCalc.tab.workdayCalc')" name="business-days">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.timeCalc.label.dateRange') }}</h4>
            <el-row :gutter="10">
              <el-col :xs="24" :sm="12" :md="12">
                <el-date-picker
                  v-model="startDate"
                  type="date"
                  :placeholder="$t('tools.timeCalc.label.startDate')"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%;"
                />
              </el-col>
              <el-col :xs="24" :sm="12" :md="12">
                <el-date-picker
                  v-model="endDate"
                  type="date"
                  :placeholder="$t('tools.timeCalc.label.endDate')"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  style="width: 100%;"
                />
              </el-col>
            </el-row>
            <el-checkbox v-model="includeWeekends" style="margin-top: 10px;">
              {{ $t('tools.timeCalc.label.includeWeekends') }}
            </el-checkbox>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="calculateBusinessDays" :loading="businessCalculating">
              {{ $t('tools.timeCalc.label.calcWorkdays') }}
            </el-button>
          </div>
          <div class="output-section" v-if="businessDaysResult">
            <h4 class="section-title">{{ $t('tools.timeCalc.label.workdayResult') }}</h4>
            <el-descriptions :column="descColumn" border>
              <el-descriptions-item :label="$t('tools.timeCalc.label.startDate')">
                {{ businessDaysResult.start_date }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.endDate')">
                {{ businessDaysResult.end_date }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.workdays')">
                {{ businessDaysResult.business_days }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.totalDays')">
                {{ businessDaysResult.total_days }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.weekendDays')">
                {{ businessDaysResult.weekend_days }}
              </el-descriptions-item>
              <el-descriptions-item :label="$t('tools.timeCalc.label.holidayDays')">
                {{ businessDaysResult.holiday_days }}
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
import { Calendar } from '@element-plus/icons-vue'
import axios from 'axios'
import { useDeviceStore } from '@/stores/device.js'
import ToolPage from '@/components/ToolPage.vue'

export default {
  name: 'TimeCalculator',
  components: {
    Calendar,
    ToolPage
  },
  data() {
    const deviceStore = useDeviceStore()
    return {
      deviceStore,
      activeTab: 'calculate',
      // 时间计算相关
      baseTimestamp: null,
      calcOperation: 'add',
      calcAmount: 1,
      calcUnit: 'days',
      calculating: false,
      calculatedResult: null,
      // 时间差计算相关
      startTime: '',
      endTime: '',
      timeType: 'timestamp',
      diffCalculating: false,
      timeDifference: null,
      // 工作日计算相关
      startDate: '',
      endDate: '',
      includeWeekends: false,
      businessCalculating: false,
      businessDaysResult: null
    }
  },
  computed: {
    descColumn() {
      return window.innerWidth <= 768 ? 1 : 2
    }
  },
  methods: {
    async calculateTime() {
      if (this.baseTimestamp === null || this.baseTimestamp < 0) {
        ElMessage.warning(this.$t('tools.timeCalc.message.inputValidTimestamp'))
        return
      }

      this.calculating = true
      try {
        const response = await axios.post('/api/timestamp-tools/calculate', {
          base_timestamp: this.baseTimestamp,
          operation: this.calcOperation,
          unit: this.calcUnit,
          amount: this.calcAmount
        })

        if (response.data.success) {
          this.calculatedResult = response.data
          ElMessage.success(this.$t('tools.timeCalc.message.calcSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.timeCalc.message.calcFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.calculating = false
      }
    },

    async calculateDifference() {
      if (!this.startTime || !this.endTime) {
        ElMessage.warning(this.$t('tools.timeCalc.message.inputStartEnd'))
        return
      }

      this.diffCalculating = true
      try {
        const response = await axios.post('/api/timestamp-tools/difference', {
          start_time: this.startTime,
          end_time: this.endTime,
          type: this.timeType
        })

        if (response.data.success) {
          this.timeDifference = response.data
          ElMessage.success(this.$t('tools.timeCalc.message.calcSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.timeCalc.message.calcFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.diffCalculating = false
      }
    },

    async calculateBusinessDays() {
      if (!this.startDate || !this.endDate) {
        ElMessage.warning(this.$t('tools.timeCalc.message.selectStartEnd'))
        return
      }

      this.businessCalculating = true
      try {
        const response = await axios.post('/api/timestamp-tools/business-days', {
          start_date: this.startDate,
          end_date: this.endDate,
          include_weekends: this.includeWeekends
        })

        if (response.data.success) {
          this.businessDaysResult = response.data
          ElMessage.success(this.$t('tools.timeCalc.message.calcSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.timeCalc.message.calcFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.businessCalculating = false
      }
    }
  }
}
</script>

<style scoped>
@media (max-width: 768px) {
  .el-form-item :deep(.el-form-item__label) { width: auto !important; min-width: 70px; }
  .el-form-item :deep(.el-form-item__content) { flex: 1; }
  .action-buttons { flex-direction: column; }
  .action-buttons .el-button { width: 100%; margin-left: 0 !important; margin-top: 8px; }
  .el-row { flex-direction: column; }
  .el-col { max-width: 100% !important; flex: 0 0 100% !important; }
}
</style>
