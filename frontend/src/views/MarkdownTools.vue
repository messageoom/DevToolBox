<template>
  <div class="markdown-tools">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><Document /></el-icon>
          <span>Markdown工具</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="Markdown转HTML" name="to-html">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入Markdown文本</h4>
              <el-input
                v-model="markdownInput"
                type="textarea"
                :rows="8"
                placeholder="请输入Markdown文本..."
                style="width: 100%;"
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="convertToHtml" :loading="converting">
                转换
              </el-button>
              <el-button @click="clearAll">清空</el-button>
            </div>
            <div class="output-section" v-if="htmlOutput">
              <h4>HTML输出</h4>
              <el-input
                v-model="htmlOutput"
                type="textarea"
                :rows="8"
                readonly
                style="width: 100%;"
              />
              <div class="stats" v-if="conversionStats">
                <el-descriptions :column="2" size="small" border>
                  <el-descriptions-item label="原始长度">
                    {{ conversionStats.original_length }} 字符
                  </el-descriptions-item>
                  <el-descriptions-item label="输出长度">
                    {{ conversionStats.html_length }} 字符
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="Markdown转纯文本" name="to-plain">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入Markdown文本</h4>
              <el-input
                v-model="markdownInput"
                type="textarea"
                :rows="8"
                placeholder="请输入Markdown文本..."
                style="width: 100%;"
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="convertToPlain" :loading="converting">
                转换
              </el-button>
              <el-button @click="clearAll">清空</el-button>
            </div>
            <div class="output-section" v-if="plainOutput">
              <h4>纯文本输出</h4>
              <el-input
                v-model="plainOutput"
                type="textarea"
                :rows="8"
                readonly
                style="width: 100%;"
              />
              <div class="stats" v-if="conversionStats">
                <el-descriptions :column="2" size="small" border>
                  <el-descriptions-item label="原始长度">
                    {{ conversionStats.original_length }} 字符
                  </el-descriptions-item>
                  <el-descriptions-item label="输出长度">
                    {{ conversionStats.plain_length }} 字符
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="转义/反转义" name="escape">
          <div class="tool-section">
            <el-tabs v-model="escapeTab">
              <el-tab-pane label="转义特殊字符" name="escape">
                <div class="input-section">
                  <h4>输入文本</h4>
                  <el-input
                    v-model="escapeInput"
                    type="textarea"
                    :rows="6"
                    placeholder="输入包含Markdown特殊字符的文本..."
                    style="width: 100%;"
                  />
                </div>
                <div class="action-section">
                  <el-button type="primary" @click="escapeMarkdown" :loading="escaping">
                    转义
                  </el-button>
                </div>
                <div class="output-section" v-if="escapedOutput">
                  <h4>转义后的文本</h4>
                  <el-input
                    v-model="escapedOutput"
                    type="textarea"
                    :rows="6"
                    readonly
                    style="width: 100%;"
                  />
                </div>
              </el-tab-pane>

              <el-tab-pane label="反转义特殊字符" name="unescape">
                <div class="input-section">
                  <h4>输入转义文本</h4>
                  <el-input
                    v-model="unescapeInput"
                    type="textarea"
                    :rows="6"
                    placeholder="输入已转义的Markdown文本..."
                    style="width: 100%;"
                  />
                </div>
                <div class="action-section">
                  <el-button type="primary" @click="unescapeMarkdown" :loading="unescaping">
                    反转义
                  </el-button>
                </div>
                <div class="output-section" v-if="unescapedOutput">
                  <h4>反转义后的文本</h4>
                  <el-input
                    v-model="unescapedOutput"
                    type="textarea"
                    :rows="6"
                    readonly
                    style="width: 100%;"
                  />
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-tab-pane>

        <el-tab-pane label="提取链接和图片" name="extract">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入Markdown文本</h4>
              <el-input
                v-model="markdownInput"
                type="textarea"
                :rows="8"
                placeholder="请输入包含链接和图片的Markdown文本..."
                style="width: 100%;"
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="extractLinks" :loading="extracting">
                提取链接
              </el-button>
              <el-button type="primary" @click="extractImages" :loading="extracting">
                提取图片
              </el-button>
              <el-button @click="clearAll">清空</el-button>
            </div>
            <div class="output-section" v-if="extractedLinks.length > 0 || extractedImages.length > 0">
              <div v-if="extractedLinks.length > 0">
                <h4>提取的链接 ({{ extractedLinks.length }}个)</h4>
                <el-table :data="extractedLinks" style="width: 100%; margin-bottom: 20px;">
                  <el-table-column prop="text" label="链接文本" width="200"></el-table-column>
                  <el-table-column prop="url" label="URL"></el-table-column>
                  <el-table-column prop="full_match" label="完整匹配" width="200"></el-table-column>
                </el-table>
              </div>
              <div v-if="extractedImages.length > 0">
                <h4>提取的图片 ({{ extractedImages.length }}个)</h4>
                <el-table :data="extractedImages" style="width: 100%;">
                  <el-table-column prop="alt" label="替代文本" width="150"></el-table-column>
                  <el-table-column prop="url" label="图片URL"></el-table-column>
                  <el-table-column prop="title" label="标题" width="150"></el-table-column>
                  <el-table-column prop="full_match" label="完整匹配" width="200"></el-table-column>
                </el-table>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="HTML表格转Markdown" name="table-convert">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入HTML表格</h4>
              <el-input
                v-model="htmlTableInput"
                type="textarea"
                :rows="8"
                placeholder="请输入HTML表格代码..."
                style="width: 100%;"
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="convertTableToMarkdown" :loading="converting">
                转换
              </el-button>
              <el-button @click="clearAll">清空</el-button>
            </div>
            <div class="output-section" v-if="markdownTableOutput">
              <h4>Markdown表格输出</h4>
              <el-input
                v-model="markdownTableOutput"
                type="textarea"
                :rows="8"
                readonly
                style="width: 100%;"
              />
              <div class="stats" v-if="tableStats">
                <el-descriptions :column="2" size="small" border>
                  <el-descriptions-item label="列数">
                    {{ tableStats.columns_count }}
                  </el-descriptions-item>
                  <el-descriptions-item label="行数">
                    {{ tableStats.rows_count }}
                  </el-descriptions-item>
                </el-descriptions>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane label="语法验证" name="validate">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入Markdown文本</h4>
              <el-input
                v-model="markdownInput"
                type="textarea"
                :rows="8"
                placeholder="请输入要验证的Markdown文本..."
                style="width: 100%;"
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="validateMarkdown" :loading="validating">
                验证语法
              </el-button>
              <el-button @click="clearAll">清空</el-button>
            </div>
            <div class="output-section" v-if="validationResult">
              <h4>验证结果</h4>
              <el-alert
                :title="validationResult.valid ? '语法正确' : '发现语法问题'"
                :type="validationResult.valid ? 'success' : 'warning'"
                :description="`发现 ${validationResult.issues_count} 个问题`"
                show-icon
                style="margin-bottom: 20px;"
              />
              <div v-if="validationResult.issues.length > 0">
                <h5>问题列表：</h5>
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
          </div>
        </el-tab-pane>

        <el-tab-pane label="文档统计" name="stats">
          <div class="tool-section">
            <div class="input-section">
              <h4>输入Markdown文本</h4>
              <el-input
                v-model="markdownInput"
                type="textarea"
                :rows="8"
                placeholder="请输入Markdown文本进行统计..."
                style="width: 100%;"
              />
            </div>
            <div class="action-section">
              <el-button type="primary" @click="getMarkdownStats" :loading="gettingStats">
                获取统计
              </el-button>
              <el-button @click="clearAll">清空</el-button>
            </div>
            <div class="output-section" v-if="markdownStats">
              <h4>文档统计</h4>
              <el-descriptions :column="3" border>
                <el-descriptions-item label="字符数">
                  {{ markdownStats.characters }}
                </el-descriptions-item>
                <el-descriptions-item label="字符数(不含空格)">
                  {{ markdownStats.characters_no_spaces }}
                </el-descriptions-item>
                <el-descriptions-item label="单词数">
                  {{ markdownStats.words }}
                </el-descriptions-item>
                <el-descriptions-item label="行数">
                  {{ markdownStats.lines }}
                </el-descriptions-item>
                <el-descriptions-item label="段落数">
                  {{ markdownStats.paragraphs }}
                </el-descriptions-item>
                <el-descriptions-item label="链接数">
                  {{ markdownStats.links }}
                </el-descriptions-item>
                <el-descriptions-item label="图片数">
                  {{ markdownStats.images }}
                </el-descriptions-item>
                <el-descriptions-item label="代码块数">
                  {{ markdownStats.code_blocks }}
                </el-descriptions-item>
                <el-descriptions-item label="行内代码数">
                  {{ markdownStats.inline_codes }}
                </el-descriptions-item>
                <el-descriptions-item label="表格数">
                  {{ markdownStats.tables }}
                </el-descriptions-item>
                <el-descriptions-item label="引用块数">
                  {{ markdownStats.blockquotes }}
                </el-descriptions-item>
              </el-descriptions>

              <h4 style="margin-top: 20px;">标题统计</h4>
              <el-descriptions :column="3" border>
                <el-descriptions-item label="H1标题">
                  {{ markdownStats.headings.h1 }}
                </el-descriptions-item>
                <el-descriptions-item label="H2标题">
                  {{ markdownStats.headings.h2 }}
                </el-descriptions-item>
                <el-descriptions-item label="H3标题">
                  {{ markdownStats.headings.h3 }}
                </el-descriptions-item>
                <el-descriptions-item label="H4标题">
                  {{ markdownStats.headings.h4 }}
                </el-descriptions-item>
                <el-descriptions-item label="H5标题">
                  {{ markdownStats.headings.h5 }}
                </el-descriptions-item>
                <el-descriptions-item label="H6标题">
                  {{ markdownStats.headings.h6 }}
                </el-descriptions-item>
                <el-descriptions-item label="标题总数" :span="3">
                  {{ markdownStats.headings.total }}
                </el-descriptions-item>
              </el-descriptions>

              <h4 style="margin-top: 20px;">列表统计</h4>
              <el-descriptions :column="2" border>
                <el-descriptions-item label="无序列表项">
                  {{ markdownStats.lists.unordered }}
                </el-descriptions-item>
                <el-descriptions-item label="有序列表项">
                  {{ markdownStats.lists.ordered }}
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
import { Document } from '@element-plus/icons-vue'
import axios from 'axios'

