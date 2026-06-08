<template>
  <ToolPage :title="$t('tools.url.title')" :icon="Link">
    <el-tabs v-model="activeTab">
      <el-tab-pane :label="$t('tools.url.tab.encode')" name="encode">
        <ToolSection
          :input-label="$t('tools.url.encode.inputLabel')"
          :output-label="$t('tools.url.encode.outputLabel')"
          :action-text="$t('tools.url.tab.encode')"
          :loading="encoding"
          @submit="encodeUrl"
        >
          <template #input>
            <el-input
              v-model="encodeInput"
              :placeholder="$t('tools.url.encode.placeholder')"
              clearable
            />
          </template>
          <template #output>
            <el-input
              v-model="encodeOutput"
              readonly
              :placeholder="$t('tools.url.encode.resultPlaceholder')"
            />
            <div class="field-toolbar" v-if="encodeOutput" style="margin-top: 6px;">
              <span style="font-size: 12px; color: #909399;">{{ encodeOutput.length }} chars</span>
              <el-button link size="small" type="primary" @click="copyText(encodeOutput)">
                <el-icon><CopyDocument /></el-icon> Copy
              </el-button>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.url.tab.decode')" name="decode">
        <ToolSection
          :input-label="$t('tools.url.decode.inputLabel')"
          :output-label="$t('tools.url.decode.outputLabel')"
          :action-text="$t('tools.url.tab.decode')"
          :loading="decoding"
          @submit="decodeUrl"
        >
          <template #input>
            <el-input
              v-model="decodeInput"
              :placeholder="$t('tools.url.decode.placeholder')"
              clearable
            />
          </template>
          <template #output>
            <el-input
              v-model="decodeOutput"
              readonly
              :placeholder="$t('tools.url.decode.resultPlaceholder')"
            />
            <div class="field-toolbar" v-if="decodeOutput" style="margin-top: 6px;">
              <span style="font-size: 12px; color: #909399;">{{ decodeOutput.length }} chars</span>
              <el-button link size="small" type="primary" @click="copyText(decodeOutput)">
                <el-icon><CopyDocument /></el-icon> Copy
              </el-button>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.url.tab.parse')" name="parse">
        <ToolSection
          :input-label="$t('tools.url.parse.inputLabel')"
          :output-label="$t('tools.url.parse.outputLabel')"
          :action-text="$t('tools.url.parse.actionText')"
          :loading="parsing"
          :has-output="!!parseResult"
          @submit="parseUrl"
        >
          <template #input>
            <el-input
              v-model="parseInput"
              :placeholder="$t('tools.url.parse.placeholder')"
              clearable
            />
          </template>
          <template #output>
            <div v-if="parseResult" class="parse-result">
              <el-descriptions :title="$t('tools.url.parse.title')" :column="2" border>
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
                <h5>{{ $t('tools.url.parse.queryParams') }}</h5>
                <el-table :data="parseQueryParamsList" border stripe>
                  <el-table-column prop="key" :label="$t('tools.url.api.paramName')" />
                  <el-table-column prop="value" :label="$t('tools.url.api.paramValue')" />
                </el-table>
              </div>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.url.tab.build')" name="build">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.url.build.title') }}</h4>
            <div class="build-form">
              <div class="build-form-row">
                <label class="build-label">Scheme:</label>
                <el-select v-model="buildScheme" :placeholder="$t('tools.url.build.inputLabel')" style="width: 150px;">
                  <el-option label="http" value="http"></el-option>
                  <el-option label="https" value="https"></el-option>
                  <el-option label="ftp" value="ftp"></el-option>
                </el-select>
              </div>
              <div class="build-form-row">
                <label class="build-label">Netloc:</label>
                <el-input v-model="buildNetloc" :placeholder="$t('tools.url.build.inputLabel')" clearable />
              </div>
              <div class="build-form-row">
                <label class="build-label">Path:</label>
                <el-input v-model="buildPath" :placeholder="$t('tools.url.build.inputLabel')" clearable />
              </div>
              <div class="build-form-row">
                <label class="build-label">Params:</label>
                <el-input v-model="buildParams" :placeholder="$t('tools.url.build.inputLabel')" clearable />
              </div>
              <div class="build-form-row">
                <label class="build-label">Query:</label>
                <el-input v-model="buildQuery" :placeholder="$t('tools.url.build.inputLabel')" clearable />
              </div>
              <div class="build-form-row">
                <label class="build-label">Fragment:</label>
                <el-input v-model="buildFragment" :placeholder="$t('tools.url.build.inputLabel')" clearable />
              </div>
              <div class="query-params-builder">
                <h5>{{ $t('tools.url.parse.queryParams') }}</h5>
                <div v-for="(param, index) in buildQueryParams" :key="index" class="header-item">
                  <el-input
                    v-model="param.key"
                    :placeholder="$t('tools.url.api.paramName')"
                    style="width: 40%;"
                  />
                  <el-input
                    v-model="param.value"
                    :placeholder="$t('tools.url.api.paramValue')"
                    style="width: 40%; margin-left: 10px;"
                  />
                  <el-button
                    type="danger"
                    size="small"
                    @click="removeBuildQueryParam(index)"
                    style="margin-left: 10px;"
                    :disabled="buildQueryParams.length === 1"
                  >{{ $t('tools.url.api.removeParam') }}</el-button>
                </div>
                <el-button type="primary" size="small" @click="addBuildQueryParam" style="margin-top: 10px;">{{ $t('tools.url.api.addParam') }}</el-button>
              </div>
            </div>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="buildUrl" :loading="building">
              {{ $t('tools.url.build.actionText') }}
            </el-button>
          </div>
          <div v-if="buildResult" class="output-section">
            <h4 class="section-title">{{ $t('tools.url.build.outputLabel') }}</h4>
            <el-input
              v-model="buildResult"
              readonly
              :placeholder="$t('tools.url.build.inputLabel')"
            />
            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(buildResult)">
                <el-icon><CopyDocument /></el-icon> Copy
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.url.tab.validate')" name="validate">
        <ToolSection
          :input-label="$t('tools.url.validate.inputLabel')"
          :output-label="$t('tools.url.validate.outputLabel')"
          :action-text="$t('tools.url.validate.actionText')"
          :loading="validating"
          :has-output="!!validateResult"
          @submit="validateUrl"
        >
          <template #input>
            <el-input
              v-model="validateInput"
              :placeholder="$t('tools.url.validate.inputLabel')"
              clearable
            />
          </template>
          <template #output>
            <div v-if="validateResult" class="validate-result">
              <el-alert
                :title="validateResult.valid ? $t('tools.url.validate.valid') : $t('tools.url.validate.invalid')"
                :type="validateResult.valid ? 'success' : 'error'"
                :description="validateResult.valid ? '' : (validateResult.error || $t('tools.url.validate.formatIncorrect'))"
                show-icon
                :closable="false"
                style="margin-bottom: 15px;"
              />
              <div v-if="validateResult.valid" class="validate-detail">
                <el-descriptions :title="$t('tools.url.validate.title')" :column="2" border>
                  <el-descriptions-item label="Scheme">{{ validateResult.scheme || '-' }}</el-descriptions-item>
                  <el-descriptions-item label="Netloc">{{ validateResult.netloc || '-' }}</el-descriptions-item>
                  <el-descriptions-item :label="$t('tools.url.validate.isHttps')">
                    <el-tag :type="validateResult.is_https ? 'success' : 'info'" size="small">
                      {{ validateResult.is_https ? $t('tools.url.validate.yes') : $t('tools.url.validate.no') }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="$t('tools.url.validate.hasPort')">
                    <el-tag :type="validateResult.has_port ? 'success' : 'info'" size="small">
                      {{ validateResult.has_port ? $t('tools.url.validate.yes') : $t('tools.url.validate.no') }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="$t('tools.url.validate.hasQuery')">
                    <el-tag :type="validateResult.has_query ? 'success' : 'info'" size="small">
                      {{ validateResult.has_query ? $t('tools.url.validate.yes') : $t('tools.url.validate.no') }}
                    </el-tag>
                  </el-descriptions-item>
                  <el-descriptions-item :label="$t('tools.url.validate.hasFragment')">
                    <el-tag :type="validateResult.has_fragment ? 'success' : 'info'" size="small">
                      {{ validateResult.has_fragment ? $t('tools.url.validate.yes') : $t('tools.url.validate.no') }}
                    </el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.url.tab.extract')" name="extract-links">
        <ToolSection
          :input-label="$t('tools.url.extract.inputLabel')"
          :output-label="$t('tools.url.extract.outputLabel')"
          :action-text="$t('tools.url.extract.actionText')"
          :loading="extractingLinks"
          :has-output="!!extractedLinks.length"
          @submit="extractLinks"
        >
          <template #input>
            <el-input
              v-model="extractInput"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.url.extract.placeholder')"
            />
          </template>
          <template #output>
            <div v-if="extractedLinks.length" class="extract-result">
              <el-alert
                :title="$t('tools.url.extract.extractedCount', { count: extractedLinks.length })"
                type="success"
                show-icon
                :closable="false"
                style="margin-bottom: 15px;"
              />
              <el-table :data="extractedLinksTable" border stripe>
                <el-table-column prop="index" :label="$t('tools.url.extract.index')" width="80" />
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

      <el-tab-pane :label="$t('tools.url.tab.queryCodec')" name="query-codec">
        <div class="tool-section">
          <div class="input-section">
            <el-tabs v-model="queryCodecTab" type="border-card">
              <el-tab-pane :label="$t('tools.url.tab.encode')" name="encode">
                <h4 class="section-title">{{ $t('tools.url.queryCodec.encode.title') }}</h4>
                <div class="query-codec-params">
                  <div v-for="(param, index) in queryEncodeParams" :key="index" class="header-item">
                    <el-input
                      v-model="param.key"
                      :placeholder="$t('tools.url.api.paramName')"
                      style="width: 40%;"
                    />
                    <el-input
                      v-model="param.value"
                      :placeholder="$t('tools.url.api.paramValue')"
                      style="width: 40%; margin-left: 10px;"
                    />
                    <el-button
                      type="danger"
                      size="small"
                      @click="removeQueryEncodeParam(index)"
                      style="margin-left: 10px;"
                      :disabled="queryEncodeParams.length === 1"
                    >{{ $t('tools.url.api.removeParam') }}</el-button>
                  </div>
                  <el-button type="primary" size="small" @click="addQueryEncodeParam" style="margin-top: 10px;">{{ $t('tools.url.api.addParam') }}</el-button>
                </div>
                <div class="action-section">
                  <el-button type="primary" @click="encodeQuery" :loading="encodingQuery">
                    {{ $t('tools.url.tab.encode') }}
                  </el-button>
                </div>
                <div v-if="queryEncodeResult" class="output-section">
                  <h4 class="section-title">{{ $t('tools.url.queryCodec.encode.outputLabel') }}</h4>
                  <el-input
                    v-model="queryEncodeResult"
                    readonly
                    :placeholder="$t('tools.url.queryCodec.encode.placeholder')"
                  />
                  <div class="field-toolbar" style="margin-top: 6px;">
                    <el-button link size="small" type="primary" @click="copyText(queryEncodeResult)">
                      <el-icon><CopyDocument /></el-icon> Copy
                    </el-button>
                  </div>
                </div>
              </el-tab-pane>

              <el-tab-pane :label="$t('tools.url.tab.decode')" name="decode">
                <h4 class="section-title">{{ $t('tools.url.queryCodec.decode.title') }}</h4>
                <el-input
                  v-model="queryDecodeInput"
                  :placeholder="$t('tools.url.queryCodec.decode.placeholder')"
                  clearable
                  style="margin-bottom: 15px;"
                />
                <div class="action-section">
                  <el-button type="primary" @click="decodeQuery" :loading="decodingQuery">
                    {{ $t('tools.url.tab.decode') }}
                  </el-button>
                </div>
                <div v-if="queryDecodeResult.length" class="output-section">
                  <h4 class="section-title">{{ $t('tools.url.queryCodec.decode.outputLabel') }}</h4>
                  <el-table :data="queryDecodeResult" border stripe>
                    <el-table-column prop="key" :label="$t('tools.url.api.paramName')" />
                    <el-table-column prop="value" :label="$t('tools.url.api.paramValue')" />
                  </el-table>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.url.tab.toHar')" name="to-har">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.url.har.inputLabel') }}</h4>
            <el-input
              v-model="harInput"
              :placeholder="$t('tools.url.har.inputLabel')"
              clearable
            />
            <div class="method-section">
              <label>{{ $t('tools.url.har.httpMethod') }}</label>
              <el-select v-model="harMethod" :placeholder="$t('tools.url.har.httpMethod')" style="width: 120px;">
                <el-option label="GET" value="GET"></el-option>
                <el-option label="POST" value="POST"></el-option>
                <el-option label="PUT" value="PUT"></el-option>
                <el-option label="DELETE" value="DELETE"></el-option>
                <el-option label="PATCH" value="PATCH"></el-option>
              </el-select>
            </div>
            <div class="format-section">
              <label>{{ $t('tools.url.har.outputFormat') }}</label>
              <el-radio-group v-model="outputFormat">
                <el-radio label="simplified">{{ $t('tools.url.har.simplifiedFormat') }}</el-radio>
                <el-radio label="har">{{ $t('tools.url.har.fullHar') }}</el-radio>
              </el-radio-group>
            </div>
          </div>
          <div class="action-section">
            <el-button type="primary" @click="urlToHar" :loading="converting">
              {{ $t('tools.url.har.convertToHar') }}
            </el-button>
            <el-button type="success" @click="generateCurl" :loading="generatingCurl" :disabled="!harOutput">
              {{ $t('tools.url.har.generateCurl') }}
            </el-button>
          </div>
          <div class="output-section">
            <h4 class="section-title">{{ $t('tools.url.har.resultLabel') }}</h4>
            <el-input
              v-model="harOutput"
              type="textarea"
              :rows="30"
              readonly
              :placeholder="$t('tools.url.har.resultPlaceholder')"
              style="font-family: 'Courier New', monospace; font-size: 12px;"
            />
            <div class="field-toolbar" v-if="harOutput" style="margin-top: 6px;">
              <span style="font-size: 12px; color: #909399;">{{ harOutput.length }} chars</span>
              <el-button link size="small" type="primary" @click="copyText(harOutput)">
                <el-icon><CopyDocument /></el-icon> Copy
              </el-button>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.url.tab.apiRequest')" name="api-request">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.url.api.configLabel') }}</h4>
            <div class="request-config">
              <div class="url-section">
                <el-input
                  v-model="apiUrl"
                  :placeholder="$t('tools.url.api.urlPlaceholder')"
                  clearable
                  style="flex: 1;"
                />
                <el-select v-model="apiMethod" :placeholder="$t('tools.url.api.method')" style="width: 100px; margin-left: 10px;">
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
                <h5>{{ $t('tools.url.api.headers') }}</h5>
                <div v-for="(header, index) in apiHeaders" :key="index" class="header-item">
                  <el-input
                    v-model="header.name"
                    :placeholder="$t('tools.url.api.headerName')"
                    style="width: 45%;"
                  />
                  <el-input
                    v-model="header.value"
                    :placeholder="$t('tools.url.api.headerValue')"
                    style="width: 45%; margin-left: 10px;"
                  />
                  <el-button
                    type="danger"
                    size="small"
                    @click="removeHeader(index)"
                    style="margin-left: 10px;"
                    :disabled="apiHeaders.length === 1"
                  >{{ $t('tools.url.api.removeParam') }}</el-button>
                </div>
                <el-button type="primary" size="small" @click="addHeader" style="margin-top: 10px;">
                  {{ $t('tools.url.api.addHeader') }}
                </el-button>
              </div>

              <div class="body-section" v-if="['POST', 'PUT', 'PATCH'].includes(apiMethod)">
                <h5>{{ $t('tools.url.api.requestBody') }}</h5>
                <el-input
                  v-model="apiBody"
                  type="textarea"
                  :rows="6"
                  :placeholder="$t('tools.url.api.bodyPlaceholder')"
                  style="font-family: 'Courier New', monospace; font-size: 12px;"
                />
              </div>
            </div>
          </div>

          <div class="action-section">
            <el-button type="primary" @click="sendApiRequest" :loading="sendingRequest">
              {{ $t('tools.url.api.sendRequest') }}
            </el-button>
            <el-button @click="clearApiResult" :disabled="!apiResponse">
              {{ $t('tools.url.api.clearResult') }}
            </el-button>
          </div>

          <div class="output-section" v-if="apiResponse">
            <h4 class="section-title">{{ $t('tools.url.api.responseLabel') }}</h4>
            <div class="response-info">
              <el-row :gutter="20">
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="response-item">
                    <strong>{{ $t('tools.url.api.statusCode') }}</strong>
                    <span :class="getStatusClass(apiResponse.response.status_code)">
                      {{ apiResponse.response.status_code }} {{ apiResponse.response.status_text }}
                    </span>
                  </div>
                </el-col>
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="response-item">
                    <strong>{{ $t('tools.url.api.responseTime') }}</strong>
                    <span>{{ apiResponse.response.response_time }}ms</span>
                  </div>
                </el-col>
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="response-item">
                    <strong>{{ $t('tools.url.api.contentLength') }}</strong>
                    <span>{{ apiResponse.response.content_length }} bytes</span>
                  </div>
                </el-col>
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="response-item">
                    <strong>{{ $t('tools.url.api.contentType') }}</strong>
                    <span>{{ apiResponse.response.body_type || 'unknown' }}</span>
                  </div>
                </el-col>
              </el-row>
            </div>

            <div class="response-tabs">
              <el-tabs v-model="responseTab">
                <el-tab-pane :label="$t('tools.url.api.responseBody')" name="body">
                  <el-input
                    v-model="responseBodyText"
                    type="textarea"
                    :rows="15"
                    readonly
                    style="font-family: 'Courier New', monospace; font-size: 12px;"
                  />
                  <div class="field-toolbar" style="margin-top: 6px;">
                    <el-button link size="small" type="primary" @click="copyText(responseBodyText)">
                      <el-icon><CopyDocument /></el-icon> Copy
                    </el-button>
                  </div>
                </el-tab-pane>
                <el-tab-pane :label="$t('tools.url.api.responseHeaders')" name="headers">
                  <div class="headers-display">
                    <div v-for="(value, key) in apiResponse.response.headers" :key="key" class="header-display-item">
                      <strong>{{ key }}:</strong> {{ value }}
                    </div>
                  </div>
                </el-tab-pane>
                <el-tab-pane :label="$t('tools.url.api.requestInfo')" name="request">
                  <div class="request-info">
                    <h5>{{ $t('tools.url.api.requestInfo') }}</h5>
                    <p><strong>{{ $t('tools.url.api.method') }}:</strong> {{ apiResponse.request.method }}</p>
                    <p><strong>URL:</strong> {{ apiResponse.request.url }}</p>
                    <p><strong>{{ $t('tools.url.api.headers') }}:</strong></p>
                    <div class="headers-display">
                      <div v-for="(value, key) in apiResponse.request.headers" :key="key" class="header-display-item">
                        <strong>{{ key }}:</strong> {{ value }}
                      </div>
                    </div>
                    <p v-if="apiResponse.request.body"><strong>{{ $t('tools.url.api.requestBody') }}:</strong></p>
                    <pre v-if="apiResponse.request.body" class="request-body">{{ apiResponse.request.body }}</pre>
                  </div>
                </el-tab-pane>
              </el-tabs>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane :label="$t('tools.url.tab.curlRequest')" name="curl-request">
        <div class="tool-section">
          <div class="input-section">
            <h4 class="section-title">{{ $t('tools.url.curl.title') }}</h4>
            <el-input
              v-model="curlCommand"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.url.curl.placeholder')"
              style="font-family: 'Courier New', monospace; font-size: 12px;"
            />
          </div>

          <div class="action-section">
            <el-button type="info" @click="parseCurlCommand" :loading="parsingCurl">
              {{ $t('tools.url.curl.parseCurl') }}
            </el-button>
            <el-button type="primary" @click="executeCurlCommand" :loading="executingCurl">
              {{ $t('tools.url.curl.executeCurl') }}
            </el-button>
            <el-button @click="clearCurlResult" :disabled="!curlResponse">
              {{ $t('tools.url.api.clearResult') }}
            </el-button>
          </div>

          <div class="output-section" v-if="curlParsed">
            <h4 class="section-title">{{ $t('tools.url.curl.parseResult') }}</h4>
            <div class="parsed-info">
              <el-row :gutter="20">
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="parsed-item">
                    <strong>{{ $t('tools.url.api.method') }}:</strong> {{ curlParsed.method }}
                  </div>
                </el-col>
                <el-col :xs="24" :sm="24" :md="18">
                  <div class="parsed-item">
                    <strong>URL:</strong> {{ curlParsed.url }}
                  </div>
                </el-col>
              </el-row>
              <div v-if="Object.keys(curlParsed.headers).length > 0" class="parsed-headers">
                <strong>{{ $t('tools.url.api.headers') }}:</strong>
                <div class="headers-display">
                  <div v-for="(value, key) in curlParsed.headers" :key="key" class="header-display-item">
                    <strong>{{ key }}:</strong> {{ value }}
                  </div>
                </div>
              </div>
              <div v-if="curlParsed.data" class="parsed-data-section">
                <strong>{{ $t('tools.url.curl.requestData') }}:</strong>
                <pre class="request-body">{{ curlParsed.data }}</pre>
              </div>
            </div>
          </div>

          <div class="output-section" v-if="curlResponse">
            <h4 class="section-title">{{ $t('tools.url.curl.executeResult') }}</h4>
            <div class="response-info">
              <el-row :gutter="20">
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="response-item">
                    <strong>{{ $t('tools.url.api.statusCode') }}</strong>
                    <span :class="getStatusClass(curlResponse.response.status_code)">
                      {{ curlResponse.response.status_code }} {{ curlResponse.response.status_text }}
                    </span>
                  </div>
                </el-col>
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="response-item">
                    <strong>{{ $t('tools.url.api.responseTime') }}</strong>
                    <span>{{ curlResponse.response.response_time }}ms</span>
                  </div>
                </el-col>
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="response-item">
                    <strong>{{ $t('tools.url.api.contentLength') }}</strong>
                    <span>{{ curlResponse.response.content_length }} bytes</span>
                  </div>
                </el-col>
                <el-col :xs="12" :sm="12" :md="6">
                  <div class="response-item">
                    <strong>{{ $t('tools.url.api.contentType') }}</strong>
                    <span>{{ curlResponse.response.body_type || 'unknown' }}</span>
                  </div>
                </el-col>
              </el-row>
            </div>

            <div class="response-tabs">
              <el-tabs v-model="curlResponseTab">
                <el-tab-pane :label="$t('tools.url.api.responseBody')" name="body">
                  <el-input
                    v-model="curlResponseBodyText"
                    type="textarea"
                    :rows="15"
                    readonly
                    style="font-family: 'Courier New', monospace; font-size: 12px;"
                  />
                  <div class="field-toolbar" style="margin-top: 6px;">
                    <el-button link size="small" type="primary" @click="copyText(curlResponseBodyText)">
                      <el-icon><CopyDocument /></el-icon> Copy
                    </el-button>
                  </div>
                </el-tab-pane>
                <el-tab-pane :label="$t('tools.url.api.responseHeaders')" name="headers">
                  <div class="headers-display">
                    <div v-for="(value, key) in curlResponse.response.headers" :key="key" class="header-display-item">
                      <strong>{{ key }}:</strong> {{ value }}
                    </div>
                  </div>
                </el-tab-pane>
                <el-tab-pane :label="$t('tools.url.curl.title')" name="command">
                  <div class="curl-command-display">
                    <h5>{{ $t('tools.url.curl.rawCurl') }}</h5>
                    <pre class="curl-command">{{ curlResponse.curl_command }}</pre>
                    <div class="field-toolbar" style="margin-top: 6px;">
                      <el-button link size="small" type="primary" @click="copyText(curlResponse.curl_command)">
                        <el-icon><CopyDocument /></el-icon> Copy
                      </el-button>
                    </div>
                    <h5>{{ $t('tools.url.curl.parsedRequest') }}</h5>
                    <div class="parsed-request">
                      <p><strong>{{ $t('tools.url.api.method') }}:</strong> {{ curlResponse.parsed_request.method }}</p>
                      <p><strong>URL:</strong> {{ curlResponse.parsed_request.url }}</p>
                      <p v-if="Object.keys(curlResponse.parsed_request.headers).length > 0"><strong>{{ $t('tools.url.api.headers') }}:</strong></p>
                      <div v-if="Object.keys(curlResponse.parsed_request.headers).length > 0" class="headers-display">
                        <div v-for="(value, key) in curlResponse.parsed_request.headers" :key="key" class="header-display-item">
                          <strong>{{ key }}:</strong> {{ value }}
                        </div>
                      </div>
                      <p v-if="curlResponse.parsed_request.data"><strong>{{ $t('tools.url.curl.requestData') }}:</strong></p>
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
import { Link, CopyDocument } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'
import ToolSection from '@/components/ToolSection.vue'

