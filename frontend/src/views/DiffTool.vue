<template>
  <ToolPage :title="$t('tools.diff.title')" :icon="DocumentCopy">
    <div class="diff-tool">
      <!-- Input section -->
      <div class="input-section">
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <h4 class="section-title">{{ $t('tools.diff.originalText') }}</h4>
            <el-input
              v-model="oldText"
              type="textarea"
              :rows="10"
              :placeholder="$t('tools.diff.placeholder')"
              clearable
            />
          </el-col>
          <el-col :xs="24" :sm="12">
            <h4 class="section-title">{{ $t('tools.diff.modifiedText') }}</h4>
            <el-input
              v-model="newText"
              type="textarea"
              :rows="10"
              :placeholder="$t('tools.diff.placeholder')"
              clearable
            />
          </el-col>
        </el-row>

        <div class="action-buttons">
          <el-button type="primary" @click="computeDiff">{{ $t('tools.diff.compare') }}</el-button>
          <el-button @click="swapTexts">{{ $t('tools.diff.swap') }}</el-button>
          <el-button @click="clearAll">{{ $t('tools.diff.clear') }}</el-button>
          <el-button v-if="diffResult.length > 0" @click="copyDiff">{{ $t('tools.diff.copyResult') }}</el-button>
        </div>

        <div class="stats-row" v-if="diffResult.length > 0">
          <el-tag type="success">{{ $t('tools.diff.addedLines', { count: stats.added }) }}</el-tag>
          <el-tag type="danger">{{ $t('tools.diff.deletedLines', { count: stats.removed }) }}</el-tag>
          <el-tag type="warning">{{ $t('tools.diff.modifiedLines', { count: stats.modified }) }}</el-tag>
          <el-tag type="info">{{ $t('tools.diff.sameLines', { count: stats.same }) }}</el-tag>
        </div>
      </div>

      <!-- Diff output tabs -->
      <el-tabs v-model="viewMode" class="diff-tabs">
        <el-tab-pane :label="$t('tools.diff.unifiedView')" name="unified">
          <div class="diff-container" v-if="diffResult.length > 0">
            <div class="diff-scroll-wrapper">
              <div
                v-for="(item, index) in diffResult"
                :key="index"
                :class="['diff-line', item.type]"
              >
                <span class="diff-marker">{{ item.type === 'add' ? '+' : item.type === 'remove' ? '-' : ' ' }}</span>
                <span class="diff-line-num">{{ item.oldIndex !== null ? item.oldIndex + 1 : '' }}</span>
                <span class="diff-line-num">{{ item.newIndex !== null ? item.newIndex + 1 : '' }}</span>
                <span class="diff-content">{{ item.line }}</span>
              </div>
            </div>
          </div>
          <el-empty v-else :description="$t('tools.diff.placeholder')" />
        </el-tab-pane>

        <el-tab-pane :label="$t('tools.diff.sideBySideView')" name="side-by-side">
          <div class="side-by-side-container" v-if="diffResult.length > 0">
            <div class="side-by-side-wrapper">
              <!-- Left column: old text -->
              <div class="side-column old-column">
                <div class="column-header">{{ $t('tools.diff.originalText') }}</div>
                <div class="column-body">
                  <div
                    v-for="(item, index) in sideBySideLeft"
                    :key="'left-' + index"
                    :class="['diff-line', item.type]"
                  >
                    <span class="diff-line-num">{{ item.lineNum !== null ? item.lineNum : '' }}</span>
                    <span class="diff-content">{{ item.line }}</span>
                  </div>
                </div>
              </div>
              <!-- Right column: new text -->
              <div class="side-column new-column">
                <div class="column-header">{{ $t('tools.diff.modifiedText') }}</div>
                <div class="column-body">
                  <div
                    v-for="(item, index) in sideBySideRight"
                    :key="'right-' + index"
                    :class="['diff-line', item.type]"
                  >
                    <span class="diff-line-num">{{ item.lineNum !== null ? item.lineNum : '' }}</span>
                    <span class="diff-content">{{ item.line }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else :description="$t('tools.diff.placeholder')" />
        </el-tab-pane>
      </el-tabs>
    </div>
  </ToolPage>
</template>

<script>
import { DocumentCopy } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ToolPage from '@/components/ToolPage.vue'

function computeLCS(a, b) {
  const dp = Array(a.length + 1).fill(null).map(() => Array(b.length + 1).fill(0))
  for (let i = 1; i <= a.length; i++) {
    for (let j = 1; j <= b.length; j++) {
      if (a[i - 1] === b[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1] + 1
      } else {
        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1])
      }
    }
  }
  const pairs = []
  let i = a.length
  let j = b.length
  while (i > 0 && j > 0) {
    if (a[i - 1] === b[j - 1]) {
      pairs.unshift([i - 1, j - 1])
      i--
      j--
    } else if (dp[i - 1][j] >= dp[i][j - 1]) {
      i--
    } else {
      j--
    }
  }
  return pairs
}