export default {
  name: 'MarkdownTools',
  components: {
    Document
  },
  data() {
    return {
      activeTab: 'to-html',
      escapeTab: 'escape',

      // 转换相关
      markdownInput: '',
      htmlOutput: '',
      plainOutput: '',
      converting: false,
      conversionStats: null,

      // 转义相关
      escapeInput: '',
      escapedOutput: '',
      escaping: false,
      unescapeInput: '',
      unescapedOutput: '',
      unescaping: false,

      // 提取相关
      extracting: false,
      extractedLinks: [],
      extractedImages: [],

      // 表格转换相关
      htmlTableInput: '',
      markdownTableOutput: '',
      tableStats: null,

      // 验证相关
      validating: false,
      validationResult: null,

      // 统计相关
      gettingStats: false,
      markdownStats: null
    }
  },
  methods: {
    async convertToHtml() {
      if (!this.markdownInput) {
        ElMessage.warning('请输入Markdown文本')
        return
      }

      this.converting = true
      try {
        const response = await axios.post('/api/markdown-tools/to-html', {
          markdown_text: this.markdownInput
        })

        if (response.data.success) {
          this.htmlOutput = response.data.html
          this.conversionStats = {
            original_length: response.data.original_length,
            html_length: response.data.html_length
          }
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

    async convertToPlain() {
      if (!this.markdownInput) {
        ElMessage.warning('请输入Markdown文本')
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

    async escapeMarkdown() {
      if (!this.escapeInput) {
        ElMessage.warning('请输入文本')
        return
      }

      this.escaping = true
      try {
        const response = await axios.post('/api/markdown-tools/escape', {
          text: this.escapeInput
        })

        if (response.data.success) {
          this.escapedOutput = response.data.escaped
          ElMessage.success('转义成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('转义失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.escaping = false
      }
    },

    async unescapeMarkdown() {
      if (!this.unescapeInput) {
        ElMessage.warning('请输入转义文本')
        return
      }

      this.unescaping = true
      try {
        const response = await axios.post('/api/markdown-tools/unescape', {
          escaped_text: this.unescapeInput
        })

        if (response.data.success) {
          this.unescapedOutput = response.data.unescaped
          ElMessage.success('反转义成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('反转义失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.unescaping = false
      }
    },

    async extractLinks() {
      if (!this.markdownInput) {
        ElMessage.warning('请输入Markdown文本')
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
          ElMessage.success(`提取成功，发现 ${response.data.total_links} 个链接`)
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('提取失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.extracting = false
      }
    },

    async extractImages() {
      if (!this.markdownInput) {
        ElMessage.warning('请输入Markdown文本')
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
          ElMessage.success(`提取成功，发现 ${response.data.total_images} 个图片`)
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('提取失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.extracting = false
      }
    },

    async convertTableToMarkdown() {
      if (!this.htmlTableInput) {
        ElMessage.warning('请输入HTML表格')
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

    async validateMarkdown() {
      if (!this.markdownInput) {
        ElMessage.warning('请输入Markdown文本')
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
            ElMessage.success('语法验证通过')
          } else {
            ElMessage.warning(`发现 ${response.data.issues_count} 个语法问题`)
          }
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('验证失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.validating = false
      }
    },

    async getMarkdownStats() {
      if (!this.markdownInput) {
        ElMessage.warning('请输入Markdown文本')
        return
      }

      this.gettingStats = true
      try {
        const response = await axios.post('/api/markdown-tools/stats', {
          markdown_text: this.markdownInput
        })

        if (response.data.success) {
          this.markdownStats = response.data.stats
          ElMessage.success('统计完成')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('统计失败: ' + error.response?.data?.error || error.message)
      } finally {
        this.gettingStats = false
      }
    },

    clearAll() {
      this.markdownInput = ''
      this.htmlOutput = ''
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
.markdown-tools {
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

.stats {
  margin-top: 15px;
}
</style>