export default {
  name: 'UrlTools',
  components: {
    Link,
    CopyDocument,
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
    async copyText(text) {
      try {
        await navigator.clipboard.writeText(text)
        ElMessage.success('Copied to clipboard')
      } catch {
        const ta = document.createElement('textarea')
        ta.value = text
        ta.style.position = 'fixed'
        ta.style.opacity = '0'
        document.body.appendChild(ta)
        ta.select()
        document.execCommand('copy')
        document.body.removeChild(ta)
        ElMessage.success('Copied to clipboard')
      }
    },

    async encodeUrl() {
      if (!this.encodeInput.trim()) {
        ElMessage.warning(this.$t('tools.url.encode.placeholder'))
        return
      }

      this.encoding = true
      try {
        const response = await axios.post('/api/url-tools/encode', {
          url: this.encodeInput
        })

        if (response.data.success) {
          this.encodeOutput = response.data.encoded_url
          ElMessage.success(this.$t('tools.url.encode.success'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.url.encode.fail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.encoding = false
      }
    },

    async decodeUrl() {
      if (!this.decodeInput.trim()) {
        ElMessage.warning(this.$t('tools.url.decode.placeholder'))
        return
      }

      this.decoding = true
      try {
        const response = await axios.post('/api/url-tools/decode', {
          encoded_url: this.decodeInput
        })

        if (response.data.success) {
          this.decodeOutput = response.data.decoded_url
          ElMessage.success(this.$t('tools.url.decode.success'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.url.decode.fail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.decoding = false
      }
    },

    async parseUrl() {
      if (!this.parseInput.trim()) {
        ElMessage.warning(this.$t('tools.url.parse.placeholder'))
        return
      }

      this.parsing = true
      try {
        const response = await axios.post('/api/url-tools/parse', {
          url: this.parseInput
        })

        if (response.data.success) {
          this.parseResult = response.data
          ElMessage.success(this.$t('tools.url.parse.success'))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.url.parse.fail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.url.parse.fail') + ': ' + (error.response?.data?.error || error.message))
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
          ElMessage.success(this.$t('tools.url.build.success'))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.url.build.fail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.url.build.fail') + ': ' + (error.response?.data?.error || error.message))
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
        ElMessage.warning(this.$t('tools.url.validate.inputLabel'))
        return
      }

      this.validating = true
      try {
        const response = await axios.post('/api/url-tools/validate', {
          url: this.validateInput
        })

        if (response.data.success) {
          this.validateResult = response.data
          ElMessage.success(response.data.valid ? this.$t('tools.url.validate.valid') : this.$t('tools.url.validate.invalid'))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.url.validate.fail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.url.validate.fail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.validating = false
      }
    },

    async extractLinks() {
      if (!this.extractInput.trim()) {
        ElMessage.warning(this.$t('tools.url.extract.placeholder'))
        return
      }

      this.extractingLinks = true
      try {
        const response = await axios.post('/api/url-tools/extract-links', {
          text: this.extractInput
        })

        if (response.data.success) {
          this.extractedLinks = response.data.links || []
          ElMessage.success(this.$t('tools.url.extract.extractedCount', { count: this.extractedLinks.length }))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.url.extract.fail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.url.extract.fail') + ': ' + (error.response?.data?.error || error.message))
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
        ElMessage.warning(this.$t('tools.url.queryCodec.encode.placeholder'))
        return
      }

      this.encodingQuery = true
      try {
        const response = await axios.post('/api/url-tools/encode-query', {
          params: params
        })

        if (response.data.success) {
          this.queryEncodeResult = response.data.query_string
          ElMessage.success(this.$t('tools.url.queryCodec.encode.success'))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.url.queryCodec.encode.fail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.url.queryCodec.encode.fail') + ': ' + (error.response?.data?.error || error.message))
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
        ElMessage.warning(this.$t('tools.url.queryCodec.decode.placeholder'))
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
          ElMessage.success(this.$t('tools.url.queryCodec.decode.success'))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.url.queryCodec.decode.fail'))
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.url.queryCodec.decode.fail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.decodingQuery = false
      }
    },

    async urlToHar() {
      if (!this.harInput.trim()) {
        ElMessage.warning(this.$t('tools.url.har.inputRequired'))
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
          ElMessage.success(this.$t('tools.url.har.success'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.url.har.fail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.converting = false
      }
    },

    async generateCurl() {
      if (!this.currentHarData) {
        ElMessage.warning(this.$t('tools.url.har.convertFirst'))
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
            ElMessage.success(this.$t('tools.url.har.curlCopied'))
          } else {
            ElMessage.success(this.$t('tools.url.har.curlGenerated'))
          }

          this.showCurlDialog = true
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.url.har.curlGenerateFail') + ': ' + (error.response?.data?.error || error.message))
      } finally {
        this.generatingCurl = false
      }
    },

    async sendApiRequest() {
      if (!this.apiUrl.trim()) {
        ElMessage.warning(this.$t('tools.url.api.urlPlaceholder'))
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
          ElMessage.success(this.$t('tools.url.api.success'))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.url.api.fail'))
        }
      } catch (error) {
        const errorMessage = error.response?.data?.error || error.message
        ElMessage.error(this.$t('tools.url.api.fail') + ': ' + errorMessage)
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
        ElMessage.warning(this.$t('tools.url.curl.placeholder'))
        return
      }

      this.parsingCurl = true
      try {
        const response = await axios.post('/api/url-tools/parse-curl', {
          curl_command: this.curlCommand
        })

        if (response.data.success) {
          this.curlParsed = response.data.parsed
          ElMessage.success(this.$t('tools.url.curl.parseSuccess'))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.url.curl.parseFail'))
        }
      } catch (error) {
        const errorMessage = error.response?.data?.error || error.message
        ElMessage.error(this.$t('tools.url.curl.parseFail') + ': ' + errorMessage)
      } finally {
        this.parsingCurl = false
      }
    },

    async executeCurlCommand() {
      if (!this.curlCommand.trim()) {
        ElMessage.warning(this.$t('tools.url.curl.placeholder'))
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
          ElMessage.success(this.$t('tools.url.curl.executeSuccess'))
        } else {
          ElMessage.error(response.data.error || this.$t('tools.url.curl.executeFail'))
        }
      } catch (error) {
        const errorMessage = error.response?.data?.error || error.message
        ElMessage.error(this.$t('tools.url.curl.executeFail') + ': ' + errorMessage)
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

.field-toolbar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
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