function buildDiffResult(oldLines, newLines, lcsPairs) {
  const result = []
  let oldIdx = 0
  let newIdx = 0
  let pairIdx = 0

  while (oldIdx < oldLines.length || newIdx < newLines.length) {
    if (pairIdx < lcsPairs.length && oldIdx === lcsPairs[pairIdx][0] && newIdx === lcsPairs[pairIdx][1]) {
      result.push({
        type: 'same',
        line: oldLines[oldIdx],
        oldIndex: oldIdx,
        newIndex: newIdx
      })
      oldIdx++
      newIdx++
      pairIdx++
    } else if (pairIdx < lcsPairs.length && oldIdx === lcsPairs[pairIdx][0]) {
      // Need to advance newIdx to match — lines were added
      result.push({
        type: 'add',
        line: newLines[newIdx],
        oldIndex: null,
        newIndex: newIdx
      })
      newIdx++
    } else if (pairIdx < lcsPairs.length && newIdx === lcsPairs[pairIdx][1]) {
      // Need to advance oldIdx to match — lines were removed
      result.push({
        type: 'remove',
        line: oldLines[oldIdx],
        oldIndex: oldIdx,
        newIndex: null
      })
      oldIdx++
    } else {
      // Neither matches next LCS pair — this is a modification region
      // We output remove then add for the same conceptual position
      if (oldIdx < oldLines.length && (pairIdx >= lcsPairs.length || oldIdx < lcsPairs[pairIdx][0])) {
        result.push({
          type: 'remove',
          line: oldLines[oldIdx],
          oldIndex: oldIdx,
          newIndex: null
        })
        oldIdx++
      }
      if (newIdx < newLines.length && (pairIdx >= lcsPairs.length || newIdx < lcsPairs[pairIdx][1])) {
        result.push({
          type: 'add',
          line: newLines[newIdx],
          oldIndex: null,
          newIndex: newIdx
        })
        newIdx++
      }
    }
  }

  return result
}

export default {
  name: 'DiffTool',
  components: {
    DocumentCopy,
    ToolPage
  },
  data() {
    return {
      oldText: '',
      newText: '',
      diffResult: [],
      viewMode: 'unified',
      stats: {
        added: 0,
        removed: 0,
        modified: 0,
        same: 0
      }
    }
  },
  computed: {
    sideBySideLeft() {
      const left = []
      for (const item of this.diffResult) {
        if (item.type === 'same') {
          left.push({ type: 'same', line: item.line, lineNum: item.oldIndex + 1 })
        } else if (item.type === 'remove') {
          left.push({ type: 'remove', line: item.line, lineNum: item.oldIndex + 1 })
        } else if (item.type === 'add') {
          // Placeholder to keep alignment
          left.push({ type: 'empty', line: '', lineNum: null })
        }
      }
      return left
    },
    sideBySideRight() {
      const right = []
      for (const item of this.diffResult) {
        if (item.type === 'same') {
          right.push({ type: 'same', line: item.line, lineNum: item.newIndex + 1 })
        } else if (item.type === 'add') {
          right.push({ type: 'add', line: item.line, lineNum: item.newIndex + 1 })
        } else if (item.type === 'remove') {
          // Placeholder to keep alignment
          right.push({ type: 'empty', line: '', lineNum: null })
        }
      }
      return right
    }
  },
  methods: {
    computeDiff() {
      const oldLines = this.oldText.split('\n')
      const newLines = this.newText.split('\n')

      const lcs = computeLCS(oldLines, newLines)
      this.diffResult = buildDiffResult(oldLines, newLines, lcs)

      // Compute stats
      let added = 0
      let removed = 0
      let same = 0
      let modified = 0

      // Detect modified lines: count consecutive remove+add pairs as modified
      let i = 0
      while (i < this.diffResult.length) {
        const item = this.diffResult[i]
        if (item.type === 'same') {
          same++
          i++
        } else if (item.type === 'remove') {
          // Check if next is an add — if so, count as modified
          if (i + 1 < this.diffResult.length && this.diffResult[i + 1].type === 'add') {
            modified++
            removed++
            added++
            i += 2
          } else {
            removed++
            i++
          }
        } else if (item.type === 'add') {
          // Check if previous was remove (should have been caught above, but handle standalone adds)
          added++
          i++
        } else {
          i++
        }
      }

      this.stats = { added, removed, modified, same }
    },
    swapTexts() {
      const temp = this.oldText
      this.oldText = this.newText
      this.newText = temp
      if (this.diffResult.length > 0) {
        this.computeDiff()
      }
    },
    clearAll() {
      this.oldText = ''
      this.newText = ''
      this.diffResult = []
      this.stats = { added: 0, removed: 0, modified: 0, same: 0 }
    },
    copyDiff() {
      const lines = this.diffResult.map(item => {
        const marker = item.type === 'add' ? '+' : item.type === 'remove' ? '-' : ' '
        return marker + ' ' + item.line
      })
      navigator.clipboard.writeText(lines.join('\n')).then(() => {
        ElMessage.success(this.$t('tools.diff.copiedToClipboard'))
      }).catch(() => {
        ElMessage.error(this.$t('tools.diff.copyFail'))
      })
    }
  }
}
</script>

