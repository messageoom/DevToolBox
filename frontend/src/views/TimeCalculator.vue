<template>
  <div class="time-calculator">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><Clock /></el-icon>
          <span>时间计算器</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="时间计算" name="calculate">
          <div class="tool-section">
            <div class="input-section">
              <h4>基础时间</h4>
              <el-input-number
                v-model="baseTimestamp"
                :min="0"
                :precision="0"
                placeholder="请输入基础时间戳..."
                style="width: 100%; margin-bottom: 10px;"
              />
              <el-row :gutter="10">
                <el-col :span="8">
                  <el-select v-model="calcOperation" placeholder="操作">
                    <el-option label="加" value="add"></el-option>
                    <el-option label="减" value="subtract"></el-option>
                  </el-select>
                </el-col>
                <el-col :span="8">
                  <el-input-number
                    v-model="calcAmount"
                    :min="1"
                    :precision="0"
                    placeholder="数量"
                  />
                </el-col>
                <el-col :span="8">
                  <el-select v-model="calcUnit" placeholder="单位">
                    <el-option label="秒" value="seconds"></el-option>
                    <el-option label="分钟" value="minutes"></el-option>
                    <el-option label="小时" value="hours"></el-option>
                    <el-option label="天" value="days"></el-option>
                    <el-option label="周" value="weeks"></el-option>
                    <el-option label="月" value="months"></el-option>
                    <el-option label="年" value="years"></el-option>
                  </el-select>
                </el-col>
              </el-row>
            </div>
            <div class="action-section">
              <el-button type="primary" @click="calculateTime" :loading="calculating">
                计算
              </el-button>
            </div>
            <div class="output-section" v-if="calculatedResult">
              <h4>计算结果</h4>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="原始时间戳">
                  {{ calculatedResult.original_timestamp }}
                </el-descriptions-item>
                <el-descriptions-item label="原始时间">
                  {{ calculatedResult.original_datetime }}
                </el-descriptions-item>
                <el-descriptions-item label="结果时间戳">
                  {{ calculatedResult.result_timestamp }}
                </el-descriptions-item>
                <el-descriptions-item label="结果时间">
                  {{ calculatedResult.result_datetime }}
                </el-descriptions-item>
                <el-descriptions-item label="时间差(秒)">
                  {{ calculatedResult.difference_seconds }}
                </el-descriptions-item>
                <el-descriptions-item label="操作">
                  {{ calculatedResult.operation }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="时间差计算" name="difference">
          <div class="tool-section">
            <div class="input-section">
              <h4>时间范围</h4>
              <el-row :gutter="10">
                <el-col :span="12">
                  <el-input
                    v-model="startTime"
                    placeholder="开始时间 (时间戳或日期时间字符串)"
                  />
                </el-col>
                <el-col :span="12">
                  <el-input
                    v-model="endTime"
                    placeholder="结束时间 (时间戳或日期时间字符串)"
                  />
                </el-col>
              </el-row>
              <el-radio-group v-model="timeType" style="margin-top: 10px;">
                <el-radio label="timestamp">时间戳</el-radio>
                <el-radio label="datetime_string">日期时间字符串</el-radio>
              </el-radio-group>
            </div>
            <div class="action-section">
              <el-button type="primary" @click="calculateDifference" :loading="diffCalculating">
                计算差值
              </el-button>
            </div>
            <div class="output-section" v-if="timeDifference">
              <h4>时间差结果</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="开始时间">
                  {{ timeDifference.start_time }}
                </el-descriptions-item>
                <el-descriptions-item label="结束时间">
                  {{ timeDifference.end_time }}
                </el-descriptions-item>
                <el-descriptions-item label="总秒数">
                  {{ timeDifference.difference.total_seconds }}
                </el-descriptions-item>
                <el-descriptions-item label="天数">
                  {{ timeDifference.difference.days }}
                </el-descriptions-item>
                <el-descriptions-item label="小时">
                  {{ timeDifference.difference.hours }}
                </el-descriptions-item>
                <el-descriptions-item label="分钟">
                  {{ timeDifference.difference.minutes }}
                </el-descriptions-item>
                <el-descriptions-item label="秒">
                  {{ timeDifference.difference.seconds }}
                </el-descriptions-item>
                <el-descriptions-item label="人类可读" :span="2">
                  {{ timeDifference.difference.human_readable }}
                </el-descriptions-item>
                <el-descriptions-item label="方向" :span="2">
                  {{ timeDifference.direction === 'positive' ? '正向' : '负向' }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="工作日计算" name="business-days">
          <div class="tool-section">
            <div class="input-section">
              <h4>日期范围</h4>
              <el-row :gutter="10">
                <el-col :span="12">
                  <el-date-picker
                    v-model="startDate"
                    type="date"
                    placeholder="开始日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                  />
                </el-col>
                <el-col :span="12">
                  <el-date-picker
                    v-model="endDate"
                    type="date"
                    placeholder="结束日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                  />
                </el-col>
              </el-row>
              <el-checkbox v-model="includeWeekends" style="margin-top: 10px;">
                包含周末
              </el-checkbox>
            </div>
            <div class="action-section">
              <el-button type="primary" @click="calculateBusinessDays" :loading="businessCalculating">
                计算工作日
              </el-button>
            </div>
            <div class="output-section" v-if="businessDaysResult">
              <h4>工作日计算结果</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="开始日期">
                  {{ businessDaysResult.start_date }}
                </el-descriptions-item>
                <el-descriptions-item label="结束日期">
                  {{ businessDaysResult.end_date }}
                </el-descriptions-item>
                <el-descriptions-item label="工作日数">
                  {{ businessDaysResult.business_days }}
                </el-descriptions-item>
                <el-descriptions-item label="总天数">
                  {{ businessDaysResult.total_days }}
                </el-descriptions-item>
                <el-descriptions-item label="周末天数">
                  {{ businessDaysResult.weekend_days }}
                </el-descriptions-item>
                <el-descriptions-item label="节假日数">
                  {{ businessDaysResult.holiday_days }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Clock } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'TimeCalculator',
  components: {
    Clock
  },
  data() {
    return {
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
  methods: {
    async calculateTime() {
      if (this.baseTimestamp === null || this.baseTimestamp < 0) {
        ElMessage.warning('请输入有效的基础时间戳')
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
          ElMessage.success('计算成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('计算失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.calculating = false
      }
    },

    async calculateDifference() {
      if (!this.startTime || !this.endTime) {
        ElMessage.warning('请输入开始时间和结束时间')
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
          ElMessage.success('计算成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('计算失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.diffCalculating = false
      }
    },

    async calculateBusinessDays() {
      if (!this.startDate || !this.endDate) {
        ElMessage.warning('请选择开始日期和结束日期')
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
          ElMessage.success('计算成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('计算失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.businessCalculating = false
      }
    }
  }
}
</script>

<style scoped>
.time-calculator {
  padding: 20px;
}

.tool-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-section, .output-section {
  flex: 1;
}

.input-section h4, .output-section h4 {
  margin-bottom: 10px;
  color: #333;
  font-weight: bold;
}

.action-section {
  text-align: center;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-icon {
  margin-right: 8px;
  font-size: 18px;
}

.card-header span {
  font-weight: bold;
}
</style>
