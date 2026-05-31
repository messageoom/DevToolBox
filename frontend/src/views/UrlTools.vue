<template>
  <ToolPage title="URL工具" :icon="Link">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="编码" name="encode">
        <ToolSection
          input-label="输入URL"
          output-label="编码结果"
          action-text="编码"
          :loading="encoding"
          @submit="encodeUrl"
        >
          <template #input>
            <el-input
              v-model="encodeInput"
              placeholder="请输入要编码的URL..."
              clearable
            />
          </template>
          <template #output>
            <el-input
              v-model="encodeOutput"
              readonly
              placeholder="编码结果将显示在这里..."
            />
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane label="解码" name="decode">
        <ToolSection
          input-label="输入编码URL"
          output-label="解码结果"
          action-text="解码"
          :loading="decoding"
          @submit="decodeUrl"
        >
          <template #input>
            <el-input
              v-model="decodeInput"
              placeholder="请输入要解码的URL..."
              clearable
            />
          </template>
          <template #output>
            <el-input
              v-model="decodeOutput"
              readonly
              placeholder="解码结果将显示在这里..."
            />
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane label="解析URL" name="parse">
        <ToolSection
          input-label="输入URL"
          output-label="解析结果"
          action-text="解析"
          :loading="parsing"
          :has-output="!!parseResult"
          @submit="parseUrl"
        >
          <template #input>
            <el-input
              v-model="parseInput"
              placeholder="请输入要解析的URL，例如: https://example.com:8080/path?key=value#section..."
              clearable
            />
          </template>
          <template #output>
            <div v-if="parseResult" class="parse-result">
              <el-descriptions title="URL组件" :column="2" border>
                <el-descriptions-item label="Scheme">{{ parseResult.scheme || '-' }}</el-descriptions-item>
                <el-descriptions-item label="Netloc">{{ parseResult.netloc || '-' }}</el-descriptions-item>
                <el-descriptions-item label="Hostname">{{ parseResult.hostname || '-' }}</el-descriptions-item>
                <el-descriptions-item label="Port">{{ parseResult.port || '-' }}</el-descriptions-item>
                <el-descriptions-item label="Path">{{ parseResult.path || '-' }}</el-descriptions-item>
                <el-descriptions-item label="Params">{{ parseResult.params || '-' }}</el-descriptions-item>
                <el-descriptions-item label="Query">{{ parseResult.query || '-' }}</el-descriptions-item>
                <el-descriptions-item label="Fragment">{{ parseResult.fragment || '-' }}</el-descriptions-item>
                <el-descriptions-item label="Username">{{ parseResult.username || '-' }}</el-descriptions-item>
                <el-descriptions-item label="Password">{{ parseResult.password || '-' }}</el-descriptions-item>
              </el-descriptions>
              <div v-if="parseResult.query_params && Object.keys(parseResult.query_params).length > 0" class="query-params-section">
                <h5>Query参数</h5>
                <el-table :data="parseQueryParamsList" border stripe>
                  <el-table-column prop="key" label="参数名" />
                  <el-table-column prop="value" label="参数值" />
                </el-table>
              </div>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane label="构建URL" name="build">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">URL组件</h4>
            <div class="build-form">
              <div class="build-form-row">
                <label class="build-label">Scheme:</label>
                <el-select v-model="buildScheme" placeholder="选择协议" style="width: 150px;">
                  <el-option label="http" value="http"></el-option>
                  <el-option label="https" value="https"></el-option>
                  <el-option label="ftp" value="ftp"></el-option>
                </el-select>
              </div>
              <div class="build-form-row">
                <label class="build-label">Netloc:</label>
                <el-input v-model="buildNetloc" placeholder="例如: example.com:8080" clearable />
              </div>
              <div class="build-form-row">
                <label class="build-label">Path:</label>
                <el-input v-model="buildPath" placeholder="例如: /api/users" clearable />
              </div>
              <div class="build-form-row">
                <label class="build-label">Params:</label>
                <el-input v-model="buildParams" placeholder="参数" clearable />
              </div>
              <div class="build-form-row">
                <label class="build-label">Query:</label>
                <el-input v-model="buildQuery" placeholder="查询字符串" clearable />
              </div>
              <div class="build-form-row">
                <label class="build-label">Fragment:</label>
                <el-input v-model="buildFragment" placeholder="锚点" clearable />
              </div>
              <div class="query-params-builder">
                <h5>Query参数列表</h5>
                <div v-for="(param, index) in buildQueryParams" :key="index" class="header-item">
                  <el-input
                    v-model="param.key"
                    placeholder="参数名"
                    style="width: 40%;"
                  />
                  <el-input
                    v-model="param.value"
                    placeholder="参数值"
                    style="width: 40%; margin-left: 10px;"
                  />
                  <el-button
                    type="danger"
                    size="small"
                    @click="removeBuildQueryParam(index)"
                    style="margin-left: 10px;"
                    :disabled="buildQueryParams.length === 1"
                  >
                    删除
                  </el-button>
                </div>
                <el-button type="primary" size="small" @click="addBuildQueryParam" style="margin-top: 10px;">
                  添加参数
                </el-button>
              </div>
            </div>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="buildUrl" :loading="building">
              构建URL
            </el-button>
          </div>
          <div v-if="buildResult" class="output-section">
            <h4 class="section-title">构建结果</h4>
            <el-input
              v-model="buildResult"
              readonly
              placeholder="构建的URL将显示在这里..."
            />
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="验证URL" name="validate">
        <ToolSection
          input-label="输入URL"
          output-label="验证结果"
          action-text="验证"
          :loading="validating"
          :has-output="!!validateResult"
          @submit="validateUrl"
        >
          <template #input>
            <el-input
              v-model="validateInput"
              placeholder="请输入要验证的URL..."
              clearable
            />
          </template>
          <template #output>
            <div v-if="validateResult" class="validate-result">
              <el-alert
                :title="validateResult.valid ? 'URL有效' : 'URL无效'"
                :type="validateResult.valid ? 'success' : 'error'"
                :description="validateResult.valid ? '' : (validateResult.error || '格式不正确')"
                show-icon
                :closable="false"
                style="margin-bottom: 15px;"
              />
              <div v-if="validateResult.valid" class="validate-detail">
                <el-descriptions title="URL信息" :column="2" border>
                  <el-descriptions-item label="Scheme">{{ validateResult.scheme || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="Netloc">{{ validateResult.netloc || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="是否HTTPS">
                    <el-tag :type="validateResult.is_https ? 'success' : 'info'" size="small">
                      {{ validateResult.is_https ? '是' : '否' }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="包含端口">
                    <el-tag :type="validateResult.has_port ? 'success' : 'info'" size="small">
                      {{ validateResult.has_port ? '是' : '否' }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="包含查询参数">
                    <el-tag :type="validateResult.has_query ? 'success' : 'info'" size="small">
                      {{ validateResult.has_query ? '是' : '否' }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item label="包含锚点">
                    <el-tag :type="validateResult.has_fragment ? 'success' : 'info'" size="small">
                      {{ validateResult.has_fragment ? '是' : '否' }}
                    </el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane label="提取链接" name="extract-links">
        <ToolSection
          input-label="输入文本"
          output-label="提取结果"
          action-text="提取链接"
          :loading="extractingLinks"
          :has-output="!!extractedLinks.length"
          @submit="extractLinks"
        >
          <template #input>
            <el-input
              v-model="extractInput"
              type="textarea"
              :rows="8"
              placeholder="请输入包含链接的文本内容..."
            />
          </template>
          <template #output>
            <div v-if="extractedLinks.length" class="extract-result">
              <el-alert
                :title="'共提取到 ' + extractedLinks.length + ' 个链接'"
                type="success"
                show-icon
                :closable="false"
                style="margin-bottom: 15px;"
              />
              <el-table :data="extractedLinksTable" border stripe>
                <el-table-column prop="index" label="序号" width="80" />
                <el-table-column prop="url" label="URL">
                  <template #default="scope">
                    <a :href="scope.row.url" target="_blank" rel="noopener noreferrer" class="link-text">{{ scope.row.url }}</a>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane label="Query编解码" name="query-codec">
        <div class="tool-section">
          <div class="input-section">
            <el-tabs v-model="queryCodecTab" type="border-card">
              <el-tab-pane label="编码" name="encode">
                <h4 class="section-title">Query编码</h4>
                <div class="query-codec-params">
                  <div v-for="(param, index) in queryEncodeParams" :key="index" class="header-item">
                    <el-input
                      v-model="param.key"
                      placeholder="参数名"
                      style="width: 40%;"
                    />
                    <el-input
                      v-model="param.value"
                      placeholder="参数值"
                      style="width: 40%; margin-left: 10px;"
                    />
                    <el-button
                      type="danger"
                      size="small"
                      @click="removeQueryEncodeParam(index)"
                      style="margin-left: 10px;"
                      :disabled="queryEncodeParams.length === 1"
                    >
                      删除
                    </el-button>
                  </div>
                  <el-button type="primary" size="small" @click="addQueryEncodeParam" style="margin-top: 10px;">
                    添加参数
                  </el-button>
                </div>
                <div class="action-section">
                  <el-button type="primary" @click="encodeQuery" :loading="encodingQuery">
                    编码
                  </el-button>
                </div>
                <div v-if="queryEncodeResult" class="output-section">
                  <h4 class="section-title">编码结果</h4>
                  <el-input
                    v-model="queryEncodeResult"
                    readonly
                    placeholder="编码结果将显示在这里..."
                  />
                </div>
              </el-tab-pane>

              <el-tab-pane label="解码" name="decode">
                <h4 class="section-title">Query解码</h4>
                <el-input
                  v-model="queryDecodeInput"
                  placeholder="请输入要解码的查询字符串，例如: key1=value1&key2=value2..."
                  clearable
                  style="margin-bottom: 15px;"
                />
                <div class="action-section">
                  <el-button type="primary" @click="decodeQuery" :loading="decodingQuery">
                    解码
                  </el-button>
                </div>
                <div v-if="queryDecodeResult.length" class="output-section">
                  <h4 class="section-title">解码结果</h4>
                  <el-table :data="queryDecodeResult" border stripe>
                    <el-table-column prop="key" label="参数名" />
                    <el-table-column prop="value" label="参数值" />
                  </el-table>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="转HAR" name="to-har">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">输入URL</h4>
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
            <h4 class="section-title">HAR格式结果</h4>
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
            <h4 class="section-title">请求配置</h4>
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
            <h4 class="section-title">响应结果</h4>
            <div class="response-info">
              <el-row :gutter="20">
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="response-item">
                    <strong>状态码:</strong>
                    <span :class="getStatusClass(apiResponse.response.status_code)">
                      {{ apiResponse.response.status_code }} {{ apiResponse.response.status_text }}
                    </span>
                  </div>
                </el-col>
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="response-item">
                    <strong>响应时间:</strong>
                    <span>{{ apiResponse.response.response_time }}ms</span>
                  </div>
                </el-col>
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="response-item">
                    <strong>内容长度:</strong>
                    <span>{{ apiResponse.response.content_length }} bytes</span>
                  </div>
                </el-col>
                <el-col :xs="12" :sm="12" :md="6">
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
            <h4 class="section-title">Curl命令</h4>
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
            <h4 class="section-title">解析结果</h4>
            <div class="parsed-info">
              <el-row :gutter="20">
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="parsed-item">
                    <strong>方法:</strong> {{ curlParsed.method }}
                  </div>
                </el-col>
                <el-col :xs="24" :sm="24" :md="18">
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
              <div v-if="curlParsed.data" class="parsed-data-section">
                <strong>请求数据:</strong>
                <pre class="request-body">{{ curlParsed.data }}</pre>
              </div>
            </div>
          </div>

          <div class="output-section" v-if="curlResponse">
            <h4 class="section-title">执行结果</h4>
            <div class="response-info">
              <el-row :gutter="20">
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="response-item">
                    <strong>状态码:</strong>
                    <span :class="getStatusClass(curlResponse.response.status_code)">
                      {{ curlResponse.response.status_code }} {{ curlResponse.response.status_text }}
                    </span>
                  </div>
                </el-col>
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="response-item">
                    <strong>响应时间:</strong>
                    <span>{{ curlResponse.response.response_time }}ms</span>
                  </div>
                </el-col>
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="response-item">
                    <strong>内容长度:</strong>
                    <span>{{ curlResponse.response.content_length }} bytes</span>
                  </div>
                </el-col>
                <el-col :xs="12" :sm="12" :md="6">
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
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Link } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'
import ToolSection from '@/components/ToolSection.vue'

export default {
  name: 'UrlTools',
  components: {
    Link,
    ToolPage,
    ToolSection
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
      // 解析URL
      parseInput: '',
      parseResult: null,
      parsing: false,
      // 构建URL
      buildScheme: 'https',
      buildNetloc: '',
      buildPath: '',
      buildParams: '',
      buildQuery: '',
      buildFragment: '',
      buildQueryParams: [{ key: '', value: '' }],
      buildResult: '',
      building: false,
      // 验证URL
      validateInput: '',
      validateResult: null,
      validating: false,
      // 提取链接
      extractInput: '',
      extractedLinks: [],
      extractingLinks: false,
      // Query编解码
      queryCodecTab: 'encode',
      queryEncodeParams: [{ key: '', value: '' }],
      queryEncodeResult: '',
      encodingQuery: false,
      queryDecodeInput: '',
      queryDecodeResult: [],
      decodingQuery: false,
      // 转HAR
      harInput: '',
      harOutput: '',
      harMethod: 'GET',
      outputFormat: 'simplified',
      converting: false,
      generatingCurl: false,
      curlCommand: '',
      currentHarData: null,
      showCurlDialog: false,
      // API请求
      apiUrl: '',
      apiMethod: 'GET',
      apiHeaders: [{ name: '', value: '' }],
      apiBody: '',
      apiResponse: null,
      responseBodyText: '',
      responseTab: 'body',
      sendingRequest: false,
      // Curl请求
      curlParsed: null,
      curlResponse: null,
      curlResponseBodyText: '',
      curlResponseTab: 'body',
      parsingCurl: false,
      executingCurl: false
    }
  },
  computed: {
    parseQueryParamsList() {
      if (!this.parseResult || !this.parseResult.query_params) return []
      return Object.entries(this.parseResult.query_params).map(([key, value]) => ({ key, value }))
    },
    extractedLinksTable() {
      return this.extractedLinks.map((url, index) => ({ index: index + 1, url }))
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

    async parseUrl() {
      if (!this.parseInput.trim()) {
        ElMessage.warning('请输入要解析的URL')
        return
      }

      this.parsing = true
      try {
        const response = await axios.post('/api/url-tools/parse', {
          url: this.parseInput
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
    },

    async buildUrl() {
      this.building = true
      try {
        const params = {}
        this.buildQueryParams.forEach(param => {
          if (param.key.trim()) {
            params[param.key.trim()] = param.value
          }
        })

        const response = await axios.post('/api/url-tools/build', {
          scheme: this.buildScheme,
          netloc: this.buildNetloc,
          path: this.buildPath,
          params: this.buildParams,
          query: this.buildQuery,
          fragment: this.buildFragment,
          query_params: params
        })

        if (response.data.success) {
          this.buildResult = response.data.url
          ElMessage.success('构建成功')
        } else {
          ElMessage.error(response.data.error || '构建失败')
        }
      } catch (error) {
        ElMessage.error('构建失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.building = false
      }
    },

    addBuildQueryParam() {
      this.buildQueryParams.push({ key: '', value: '' })
    },

    removeBuildQueryParam(index) {
      if (this.buildQueryParams.length > 1) {
        this.buildQueryParams.splice(index, 1)
      }
    },

    async validateUrl() {
      if (!this.validateInput.trim()) {
        ElMessage.warning('请输入要验证的URL')
        return
      }

      this.validating = true
      try {
        const response = await axios.post('/api/url-tools/validate', {
          url: this.validateInput
        })

        if (response.data.success) {
          this.validateResult = response.data
          ElMessage.success(response.data.valid ? 'URL有效' : 'URL无效')
        } else {
          ElMessage.error(response.data.error || '验证失败')
        }
      } catch (error) {
        ElMessage.error('验证失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.validating = false
      }
    },

    async extractLinks() {
      if (!this.extractInput.trim()) {
        ElMessage.warning('请输入要提取链接的文本')
        return
      }

      this.extractingLinks = true
      try {
        const response = await axios.post('/api/url-tools/extract-links', {
          text: this.extractInput
        })

        if (response.data.success) {
          this.extractedLinks = response.data.links || []
          ElMessage.success('提取成功，共找到 ' + this.extractedLinks.length + ' 个链接')
        } else {
          ElMessage.error(response.data.error || '提取失败')
        }
      } catch (error) {
        ElMessage.error('提取失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.extractingLinks = false
      }
    },

    async encodeQuery() {
      const params = {}
      let hasParams = false
      this.queryEncodeParams.forEach(param => {
        if (param.key.trim()) {
          params[param.key.trim()] = param.value
          hasParams = true
        }
      })

      if (!hasParams) {
        ElMessage.warning('请至少输入一个参数')
        return
      }

      this.encodingQuery = true
      try {
        const response = await axios.post('/api/url-tools/encode-query', {
          params: params
        })

        if (response.data.success) {
          this.queryEncodeResult = response.data.query_string
          ElMessage.success('编码成功')
        } else {
          ElMessage.error(response.data.error || '编码失败')
        }
      } catch (error) {
        ElMessage.error('编码失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.encodingQuery = false
      }
    },

    addQueryEncodeParam() {
      this.queryEncodeParams.push({ key: '', value: '' })
    },

    removeQueryEncodeParam(index) {
      if (this.queryEncodeParams.length > 1) {
        this.queryEncodeParams.splice(index, 1)
      }
    },

    async decodeQuery() {
      if (!this.queryDecodeInput.trim()) {
        ElMessage.warning('请输入要解码的查询字符串')
        return
      }

      this.decodingQuery = true
      try {
        const response = await axios.post('/api/url-tools/decode-query', {
          query_string: this.queryDecodeInput
        })

        if (response.data.success) {
          const decodedParams = response.data.params || {}
          this.queryDecodeResult = Object.entries(decodedParams).map(([key, value]) => ({ key, value }))
          ElMessage.success('解码成功')
        } else {
          ElMessage.error(response.data.error || '解码失败')
        }
      } catch (error) {
        ElMessage.error('解码失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.decodingQuery = false
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
          if (navigator.clipboard) {
            await navigator.clipboard.writeText(this.curlCommand)
            ElMessage.success('Curl命令已生成并复制到剪贴板')
          } else {
            ElMessage.success('Curl命令已生成')
          }

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
.method-section {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.method-section label {
  font-weight: 600;
  color: var(--dt-text-primary);
}

.format-section {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.format-section label {
  font-weight: 600;
  color: var(--dt-text-primary);
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
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-sm);
  padding: 15px;
  background-color: var(--dt-bg-section);
}

.headers-section h5, .body-section h5 {
  margin: 0 0 10px 0;
  color: var(--dt-text-primary);
  font-weight: 600;
}

.header-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.response-info {
  background-color: var(--dt-bg-page);
  padding: 15px;
  border-radius: var(--dt-radius-sm);
  margin-bottom: 20px;
}

.response-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.response-item strong {
  color: var(--dt-text-regular);
  font-size: var(--dt-font-size-xs);
}

.status-success {
  color: var(--dt-success);
  font-weight: bold;
}

.status-redirect {
  color: var(--dt-warning);
  font-weight: bold;
}

.status-client-error {
  color: var(--dt-danger);
  font-weight: bold;
}

.status-server-error {
  color: var(--dt-danger);
  font-weight: bold;
}

.status-unknown {
  color: var(--dt-info);
  font-weight: bold;
}

.headers-display {
  background-color: var(--dt-bg-section);
  border: 1px solid var(--dt-border-lighter);
  border-radius: var(--dt-radius-sm);
  padding: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.header-display-item {
  padding: 5px 0;
  border-bottom: 1px solid var(--dt-border-lighter);
  font-family: 'Courier New', monospace;
  font-size: var(--dt-font-size-xs);
}

.header-display-item:last-child {
  border-bottom: none;
}

.request-info {
  padding: 15px;
}

.request-info p {
  margin: 8px 0;
  font-size: var(--dt-font-size-base);
}

.request-body {
  background-color: var(--dt-bg-section);
  border: 1px solid var(--dt-border-lighter);
  border-radius: var(--dt-radius-sm);
  padding: 10px;
  font-family: 'Courier New', monospace;
  font-size: var(--dt-font-size-xs);
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

/* Curl相关样式 */
.parsed-info {
  background-color: var(--dt-primary-light);
  padding: 15px;
  border-radius: var(--dt-radius-sm);
  margin-bottom: 20px;
}

.parsed-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.parsed-item strong {
  color: var(--dt-text-regular);
  font-size: var(--dt-font-size-xs);
}

.parsed-headers, .parsed-data-section {
  margin-top: 15px;
}

.parsed-headers strong, .parsed-data-section strong {
  color: var(--dt-text-primary);
  font-size: var(--dt-font-size-base);
  margin-bottom: 8px;
  display: block;
}

.curl-command-display {
  padding: 15px;
}

.curl-command-display h5 {
  margin: 0 0 10px 0;
  color: var(--dt-text-primary);
  font-weight: 600;
}

.curl-command {
  background-color: var(--dt-bg-section);
  border: 1px solid var(--dt-border-lighter);
  border-radius: var(--dt-radius-sm);
  padding: 15px;
  font-family: 'Courier New', monospace;
  font-size: var(--dt-font-size-xs);
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
  margin-bottom: 20px;
}

.parsed-request {
  background-color: var(--dt-bg-section);
  border: 1px solid var(--dt-border-lighter);
  border-radius: var(--dt-radius-sm);
  padding: 15px;
}

.parsed-request p {
  margin: 8px 0;
  font-size: var(--dt-font-size-base);
}

/* 解析URL样式 */
.parse-result {
  margin-top: 10px;
}

.query-params-section {
  margin-top: 20px;
}

.query-params-section h5 {
  margin: 0 0 10px 0;
  color: var(--dt-text-primary);
  font-weight: 600;
}

/* 构建URL样式 */
.build-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.build-form-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.build-label {
  font-weight: 600;
  color: var(--dt-text-primary);
  min-width: 70px;
  text-align: right;
}

.query-params-builder {
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-sm);
  padding: 15px;
  background-color: var(--dt-bg-section);
}

.query-params-builder h5 {
  margin: 0 0 10px 0;
  color: var(--dt-text-primary);
  font-weight: 600;
}

/* 验证URL样式 */
.validate-result {
  margin-top: 10px;
}

.validate-detail {
  margin-top: 10px;
}

/* 提取链接样式 */
.extract-result {
  margin-top: 10px;
}

.link-text {
  color: var(--el-color-primary);
  text-decoration: none;
  word-break: break-all;
}

.link-text:hover {
  text-decoration: underline;
}

/* Query编解码样式 */
.query-codec-params {
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-sm);
  padding: 15px;
  background-color: var(--dt-bg-section);
  margin-bottom: 15px;
}

@media (max-width: 768px) {
  .url-section {
    flex-direction: column;
    gap: 10px;
  }

  .url-section .el-select {
    margin-left: 0;
    width: 100% !important;
  }

  .header-item {
    flex-wrap: wrap;
  }

  .header-item .el-input {
    width: 100% !important;
    margin-left: 0 !important;
    margin-bottom: 8px;
  }

  .method-section,
  .format-section {
    flex-wrap: wrap;
  }

  .build-form-row {
    flex-wrap: wrap;
  }

  .build-label {
    min-width: auto;
    text-align: left;
  }
}
</style>