<style scoped>
.diff-tool {
  display: flex;
  flex-direction: column;
  gap: var(--dt-spacing-md);
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: var(--dt-spacing-md);
}

.section-title {
  margin: 0 0 var(--dt-spacing-sm) 0;
  font-size: var(--dt-font-size-base);
  color: var(--dt-text-primary);
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: var(--dt-spacing-sm);
  flex-wrap: wrap;
}

.stats-row {
  display: flex;
  gap: var(--dt-spacing-sm);
  flex-wrap: wrap;
}

.diff-tabs {
  margin-top: var(--dt-spacing-sm);
}

.diff-container {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.5;
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
  overflow: hidden;
}

.diff-scroll-wrapper {
  max-height: 500px;
  overflow-y: auto;
}

.diff-line {
  display: flex;
  padding: 2px 8px;
  white-space: pre-wrap;
  word-break: break-all;
  min-height: 22px;
}

.diff-line.same {
  background: transparent;
}

.diff-line.add {
  background: #e6ffed;
  border-left: 3px solid var(--dt-success);
}

.diff-line.remove {
  background: #ffe6e6;
  border-left: 3px solid var(--dt-danger);
}

.diff-line.empty {
  background: var(--dt-bg-page);
}

.diff-marker {
  width: 24px;
  flex-shrink: 0;
  text-align: center;
  color: var(--dt-text-secondary);
  font-weight: bold;
  user-select: none;
}

.diff-line-num {
  width: 40px;
  text-align: right;
  padding-right: 8px;
  color: var(--dt-text-secondary);
  flex-shrink: 0;
  border-right: 1px solid var(--dt-border-light);
  user-select: none;
}

.diff-content {
  padding-left: 8px;
  flex: 1;
}

/* Side-by-side view */
.side-by-side-container {
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.5;
  border: 1px solid var(--dt-border-light);
  border-radius: var(--dt-radius-md);
  overflow: hidden;
}

.side-by-side-wrapper {
  display: grid;
  grid-template-columns: 1fr 1fr;
  max-height: 500px;
  overflow-y: auto;
}

.side-column {
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--dt-border-light);
}

.side-column:last-child {
  border-right: none;
}

.column-header {
  padding: 8px;
  background: var(--dt-bg-hover);
  border-bottom: 1px solid var(--dt-border-light);
  font-weight: 600;
  text-align: center;
  color: var(--dt-text-primary);
  position: sticky;
  top: 0;
  z-index: 1;
}

.column-body .diff-line {
  padding: 2px 4px;
}

.column-body .diff-line-num {
  width: 36px;
  padding-right: 6px;
}

.column-body .diff-line.add {
  background: #e6ffed;
}

.column-body .diff-line.remove {
  background: #ffe6e6;
}

.column-body .diff-line.empty {
  background: var(--dt-bg-page);
  min-height: 22px;
}

/* Responsive: stack input textareas vertically */
@media (max-width: 768px) {
  .side-by-side-wrapper {
    grid-template-columns: 1fr;
  }

  .side-column {
    border-right: none;
    border-bottom: 1px solid var(--dt-border-light);
  }

  .side-column:last-child {
    border-bottom: none;
  }
}
</style>
