<template>
  <ToolPage :title="$t('tools.markdown.title')" :icon="Document">
    <el-tabs v-model="activeTab">
      <!-- Markdown转HTML -->
      <el-tab-pane :label="$t('tools.markdown.tab.mdToHtml')" name="to-html">
        <ToolSection
          :input-label="$t('tools.markdown.label.inputMarkdown')"
          :output-label="$t('tools.markdown.label.htmlOutput')"
          :action-text="$t('tools.markdown.label.convert')"
          :loading="converting"
          :has-output="!!htmlOutput"
          @submit="convertToHtml"
        >
          <template #input>
            <el-input
              v-model="markdownInput"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.markdown.label.inputMarkdown') + '...'"
              style="width: 100%;"
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="markdownInput">
                {{ markdownInput.length }} {{ $t('tools.markdown.label.chars') }} · {{ lineCount(markdownInput) }} {{ $t('tools.markdown.label.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('markdown')">{{ $t('tools.markdown.label.sample') }}</el-button>
              </div>
            </div>
          </template>
          <template #actions>
            <el-button type="primary" @click="convertToHtml" :loading="converting">
              {{ $t('tools.markdown.label.convert') }}
            </el-button>
            <el-button @click="clearAll">{{ $t('tools.markdown.label.clear') }}</el-button>
          </template>
          <template #output>
            <el-input
              v-model="htmlOutput"
              type="textarea"
              :rows="8"
              readonly
              style="width: 100%;"
            />
            <div class="field-toolbar" v-if="htmlOutput">
              <span class="field-stats">
                {{ htmlOutput.length }} {{ $t('tools.markdown.label.chars') }} · {{ lineCount(htmlOutput) }} {{ $t('tools.markdown.label.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" type="primary" @click="copyText(htmlOutput)">
                  <el-icon><CopyDocument /></el-icon> {{ $t('tools.markdown.label.copy') }}
                </el-button>
                <el-button link size="small" type="success" @click="downloadHtml" :disabled="!fullHtmlOutput">
                  {{ $t('tools.markdown.label.downloadFullHtml') }}
                </el-button>
              </div>
            </div>
            <div class="stats" v-if="conversionStats">
              <el-descriptions :column="descColumn" size="small" border>
                <el-descriptions-item :label="$t('tools.markdown.label.originalLength')">
                  {{ conversionStats.original_length }} {{ $t('tools.markdown.label.chars') }}
                </el-descriptions-item>
                <el-descriptions-item :label="$t('tools.markdown.label.htmlLength')">
                  {{ conversionStats.html_length }} {{ $t('tools.markdown.label.chars') }}
                </el-descriptions-item>
                <el-descriptions-item :label="$t('tools.markdown.label.fullHtmlLength')">
                  {{ conversionStats.full_html_length }} {{ $t('tools.markdown.label.chars') }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <!-- Markdown转纯文本 -->
      <el-tab-pane :label="$t('tools.markdown.tab.mdToText')" name="to-plain">
        <ToolSection
          :input-label="$t('tools.markdown.label.inputMarkdown')"
          :output-label="$t('tools.markdown.label.textOutput')"
          :action-text="$t('tools.markdown.label.convert')"
          :loading="converting"
          :has-output="!!plainOutput"
          @submit="convertToPlain"
        >
          <template #input>
            <el-input
              v-model="markdownInput"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.markdown.label.inputMarkdown') + '...'"
              style="width: 100%;"
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="markdownInput">
                {{ markdownInput.length }} {{ $t('tools.markdown.label.chars') }} · {{ lineCount(markdownInput) }} {{ $t('tools.markdown.label.lines') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('markdown')">{{ $t('tools.markdown.label.sample') }}</el-button>
              </div>
            </div>
          </template>
          <template #actions>
            <el-button type="primary" @click="convertToPlain" :loading="converting">
              {{ $t('tools.markdown.label.convert') }}
            </el-button>
            <el-button @click="clearAll">{{ $t('tools.markdown.label.clear') }}</el-button>
          </template>
          <template #output>
            <el-input
              v-model="plainOutput"
              type="textarea"
              :rows="8"
              readonly
              style="width: 100%;"
            />
            <div class="field-toolbar" v-if="plainOutput">
              <span class="field-stats">
                {{ plainOutput.length }} {{ $t('tools.markdown.label.chars') }} · {{ lineCount(plainOutput) }} {{ $t('tools.markdown.label.lines') }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(plainOutput)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.markdown.label.copy') }}
              </el-button>
            </div>
            <div class="stats" v-if="conversionStats">
              <el-descriptions :column="2" size="small" border>
                <el-descriptions-item :label="$t('tools.markdown.label.originalLength')">
                  {{ conversionStats.original_length }} {{ $t('tools.markdown.label.chars') }}
                </el-descriptions-item>
                <el-descriptions-item :label="$t('tools.markdown.label.outputLength')">
                  {{ conversionStats.plain_length }} {{ $t('tools.markdown.label.chars') }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <!-- 转义/反转义 -->
      <el-tab-pane :label="$t('tools.markdown.tab.escape')" name="escape">
        <el-tabs v-model="escapeTab">
          <el-tab-pane :label="$t('tools.markdown.label.escapeSpecialChars')" name="escape">
            <div class="input-section">
              <h4 class="section-title">{{ $t('tools.markdown.label.inputText') }}</h4>
              <el-input
                v-model="escapeInput"
                type="textarea"
                :rows="6"
                :placeholder="$t('tools.markdown.label.inputText') + '...'"
                style="width: 100%;"
              />
              <div class="field-toolbar">
                <span class="field-stats" v-if="escapeInput">
                  {{ escapeInput.length }} {{ $t('tools.markdown.label.chars') }}
                </span>
                <div class="toolbar-actions">
                  <el-button link size="small" @click="loadSample('escape')">{{ $t('tools.markdown.label.sample') }}</el-button>
                  <el-button link size="small" v-if="escapeInput || escapedOutput" @click="escapeInput = ''; escapedOutput = ''">{{ $t('tools.markdown.label.clear') }}</el-button>
                </div>
              </div>
            </div>
            <div class="action-section">
              <el-button type="primary" @click="escapeMarkdown" :loading="escaping">
                {{ $t('tools.markdown.label.escapeSpecialChars') }}
              </el-button>
            </div>
            <div class="output-section" v-if="escapedOutput">
              <h4 class="section-title">{{ $t('tools.markdown.label.escapedText') }}</h4>
              <el-input
                v-model="escapedOutput"
                type="textarea"
                :rows="6"
                readonly
                style="width: 100%;"
              />
              <div class="field-toolbar">
                <span class="field-stats">{{ escapedOutput.length }} {{ $t('tools.markdown.label.chars') }}</span>
                <el-button link size="small" type="primary" @click="copyText(escapedOutput)">
                  <el-icon><CopyDocument /></el-icon> {{ $t('tools.markdown.label.copy') }}
                </el-button>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane :label="$t('tools.markdown.label.unescapeSpecialChars')" name="unescape">
            <div class="input-section">
              <h4 class="section-title">{{ $t('tools.markdown.label.inputEscapedText') }}</h4>
              <el-input
                v-model="unescapeInput"
                type="textarea"
                :rows="6"
                :placeholder="$t('tools.markdown.label.inputEscapedText') + '...'"
                style="width: 100%;"
              />
              <div class="field-toolbar">
                <span class="field-stats" v-if="unescapeInput">
                  {{ unescapeInput.length }} {{ $t('tools.markdown.label.chars') }}
                </span>
                <div class="toolbar-actions">
                  <el-button link size="small" @click="loadSample('unescape')">{{ $t('tools.markdown.label.sample') }}</el-button>
                  <el-button link size="small" v-if="unescapeInput || unescapedOutput" @click="unescapeInput = ''; unescapedOutput = ''">{{ $t('tools.markdown.label.clear') }}</el-button>
                </div>
              </div>
            </div>
            <div class="action-section">
              <el-button type="primary" @click="unescapeMarkdown" :loading="unescaping">
                {{ $t('tools.markdown.label.unescapeSpecialChars') }}
              </el-button>
            </div>
            <div class="output-section" v-if="unescapedOutput">
              <h4 class="section-title">{{ $t('tools.markdown.label.unescapedText') }}</h4>
              <el-input
                v-model="unescapedOutput"
                type="textarea"
                :rows="6"
                readonly
                style="width: 100%;"
              />
              <div class="field-toolbar">
                <span class="field-stats">{{ unescapedOutput.length }} {{ $t('tools.markdown.label.chars') }}</span>
                <el-button link size="small" type="primary" @click="copyText(unescapedOutput)">
                  <el-icon><CopyDocument /></el-icon> {{ $t('tools.markdown.label.copy') }}
                </el-button>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-tab-pane>

      <!-- 提取链接和图片 -->
      <el-tab-pane :label="$t('tools.markdown.tab.extractLinks')" name="extract">
        <div class="input-section">
          <h4 class="section-title">{{ $t('tools.markdown.label.inputMarkdown') }}</h4>
          <el-input
            v-model="markdownInput"
            type="textarea"
            :rows="8"
            :placeholder="$t('tools.markdown.label.inputMarkdown') + '...'"
            style="width: 100%;"
          />
          <div class="field-toolbar">
            <span class="field-stats" v-if="markdownInput">
              {{ markdownInput.length }} {{ $t('tools.markdown.label.chars') }} · {{ lineCount(markdownInput) }} {{ $t('tools.markdown.label.lines') }}
            </span>
            <div class="toolbar-actions">
              <el-button link size="small" @click="loadSample('markdown')">{{ $t('tools.markdown.label.sample') }}</el-button>
            </div>
          </div>
        </div>
        <div class="action-section">
          <el-button type="primary" @click="extractLinks" :loading="extracting">
            {{ $t('tools.markdown.label.extractLinks') }}
          </el-button>
          <el-button type="primary" @click="extractImages" :loading="extracting">
            {{ $t('tools.markdown.label.extractImages') }}
          </el-button>
          <el-button @click="clearAll">{{ $t('tools.markdown.label.clear') }}</el-button>
        </div>
        <div class="output-section" v-if="extractedLinks.length > 0 || extractedImages.length > 0">
          <div v-if="extractedLinks.length > 0">
            <div class="field-toolbar">
              <h4 class="section-title" style="margin: 0;">{{ $t('tools.markdown.label.extractedLinks') }} ({{ extractedLinks.length }})</h4>
              <el-button link size="small" type="primary" @click="copyExtractedUrls(extractedLinks)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.markdown.label.copy') }}
              </el-button>
            </div>
            <el-table :data="extractedLinks" style="width: 100%; margin-bottom: 20px;">
              <el-table-column prop="text" :label="$t('tools.markdown.label.linkText')" width="200"></el-table-column>
              <el-table-column prop="url" label="URL"></el-table-column>
              <el-table-column prop="full_match" :label="$t('tools.markdown.label.fullMatch')" width="200"></el-table-column>
            </el-table>
          </div>
          <div v-if="extractedImages.length > 0">
            <div class="field-toolbar">
              <h4 class="section-title" style="margin: 0;">{{ $t('tools.markdown.label.extractedImages') }} ({{ extractedImages.length }})</h4>
              <el-button link size="small" type="primary" @click="copyExtractedImageUrls(extractedImages)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.markdown.label.copy') }}
              </el-button>
            </div>
            <el-table :data="extractedImages" style="width: 100%;">
              <el-table-column prop="alt" :label="$t('tools.markdown.label.altText')" width="150"></el-table-column>
              <el-table-column prop="url" :label="$t('tools.markdown.label.imageUrl')"></el-table-column>
              <el-table-column prop="title" :label="$t('tools.markdown.label.title')" width="150"></el-table-column>
              <el-table-column prop="full_match" :label="$t('tools.markdown.label.fullMatch')" width="200"></el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>

      <!-- HTML表格转Markdown -->
      <el-tab-pane :label="$t('tools.markdown.tab.htmlTableToMd')" name="table-convert">
        <ToolSection
          :input-label="$t('tools.markdown.label.inputHtmlTable')"
          :output-label="$t('tools.markdown.label.mdTableOutput')"
          :action-text="$t('tools.markdown.label.convert')"
          :loading="converting"
          :has-output="!!markdownTableOutput"
          @submit="convertTableToMarkdown"
        >
          <template #input>
            <el-input
              v-model="htmlTableInput"
              type="textarea"
              :rows="8"
              :placeholder="$t('tools.markdown.label.inputHtmlTable') + '...'"
              style="width: 100%;"
            />
            <div class="field-toolbar">
              <span class="field-stats" v-if="htmlTableInput">
                {{ htmlTableInput.length }} {{ $t('tools.markdown.label.chars') }}
              </span>
              <div class="toolbar-actions">
                <el-button link size="small" @click="loadSample('table')">{{ $t('tools.markdown.label.sample') }}</el-button>
              </div>
            </div>
          </template>
          <template #actions>
            <el-button type="primary" @click="convertTableToMarkdown" :loading="converting">
              {{ $t('tools.markdown.label.convert') }}
            </el-button>
            <el-button @click="htmlTableInput = ''; markdownTableOutput = ''; tableStats = null">{{ $t('tools.markdown.label.clear') }}</el-button>
          </template>
          <template #output>
            <el-input
              v-model="markdownTableOutput"
              type="textarea"
              :rows="8"
              readonly
              style="width: 100%;"
            />
            <div class="field-toolbar" v-if="markdownTableOutput">
              <span class="field-stats">
                {{ markdownTableOutput.length }} {{ $t('tools.markdown.label.chars') }} · {{ lineCount(markdownTableOutput) }} {{ $t('tools.markdown.label.lines') }}
              </span>
              <el-button link size="small" type="primary" @click="copyText(markdownTableOutput)">
                <el-icon><CopyDocument /></el-icon> {{ $t('tools.markdown.label.copy') }}
              </el-button>
            </div>
            <div class="stats" v-if="tableStats">
              <el-descriptions :column="2" size="small" border>
                <el-descriptions-item :label="$t('tools.markdown.label.columnCount')">
                  {{ tableStats.columns_count }}
                </el-descriptions-item>
                <el-descriptions-item :label="$t('tools.markdown.label.rowCount')">
                  {{ tableStats.rows_count }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </template>
        </ToolSection>
      </el-tab-pane>

      <!-- 语法验证 -->
      <el-tab-pane :label="$t('tools.markdown.tab.syntaxValidate')" name="validate">
        <div class="input-section">
          <h4 class="section-title">{{ $t('tools.markdown.label.inputMarkdown') }}</h4>
          <el-input
            v-model="markdownInput"
            type="textarea"
            :rows="8"
            :placeholder="$t('tools.markdown.label.inputMarkdown') + '...'"
            style="width: 100%;"
          />
          <div class="field-toolbar">
            <span class="field-stats" v-if="markdownInput">
              {{ markdownInput.length }} {{ $t('tools.markdown.label.chars') }} · {{ lineCount(markdownInput) }} {{ $t('tools.markdown.label.lines') }}
            </span>
            <div class="toolbar-actions">
              <el-button link size="small" @click="loadSample('markdown')">{{ $t('tools.markdown.label.sample') }}</el-button>
            </div>
          </div>
        </div>
        <div class="action-section">
          <el-button type="primary" @click="validateMarkdown" :loading="validating">
            {{ $t('tools.markdown.label.validateSyntax') }}
          </el-button>
          <el-button @click="clearAll">{{ $t('tools.markdown.label.clear') }}</el-button>
        </div>
        <div class="output-section" v-if="validationResult">
          <h4 class="section-title">{{ $t('tools.markdown.label.validateResult') }}</h4>
          <el-alert
            :title="validationResult.valid ? $t('tools.markdown.label.syntaxCorrect') : $t('tools.markdown.label.syntaxIssues')"
            :type="validationResult.valid ? 'success' : 'warning'"
            :description="$t('tools.markdown.label.issueCount', { count: validationResult.issues_count })"
            show-icon
            style="margin-bottom: 20px;"
          />
          <div v-if="validationResult.issues.length > 0">
            <h5>{{ $t('tools.markdown.label.issueList') }}:</h5>
            <el-tag
              v-for="(issue, index) in validationResult.issues"
              :key="index"
              type="danger"
              style="margin: 5px;"
            >
              {{ issue }}
            </el-tag>
          </div>
        </div>
      </el-tab-pane>

      <!-- 文档统计 -->
      <el-tab-pane :label="$t('tools.markdown.tab.docStats')" name="stats">
        <div class="input-section">
          <h4 class="section-title">{{ $t('tools.markdown.label.inputMarkdown') }}</h4>
          <el-input
            v-model="markdownInput"
            type="textarea"
            :rows="8"
            :placeholder="$t('tools.markdown.label.inputMarkdown') + '...'"
            style="width: 100%;"
          />
          <div class="field-toolbar">
            <span class="field-stats" v-if="markdownInput">
              {{ markdownInput.length }} {{ $t('tools.markdown.label.chars') }} · {{ lineCount(markdownInput) }} {{ $t('tools.markdown.label.lines') }}
            </span>
            <div class="toolbar-actions">
              <el-button link size="small" @click="loadSample('markdown')">{{ $t('tools.markdown.label.sample') }}</el-button>
            </div>
          </div>
        </div>
        <div class="action-section">
          <el-button type="primary" @click="getMarkdownStats" :loading="gettingStats">
            {{ $t('tools.markdown.label.docStats') }}
          </el-button>
          <el-button @click="clearAll">{{ $t('tools.markdown.label.clear') }}</el-button>
        </div>
        <div class="output-section" v-if="markdownStats">
          <h4 class="section-title">{{ $t('tools.markdown.label.docStats') }}</h4>
          <el-descriptions :column="descColumn" border>
            <el-descriptions-item :label="$t('tools.markdown.label.charCount')">
              {{ markdownStats.characters }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.charCountNoSpace')">
              {{ markdownStats.characters_no_spaces }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.wordCount')">
              {{ markdownStats.words }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.lineCount')">
              {{ markdownStats.lines }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.paragraphCount')">
              {{ markdownStats.paragraphs }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.linkCount')">
              {{ markdownStats.links }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.imageCount')">
              {{ markdownStats.images }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.codeBlockCount')">
              {{ markdownStats.code_blocks }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.inlineCodeCount')">
              {{ markdownStats.inline_codes }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.tableCount')">
              {{ markdownStats.tables }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.blockquoteCount')">
              {{ markdownStats.blockquotes }}
            </el-descriptions-item>
          </el-descriptions>

          <h4 class="section-title" style="margin-top: 20px;">{{ $t('tools.markdown.label.headingStats') }}</h4>
          <el-descriptions :column="descColumn" border>
            <el-descriptions-item :label="$t('tools.markdown.label.h1')">
              {{ markdownStats.headings.h1 }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.h2')">
              {{ markdownStats.headings.h2 }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.h3')">
              {{ markdownStats.headings.h3 }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.h4')">
              {{ markdownStats.headings.h4 }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.h5')">
              {{ markdownStats.headings.h5 }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.h6')">
              {{ markdownStats.headings.h6 }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.totalHeadings')" :span="3">
              {{ markdownStats.headings.total }}
            </el-descriptions-item>
          </el-descriptions>

          <h4 class="section-title" style="margin-top: 20px;">{{ $t('tools.markdown.label.headingStats') }}</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item :label="$t('tools.markdown.label.unorderedListItems')">
              {{ markdownStats.lists.unordered }}
            </el-descriptions-item>
            <el-descriptions-item :label="$t('tools.markdown.label.orderedListItems')">
              {{ markdownStats.lists.ordered }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-tab-pane>
    </el-tabs>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Document, CopyDocument } from '@element-plus/icons-vue'
import axios from 'axios'
import ToolPage from '@/components/ToolPage.vue'
import ToolSection from '@/components/ToolSection.vue'
import { useDeviceStore } from '@/stores/device.js'

const SAMPLES = {
  markdown: `# DevToolBox 使用指南

## 简介

**DevToolBox** 是一款开发者工具箱，集成了多种常用工具。

## 功能列表

1. **JSON工具** — 格式化、压缩、验证
2. **YAML工具** — 格式化、转换
3. **Markdown工具** — 转换、统计
4. **文件管理** — 上传、下载、分类

### 代码示例

\`\`\`python
def hello():
    print("Hello, DevToolBox!")
\`\`\`

> DevToolBox 让开发更高效！

| 工具 | 描述 | 状态 |
|------|------|------|
| JSON | 格式化与验证 | ✅ |
| YAML | 格式化与转换 | ✅ |

[官方网站](https://example.com) 和 [GitHub](https://github.com)

![Logo](https://example.com/logo.png "DevToolBox Logo")`,
  escape: '# Hello **World**\nThis is a `test` with *special* characters.\n> Blockquote with [link](https://example.com)',
  unescape: '\\# Hello \\\\*\\\\*World\\\\*\\\\*\nThis is a \\\\`test\\\\` with \\\\*special\\\\* characters.',
  table: `<table>
  <thead>
    <tr>
      <th>工具名称</th>
      <th>类型</th>
      <th>状态</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>JSON工具</td>
      <td>数据处理</td>
      <td>已完成</td>
    </tr>
    <tr>
      <td>YAML工具</td>
      <td>数据处理</td>
      <td>已完成</td>
    </tr>
    <tr>
      <td>Markdown工具</td>
      <td>文本处理</td>
      <td>已完成</td>
    </tr>
  </tbody>
</table>`
}

export default {
  name: 'MarkdownTools',
  components: {
    Document,
    CopyDocument,
    ToolPage,
    ToolSection
  },
  data() {
    const deviceStore = useDeviceStore()
    return {
      deviceStore,
      activeTab: 'to-html',
      escapeTab: 'escape',
      markdownInput: '',
      htmlOutput: '',
      fullHtmlOutput: '',
      plainOutput: '',
      converting: false,
      conversionStats: null,
      escapeInput: '',
      escapedOutput: '',
      escaping: false,
      unescapeInput: '',
      unescapedOutput: '',
      unescaping: false,
      extracting: false,
      extractedLinks: [],
      extractedImages: [],
      htmlTableInput: '',
      markdownTableOutput: '',
      tableStats: null,
      validating: false,
      validationResult: null,
      gettingStats: false,
      markdownStats: null
    }
  },
  computed: {
    descColumn() {
      return window.innerWidth <= 768 ? 1 : 3
    }
  },
  methods: {
    lineCount(text) {
      if (!text) return 0
      return text.split('\n').length
    },

    loadSample(type) {
      const sample = SAMPLES[type]
      if (!sample) return
      switch (type) {
        case 'markdown':
          this.markdownInput = sample
          break
        case 'escape':
          this.escapeInput = sample
          break
        case 'unescape':
          this.unescapeInput = sample
          break
        case 'table':
          this.htmlTableInput = sample
          break
      }
    },

    async copyText(text) {
      try {
        await navigator.clipboard.writeText(text)
        ElMessage.success(this.$t('tools.markdown.message.copied'))
      } catch {
        const ta = document.createElement('textarea')
        ta.value = text
        ta.style.position = 'fixed'
        ta.style.opacity = '0'
        document.body.appendChild(ta)
        ta.select()
        document.execCommand('copy')
        document.body.removeChild(ta)
        ElMessage.success(this.$t('tools.markdown.message.copied'))
      }
    },

    copyExtractedUrls(links) {
      const urls = links.map(l => l.url).join('\n')
      this.copyText(urls)
    },

    copyExtractedImageUrls(images) {
      const urls = images.map(i => i.url).join('\n')
      this.copyText(urls)
    },

    async convertToHtml() {
      if (!this.markdownInput) {
        ElMessage.warning(this.$t('tools.markdown.message.inputRequired'))
        return
      }
      this.converting = true
      try {
        const response = await axios.post('/api/markdown-tools/to-html', {
          markdown_text: this.markdownInput
        })
        if (response.data.success) {
          this.htmlOutput = response.data.html
          this.fullHtmlOutput = response.data.full_html
          this.conversionStats = {
            original_length: response.data.original_length,
            html_length: response.data.html_length,
            full_html_length: response.data.full_html_length
          }
          ElMessage.success(this.$t('tools.markdown.message.convertSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.markdown.message.convertFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.converting = false
      }
    },

    async convertToPlain() {
      if (!this.markdownInput) {
        ElMessage.warning(this.$t('tools.markdown.message.inputRequired'))
        return
      }
      this.converting = true
      try {
        const response = await axios.post('/api/markdown-tools/to-plain', {
          markdown_text: this.markdownInput
        })
        if (response.data.success) {
          this.plainOutput = response.data.plain_text
          this.conversionStats = {
            original_length: response.data.original_length,
            plain_length: response.data.plain_length
          }
          ElMessage.success(this.$t('tools.markdown.message.convertSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.markdown.message.convertFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.converting = false
      }
    },

    async escapeMarkdown() {
      if (!this.escapeInput) {
        ElMessage.warning(this.$t('tools.markdown.message.inputRequired'))
        return
      }
      this.escaping = true
      try {
        const response = await axios.post('/api/markdown-tools/escape', {
          text: this.escapeInput
        })
        if (response.data.success) {
          this.escapedOutput = response.data.escaped
          ElMessage.success(this.$t('tools.markdown.message.escapeSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.markdown.message.escapeFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.escaping = false
      }
    },

    async unescapeMarkdown() {
      if (!this.unescapeInput) {
        ElMessage.warning(this.$t('tools.markdown.message.inputRequired'))
        return
      }
      this.unescaping = true
      try {
        const response = await axios.post('/api/markdown-tools/unescape', {
          escaped_text: this.unescapeInput
        })
        if (response.data.success) {
          this.unescapedOutput = response.data.unescaped
          ElMessage.success(this.$t('tools.markdown.message.unescapeSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.markdown.message.unescapeFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.unescaping = false
      }
    },

    async extractLinks() {
      if (!this.markdownInput) {
        ElMessage.warning(this.$t('tools.markdown.message.inputRequired'))
        return
      }
      this.extracting = true
      try {
        const response = await axios.post('/api/markdown-tools/extract-links', {
          markdown_text: this.markdownInput
        })
        if (response.data.success) {
          this.extractedLinks = response.data.links
          this.extractedImages = []
          ElMessage.success(this.$t('tools.markdown.message.extractSuccess') + ' - ' + response.data.total_links)
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.markdown.message.extractFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.extracting = false
      }
    },

    async extractImages() {
      if (!this.markdownInput) {
        ElMessage.warning(this.$t('tools.markdown.message.inputRequired'))
        return
      }
      this.extracting = true
      try {
        const response = await axios.post('/api/markdown-tools/extract-images', {
          markdown_text: this.markdownInput
        })
        if (response.data.success) {
          this.extractedImages = response.data.images
          this.extractedLinks = []
          ElMessage.success(this.$t('tools.markdown.message.extractSuccess') + ' - ' + response.data.total_images)
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.markdown.message.extractFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.extracting = false
      }
    },

    async convertTableToMarkdown() {
      if (!this.htmlTableInput) {
        ElMessage.warning(this.$t('tools.markdown.message.inputRequired'))
        return
      }
      this.converting = true
      try {
        const response = await axios.post('/api/markdown-tools/table-to-markdown', {
          html_table: this.htmlTableInput
        })
        if (response.data.success) {
          this.markdownTableOutput = response.data.markdown_table
          this.tableStats = {
            columns_count: response.data.columns_count,
            rows_count: response.data.rows_count
          }
          ElMessage.success(this.$t('tools.markdown.message.convertSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.markdown.message.convertFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.converting = false
      }
    },

    async validateMarkdown() {
      if (!this.markdownInput) {
        ElMessage.warning(this.$t('tools.markdown.message.inputRequired'))
        return
      }
      this.validating = true
      try {
        const response = await axios.post('/api/markdown-tools/validate', {
          markdown_text: this.markdownInput
        })
        if (response.data.success) {
          this.validationResult = response.data
          if (response.data.valid) {
            ElMessage.success(this.$t('tools.markdown.message.validateSuccess'))
          } else {
            ElMessage.warning(this.$t('tools.markdown.label.syntaxIssues') + ' - ' + response.data.issues_count)
          }
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.markdown.message.validateFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.validating = false
      }
    },

    async getMarkdownStats() {
      if (!this.markdownInput) {
        ElMessage.warning(this.$t('tools.markdown.message.inputRequired'))
        return
      }
      this.gettingStats = true
      try {
        const response = await axios.post('/api/markdown-tools/stats', {
          markdown_text: this.markdownInput
        })
        if (response.data.success) {
          this.markdownStats = response.data.stats
          ElMessage.success(this.$t('tools.markdown.message.statsSuccess'))
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error(this.$t('tools.markdown.message.statsFail') + ': ' + error.response?.data?.error || error.message)
      } finally {
        this.gettingStats = false
      }
    },

    downloadHtml() {
      if (!this.fullHtmlOutput) {
        ElMessage.warning(this.$t('tools.markdown.message.inputRequired'))
        return
      }
      try {
        const blob = new Blob([this.fullHtmlOutput], { type: 'text/html;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url

        let filename = 'markdown-document.html'
        const lines = this.markdownInput.split('\n')
        for (const line of lines) {
          if (line.trim().startsWith('# ')) {
            const title = line.trim().substring(2).trim()
            filename = title.replace(/[^a-zA-Z0-9一-龥\-_]/g, '-').substring(0, 50) + '.html'
            break
          }
        }

        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        ElMessage.success(this.$t('tools.markdown.message.downloadSuccess'))
      } catch (error) {
        ElMessage.error(this.$t('tools.markdown.message.downloadFail') + ': ' + error.message)
      }
    },

    clearAll() {
      this.markdownInput = ''
      this.htmlOutput = ''
      this.fullHtmlOutput = ''
      this.plainOutput = ''
      this.escapeInput = ''
      this.escapedOutput = ''
      this.unescapeInput = ''
      this.unescapedOutput = ''
      this.extractedLinks = []
      this.extractedImages = []
      this.htmlTableInput = ''
      this.markdownTableOutput = ''
      this.validationResult = null
      this.markdownStats = null
      this.conversionStats = null
      this.tableStats = null
    }
  }
}
</script>

<style scoped>
.field-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6px;
  min-height: 24px;
}

.field-stats {
  font-size: 12px;
  color: var(--dt-text-secondary);
  line-height: 24px;
}

.toolbar-actions {
  display: flex;
  gap: 4px;
  align-items: center;
}

.stats {
  margin-top: var(--dt-spacing-md);
}

@media (max-width: 768px) {
  .action-section {
    flex-direction: column;
  }
  .action-section .el-button {
    width: 100%;
    margin-left: 0 !important;
    margin-top: 8px;
  }
  .tool-section {
    flex-direction: column;
  }
  .input-section,
  .output-section {
    width: 100% !important;
    max-width: 100% !important;
  }
}
</style>
