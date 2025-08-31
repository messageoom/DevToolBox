<template>
  <div class="url-tools">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><Key /></el-icon>
          <span>URL工具</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="编码" name="encode">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入URL</h4>
              <el-input
                v-model="encodeInput"
                placeholder="请输入要编码的URL..."
                clearable
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="encodeUrl" :loading="encoding">
                编码
              </el-button>
            </div>
            <div class="output-section">
              <h4>编码结果</h4>
              <el-input
                v-model="encodeOutput"
                readonly
                placeholder="编码结果将显示在这里..."
              />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="解码" name="decode">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入编码URL</h4>
              <el-input
                v-model="decodeInput"
                placeholder="请输入要解码的URL..."
                clearable
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="decodeUrl" :loading="decoding">
                解码
              </el-button>
            </div>
            <div class="output-section">
              <h4>解码结果</h4>
              <el-input
                v-model="decodeOutput"
                readonly
                placeholder="解码结果将显示在这里..."
              />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="转HAR" name="to-har">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入URL</h4>
              <el-input
                v-model="harInput"
                placeholder="请输入要转换为HAR格式的URL..."
                clearable
              />
              <div class="method-section">
                <label>HTTP方法:</label>
                <el-select v-model="harMethod" placeholder="选择方法" style="width: 120px;">
                  <el-option label="GET" value="GET"></el-option>
                  <el-option label="POST" value="POST"></el-option>
                  <el-option label="PUT" value="PUT"></el-option>
                  <el-option label="DELETE" value="DELETE"></el-option>
                  <el-option label="PATCH" value="PATCH"></el-option>
                </el-select>
              </div>
              <div class="format-section">
                <label>输出格式:</label>
                <el-radio-group v-model="outputFormat">
                  <el-radio label="simplified">简化格式</el-radio>
                  <el-radio label="har">完整HAR</el-radio>
                </el-radio-group>
              </div>
            </div>
            <div class="action-section">
              <el-button type="primary" @click="urlToHar" :loading="converting">
                转换为HAR
              </el-button>
              <el-button type="success" @click="generateCurl" :loading="generatingCurl" :disabled="!harOutput">
                生成Curl
              </el-button>
            </div>
            <div class="output-section">
              <h4>HAR格式结果</h4>
              <el-input
                v-model="harOutput"
                type="textarea"
                :rows="30"
                readonly
                placeholder="HAR格式结果将显示在这里..."
                style="font-family: 'Courier New', monospace; font-size: 12px;"
              />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="API请求" name="api-request">
          <div class="tool-section">
            <div class="input-section">
              <h4>请求配置</h4>
              <div class="request-config">
                <div class="url-section">
                  <el-input
                    v-model="apiUrl"
                    placeholder="请输入API URL..."
                    clearable
                    style="flex: 1;"
                  />
                  <el-select v-model="apiMethod" placeholder="方法" style="width: 100px; margin-left: 10px;">
                    <el-option label="GET" value="GET"></el-option>
                    <el-option label="POST" value="POST"></el-option>
                    <el-option label="PUT" value="PUT"></el-option>
                    <el-option label="DELETE" value="DELETE"></el-option>
                    <el-option label="PATCH" value="PATCH"></el-option>
                    <el-option label="HEAD" value="HEAD"></el-option>
                    <el-option label="OPTIONS" value="OPTIONS"></el-option>
                  </el-select>
                </div>

                <div class="headers-section">
                  <h5>请求头</h5>
                  <div v-for="(header, index) in apiHeaders" :key="index" class="header-item">
                    <el-input
                      v-model="header.name"
                      placeholder="Header名称"
                      style="width: 45%;"
                    />
                    <el-input
                      v-model="header.value"
                      placeholder="Header值"
                      style="width: 45%; margin-left: 10px;"
                    />
                    <el-button
                      type="danger"
                      size="small"
                      @click="removeHeader(index)"
                      style="margin-left: 10px;"
                      :disabled="apiHeaders.length === 1"
                    >
                      删除
                    </el-button>
                  </div>
                  <el-button type="primary" size="small" @click="addHeader" style="margin-top: 10px;">
                    添加Header
                  </el-button>
                </div>

                <div class="body-section" v-if="['POST', 'PUT', 'PATCH'].includes(apiMethod)">
                  <h5>请求体</h5>
                  <el-input
                    v-model="apiBody"
                    type="textarea"
                    :rows="6"
                    placeholder="请输入请求体内容..."
                    style="font-family: 'Courier New', monospace; font-size: 12px;"
                  />
                </div>
              </div>
            </div>

            <div class="action-section">
              <el-button type="primary" @click="sendApiRequest" :loading="sendingRequest">
                发送请求
              </el-button>
              <el-button @click="clearApiResult" :disabled="!apiResponse">
                清空结果
              </el-button>
            </div>

            <div class="output-section" v-if="apiResponse">
              <h4>响应结果</h4>
              <div class="response-info">
                <el-row :gutter="20">
                  <el-col :span="6">
                    <div class="response-item">
                      <strong>状态码:</strong>
                      <span :class="getStatusClass(apiResponse.response.status_code)">
                        {{ apiResponse.response.status_code }} {{ apiResponse.response.status_text }}
                      </span>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="response-item">
                      <strong>响应时间:</strong>
                      <span>{{ apiResponse.response.response_time }}ms</span>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="response-item">
                      <strong>内容长度:</strong>
                      <span>{{ apiResponse.response.content_length }} bytes</span>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="response-item">
                      <strong>内容类型:</strong>
                      <span>{{ apiResponse.response.body_type || 'unknown' }}</span>
                    </div>
                  </el-col>
                </el-row>
              </div>

              <div class="response-tabs">
                <el-tabs v-model="responseTab">
                  <el-tab-pane label="响应体" name="body">
                    <el-input
                      v-model="responseBodyText"
                      type="textarea"
                      :rows="15"
                      readonly
                      style="font-family: 'Courier New', monospace; font-size: 12px;"
                    />
                  </el-tab-pane>
                  <el-tab-pane label="响应头" name="headers">
                    <div class="headers-display">
                      <div v-for="(value, key) in apiResponse.response.headers" :key="key" class="header-display-item">
                        <strong>{{ key }}:</strong> {{ value }}
                      </div>
                    </div>
                  </el-tab-pane>
                  <el-tab-pane label="请求信息" name="request">
                    <div class="request-info">
                      <h5>请求详情</h5>
                      <p><strong>方法:</strong> {{ apiResponse.request.method }}</p>
                      <p><strong>URL:</strong> {{ apiResponse.request.url }}</p>
                      <p><strong>请求头:</strong></p>
                      <div class="headers-display">
                        <div v-for="(value, key) in apiResponse.request.headers" :key="key" class="header-display-item">
                          <strong>{{ key }}:</strong> {{ value }}
                        </div>
                      </div>
                      <p v-if="apiResponse.request.body"><strong>请求体:</strong></p>
                      <pre v-if="apiResponse.request.body" class="request-body">{{ apiResponse.request.body }}</pre>
                    </div>
                  </el-tab-pane>
                </el-tabs>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="Curl请求" name="curl-request">
          <div class="tool-section">
            <div class="input-section">
              <h4>Curl命令</h4>
              <el-input
                v-model="curlCommand"
                type="textarea"
                :rows="8"
                placeholder='请输入curl命令，例如：&#10;curl -X POST "https://api.example.com/users" \&#10;  -H "Content-Type: application/json" \&#10;  -d "{\"name\": \"test\", \"email\": \"test@example.com\"}"'
                style="font-family: 'Courier New', monospace; font-size: 12px;"
              />
            </div>

            <div class="action-section">
              <el-button type="info" @click="parseCurlCommand" :loading="parsingCurl">
                解析Curl
              </el-button>
              <el-button type="primary" @click="executeCurlCommand" :loading="executingCurl">
                执行Curl
              </el-button>
              <el-button @click="clearCurlResult" :disabled="!curlResponse">
                清空结果
              </el-button>
            </div>

            <div class="output-section" v-if="curlParsed">
              <h4>解析结果</h4>
              <div class="parsed-info">
                <el-row :gutter="20">
                  <el-col :span="6">
                    <div class="parsed-item">
                      <strong>方法:</strong> {{ curlParsed.method }}
                    </div>
                  </el-col>
                  <el-col :span="18">
                    <div class="parsed-item">
                      <strong>URL:</strong> {{ curlParsed.url }}
                    </div>
                  </el-col>
                </el-row>
                <div v-if="Object.keys(curlParsed.headers).length > 0" class="parsed-headers">
                  <strong>请求头:</strong>
                  <div class="headers-display">
                    <div v-for="(value, key) in curlParsed.headers" :key="key" class="header-display-item">
                      <strong>{{ key }}:</strong> {{ value }}
                    </div>
                  </div>
                </div>
                <div v-if="curlParsed.data" class="parsed-data">
                  <strong>请求数据:</strong>
                  <pre class="request-body">{{ curlParsed.data }}</pre>
                </div>
              </div>
            </div>

            <div class="output-section" v-if="curlResponse">
              <h4>执行结果</h4>
              <div class="response-info">
                <el-row :gutter="20">
                  <el-col :span="6">
                    <div class="response-item">
                      <strong>状态码:</strong>
                      <span :class="getStatusClass(curlResponse.response.status_code)">
                        {{ curlResponse.response.status_code }} {{ curlResponse.response.status_text }}
                      </span>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="response-item">
                      <strong>响应时间:</strong>
                      <span>{{ curlResponse.response.response_time }}ms</span>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="response-item">
                      <strong>内容长度:</strong>
                      <span>{{ curlResponse.response.content_length }} bytes</span>
                    </div>
                  </el-col>
                  <el-col :span="6">
                    <div class="response-item">
                      <strong>内容类型:</strong>
                      <span>{{ curlResponse.response.body_type || 'unknown' }}</span>
                    </div>
                  </el-col>
                </el-row>
              </div>

              <div class="response-tabs">
                <el-tabs v-model="curlResponseTab">
                  <el-tab-pane label="响应体" name="body">
                    <el-input
                      v-model="curlResponseBodyText"
                      type="textarea"
                      :rows="15"
                      readonly
                      style="font-family: 'Courier New', monospace; font-size: 12px;"
                    />
                  </el-tab-pane>
                  <el-tab-pane label="响应头" name="headers">
                    <div class="headers-display">
                      <div v-for="(value, key) in curlResponse.response.headers" :key="key" class="header-display-item">
                        <strong>{{ key }}:</strong> {{ value }}
                      </div>
                    </div>
                  </el-tab-pane>
                  <el-tab-pane label="Curl命令" name="command">
                    <div class="curl-command-display">
                      <h5>原始Curl命令</h5>
                      <pre class="curl-command">{{ curlResponse.curl_command }}</pre>
                      <h5>解析后的请求</h5>
                      <div class="parsed-request">
                        <p><strong>方法:</strong> {{ curlResponse.parsed_request.method }}</p>
                        <p><strong>URL:</strong> {{ curlResponse.parsed_request.url }}</p>
                        <p v-if="Object.keys(curlResponse.parsed_request.headers).length > 0"><strong>请求头:</strong></p>
                        <div v-if="Object.keys(curlResponse.parsed_request.headers).length > 0" class="headers-display">
                          <div v-for="(value, key) in curlResponse.parsed_request.headers" :key="key" class="header-display-item">
                            <strong>{{ key }}:</strong> {{ value }}
                          </div>
                        </div>
                        <p v-if="curlResponse.parsed_request.data"><strong>请求数据:</strong></p>
                        <pre v-if="curlResponse.parsed_request.data" class="request-body">{{ curlResponse.parsed_request.data }}</pre>
                      </div>
                    </div>
                  </el-tab-pane>
                </el-tabs>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Key } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'UrlTools',
  components: {
    Key
  },
  data() {
    return {
      activeTab: 'encode',
      encodeInput: '',
      encodeOutput: '',
      encoding: false,
      decodeInput: '',
      decodeOutput: '',
      decoding: false,
      harInput: '',
      harOutput: '',
      harMethod: 'GET',
      outputFormat: 'simplified',
      converting: false,
      generatingCurl: false,
      curlCommand: '',
      currentHarData: null,
      showCurlDialog: false,
      apiUrl: '',
      apiMethod: 'GET',
      apiHeaders: [{ name: '', value: '' }],
      apiBody: '',
      apiResponse: null,
      responseBodyText: '',
      responseTab: 'body',
      sendingRequest: false,
      curlCommand: '',
      curlParsed: null,
      curlResponse: null,
      curlResponseBodyText: '',
      curlResponseTab: 'body',
      parsingCurl: false,
      executingCurl: false
    }
  },
  methods: {
    async encodeUrl() {
      if (!this.encodeInput.trim()) {
        ElMessage.warning('请输入要编码的URL')
        return
      }

      this.encoding = true
      try {
        const response = await axios.post('/api/url-tools/encode', {
          url: this.encodeInput
        })

        if (response.data.success) {
          this.encodeOutput = response.data.encoded_url
          ElMessage.success('编码成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('编码失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.encoding = false
      }
    },

    async decodeUrl() {
      if (!this.decodeInput.trim()) {
        ElMessage.warning('请输入要解码的URL')
        return
      }

      this.decoding = true
      try {
        const response = await axios.post('/api/url-tools/decode', {
          encoded_url: this.decodeInput
        })

        if (response.data.success) {
          this.decodeOutput = response.data.decoded_url
          ElMessage.success('解码成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('解码失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.decoding = false
      }
    },

    async urlToHar() {
      if (!this.harInput.trim()) {
        ElMessage.warning('请输入要转换为HAR格式的URL')
        return
      }

      this.converting = true
      try {
        const response = await axios.post('/api/url-tools/to-har', {
          url: this.harInput,
          method: this.harMethod
        })

        if (response.data.success) {
          if (this.outputFormat === 'simplified') {
            this.harOutput = response.data.simplified_json
          } else {
            this.harOutput = response.data.har_json
          }
          // 保存HAR数据用于生成curl
          this.currentHarData = response.data.har
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

    async generateCurl() {
      if (!this.currentHarData) {
        ElMessage.warning('请先转换为HAR格式')
        return
      }

      this.generatingCurl = true
      try {
        const response = await axios.post('/api/url-tools/generate-curl', {
          har: this.currentHarData
        })

        if (response.data.success) {
          this.curlCommand = response.data.curl_command
          // 复制到剪贴板
          if (navigator.clipboard) {
            await navigator.clipboard.writeText(this.curlCommand)
            ElMessage.success('Curl命令已生成并复制到剪贴板')
          } else {
            ElMessage.success('Curl命令已生成')
          }

          // 显示curl命令（可以考虑在新窗口或弹窗中显示）
          this.showCurlDialog = true
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('生成Curl失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.generatingCurl = false
      }
    },

    async sendApiRequest() {
      if (!this.apiUrl.trim()) {
        ElMessage.warning('请输入API URL')
        return
      }

      this.sendingRequest = true
      try {
        // 构建请求头对象
        const headers = {}
        this.apiHeaders.forEach(header => {
          if (header.name.trim() && header.value.trim()) {
            headers[header.name.trim()] = header.value.trim()
          }
        })

        const response = await axios.post('/api/url-tools/send-request', {
          url: this.apiUrl,
          method: this.apiMethod,
          headers: headers,
          body: this.apiBody
        })

        if (response.data.success) {
          this.apiResponse = response.data
          // 格式化响应体文本
          if (response.data.response.body_type === 'json') {
            this.responseBodyText = JSON.stringify(response.data.response.body, null, 2)
          } else {
            this.responseBodyText = response.data.response.body || ''
          }
          ElMessage.success('请求发送成功')
        } else {
          ElMessage.error(response.data.error || '请求失败')
        }
      } catch (error) {
        const errorMessage = error.response?.data?.error || error.message
        ElMessage.error('请求失败: ' + errorMessage)
      } finally {
        this.sendingRequest = false
      }
    },

    addHeader() {
      this.apiHeaders.push({ name: '', value: '' })
    },

    removeHeader(index) {
      if (this.apiHeaders.length > 1) {
        this.apiHeaders.splice(index, 1)
      }
    },

    clearApiResult() {
      this.apiResponse = null
      this.responseBodyText = ''
      this.responseTab = 'body'
    },

    getStatusClass(statusCode) {
      if (statusCode >= 200 && statusCode < 300) {
        return 'status-success'
      } else if (statusCode >= 300 && statusCode < 400) {
        return 'status-redirect'
      } else if (statusCode >= 400 && statusCode < 500) {
        return 'status-client-error'
      } else if (statusCode >= 500) {
        return 'status-server-error'
      }
      return 'status-unknown'
    },

    async parseCurlCommand() {
      if (!this.curlCommand.trim()) {
        ElMessage.warning('请输入curl命令')
        return
      }

      this.parsingCurl = true
      try {
        const response = await axios.post('/api/url-tools/parse-curl', {
          curl_command: this.curlCommand
        })

        if (response.data.success) {
          this.curlParsed = response.data.parsed
          ElMessage.success('解析成功')
        } else {
          ElMessage.error(response.data.error || '解析失败')
        }
      } catch (error) {
        const errorMessage = error.response?.data?.error || error.message
        ElMessage.error('解析失败: ' + errorMessage)
      } finally {
        this.parsingCurl = false
      }
    },

    async executeCurlCommand() {
      if (!this.curlCommand.trim()) {
        ElMessage.warning('请输入curl命令')
        return
      }

      this.executingCurl = true
      try {
        const response = await axios.post('/api/url-tools/execute-curl', {
          curl_command: this.curlCommand
        })

        if (response.data.success) {
          this.curlResponse = response.data
          // 格式化响应体文本
          if (response.data.response.body_type === 'json') {
            this.curlResponseBodyText = JSON.stringify(response.data.response.body, null, 2)
          } else {
            this.curlResponseBodyText = response.data.response.body || ''
          }
          ElMessage.success('执行成功')
        } else {
          ElMessage.error(response.data.error || '执行失败')
        }
      } catch (error) {
        const errorMessage = error.response?.data?.error || error.message
        ElMessage.error('执行失败: ' + errorMessage)
      } finally {
        this.executingCurl = false
      }
    },

    clearCurlResult() {
      this.curlParsed = null
      this.curlResponse = null
      this.curlResponseBodyText = ''
      this.curlResponseTab = 'body'
    }
  }
}
</script>

<style scoped>
.url-tools {
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

.method-section {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.method-section label {
  font-weight: bold;
  color: #333;
}

.format-section {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.format-section label {
  font-weight: bold;
  color: #333;
}

/* API请求相关样式 */
.request-config {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.url-section {
  display: flex;
  align-items: center;
}

.headers-section, .body-section {
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  background-color: #fafafa;
}

.headers-section h5, .body-section h5 {
  margin: 0 0 10px 0;
  color: #333;
  font-weight: bold;
}

.header-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.response-info {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.response-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.response-item strong {
  color: #666;
  font-size: 12px;
}

.status-success {
  color: #67c23a;
  font-weight: bold;
}

.status-redirect {
  color: #e6a23c;
  font-weight: bold;
}

.status-client-error {
  color: #f56c6c;
  font-weight: bold;
}

.status-server-error {
  color: #f56c6c;
  font-weight: bold;
}

.status-unknown {
  color: #909399;
  font-weight: bold;
}

.headers-display {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.header-display-item {
  padding: 5px 0;
  border-bottom: 1px solid #f0f0f0;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.header-display-item:last-child {
  border-bottom: none;
}

.request-info {
  padding: 15px;
}

.request-info p {
  margin: 8px 0;
  font-size: 14px;
}

.request-body {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 10px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

/* Curl相关样式 */
.parsed-info {
  background-color: #f0f9ff;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.parsed-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.parsed-item strong {
  color: #666;
  font-size: 12px;
}

.parsed-headers, .parsed-data {
  margin-top: 15px;
}

.parsed-headers strong, .parsed-data strong {
  color: #333;
  font-size: 14px;
  margin-bottom: 8px;
  display: block;
}

.curl-command-display {
  padding: 15px;
}

.curl-command-display h5 {
  margin: 0 0 10px 0;
  color: #333;
  font-weight: bold;
}

.curl-command {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 15px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.parsed-request {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 15px;
}

.parsed-request p {
  margin: 8px 0;
  font-size: 14px;
}
</style>
