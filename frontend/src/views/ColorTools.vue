<template>
  <ToolPage :title="$t('tools.color.title')" :icon="Brush">
    <div class="tool-section">
      <el-tabs v-model="activeTab">
        <!-- Converter tab -->
        <el-tab-pane :label="$t('tools.color.tab.converter')" name="converter">
          <div class="picker-row">
            <div class="picker-swatch" :style="{ background: hex }">
              <input
                type="color"
                v-model="hex"
                class="native-color-input"
                :aria-label="$t('tools.color.labels.picker')"
                @input="onPickerInput"
              />
            </div>
            <div class="picker-hex">
              <div class="field-label">{{ $t('tools.color.labels.hex') }}</div>
              <el-input v-model="hex" @change="onHexInput">
                <template #prepend>#</template>
              </el-input>
            </div>
          </div>

          <!-- Format cards -->
          <div class="format-grid">
            <div class="format-item">
              <div class="field-label">HEX</div>
              <div class="format-line">
                <el-input :model-value="hexDisplay" readonly />
                <el-button @click="copyText(hexDisplay)">
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
              </div>
            </div>
            <div class="format-item">
              <div class="field-label">RGB</div>
              <div class="format-line">
                <el-input :model-value="rgbText" readonly />
                <el-button @click="copyText(rgbText)">
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
              </div>
            </div>
            <div class="format-item">
              <div class="field-label">HSL</div>
              <div class="format-line">
                <el-input :model-value="hslText" readonly />
                <el-button @click="copyText(hslText)">
                  <el-icon><CopyDocument /></el-icon>
                </el-button>
              </div>
            </div>
          </div>

          <!-- Shade palette -->
          <div class="output-section">
            <div class="result-header">
              <h4 class="section-title">{{ $t('tools.color.labels.shades') }}</h4>
            </div>
            <div class="swatch-row">
              <div
                v-for="s in shades"
                :key="s.hex"
                class="swatch"
                :style="{ background: s.hex }"
                :title="$t('tools.color.messages.clickToCopy')"
                @click="copyText(s.hex)"
              >
                <span class="swatch-label" :style="{ color: s.text }">{{ s.hex }}</span>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- Contrast tab -->
        <el-tab-pane :label="$t('tools.color.tab.contrast')" name="contrast">
          <div class="config-row">
            <div class="config-item">
              <div class="field-label">{{ $t('tools.color.labels.foreground') }}</div>
              <div class="picker-inline">
                <input type="color" v-model="hex" class="native-color-input-sm" @input="onPickerInput" />
                <el-input v-model="hex" size="small" @change="onHexInput" />
              </div>
            </div>
            <div class="config-item">
              <div class="field-label">{{ $t('tools.color.labels.background') }}</div>
              <div class="picker-inline">
                <input type="color" v-model="bgHex" class="native-color-input-sm" @input="bgHex = $event.target.value" />
                <el-input v-model="bgHex" size="small" @change="bgHex = normalizeHex(bgHex)" />
              </div>
            </div>
          </div>

          <!-- Contrast results -->
          <div class="output-section">
            <div class="contrast-preview" :style="{ background: bgHex, color: hex }">
              <span class="preview-large">Aa</span>
              <span class="preview-small">{{ $t('tools.color.labels.previewText') }}</span>
            </div>

            <div class="ratio-box">
              <span class="ratio-label">{{ $t('tools.color.labels.contrastRatio') }}</span>
              <span class="ratio-value">{{ contrastRatio.toFixed(2) }}:1</span>
            </div>

            <div class="wcag-grid">
              <div class="wcag-item">
                <div class="wcag-name">{{ $t('tools.color.labels.aaNormal') }} (4.5:1)</div>
                <el-tag :type="passesAA(4.5) ? 'success' : 'danger'" effect="dark">
                  {{ passesAA(4.5) ? $t('tools.color.labels.pass') : $t('tools.color.labels.fail') }}
                </el-tag>
              </div>
              <div class="wcag-item">
                <div class="wcag-name">{{ $t('tools.color.labels.aaLarge') }} (3:1)</div>
                <el-tag :type="passesAA(3) ? 'success' : 'danger'" effect="dark">
                  {{ passesAA(3) ? $t('tools.color.labels.pass') : $t('tools.color.labels.fail') }}
                </el-tag>
              </div>
              <div class="wcag-item">
                <div class="wcag-name">{{ $t('tools.color.labels.aaaNormal') }} (7:1)</div>
                <el-tag :type="passesAA(7) ? 'success' : 'danger'" effect="dark">
                  {{ passesAA(7) ? $t('tools.color.labels.pass') : $t('tools.color.labels.fail') }}
                </el-tag>
              </div>
              <div class="wcag-item">
                <div class="wcag-name">{{ $t('tools.color.labels.aaaLarge') }} (4.5:1)</div>
                <el-tag :type="passesAA(4.5) ? 'success' : 'danger'" effect="dark">
                  {{ passesAA(4.5) ? $t('tools.color.labels.pass') : $t('tools.color.labels.fail') }}
                </el-tag>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </ToolPage>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Brush, CopyDocument } from '@element-plus/icons-vue'
import ToolPage from '@/components/ToolPage.vue'
import { copyToClipboard } from '@/utils/format.js'

export default {
  name: 'ColorTools',
  components: { Brush, CopyDocument, ToolPage },
  data() {
    return {
      activeTab: 'converter',
      hex: '#409eff',
      bgHex: '#ffffff'
    }
  },
  computed: {
    rgb() {
      return this.hexToRgb(this.hex) || { r: 0, g: 0, b: 0 }
    },
    hsl() {
      return this.rgbToHsl(this.rgb.r, this.rgb.g, this.rgb.b)
    },
    hexDisplay() {
      return this.hex.toUpperCase()
    },
    rgbText() {
      return `rgb(${this.rgb.r}, ${this.rgb.g}, ${this.rgb.b})`
    },
    hslText() {
      const h = this.hsl
      return `hsl(${h.h}, ${h.s}%, ${h.l}%)`
    },
    shades() {
      const base = this.hsl
      const list = []
      const stops = [90, 70, 50, 30, 10]
      stops.forEach((l) => {
        const rgb = this.hslToRgb(base.h, base.s, l)
        const hx = this.rgbToHex(rgb.r, rgb.g, rgb.b)
        list.push({ hex: hx.toUpperCase(), text: l > 55 ? '#000' : '#fff' })
      })
      return list
    },
    contrastRatio() {
      return this.computeContrast(this.hex, this.bgHex)
    }
  },
  methods: {
    onPickerInput(e) {
      this.hex = e.target.value
    },
    onHexInput() {
      this.hex = this.normalizeHex(this.hex)
    },
    normalizeHex(input) {
      if (!input) return '#000000'
      let s = String(input).trim().replace(/^#/, '')
      if (/^[0-9a-fA-F]{3}$/.test(s)) {
        s = s.split('').map((c) => c + c).join('')
      }
      if (!/^[0-9a-fA-F]{6}$/.test(s)) {
        return '#000000'
      }
      return '#' + s.toLowerCase()
    },
    hexToRgb(hx) {
      const s = this.normalizeHex(hx).slice(1)
      return {
        r: parseInt(s.slice(0, 2), 16),
        g: parseInt(s.slice(2, 4), 16),
        b: parseInt(s.slice(4, 6), 16)
      }
    },
    rgbToHex(r, g, b) {
      const toHex = (n) => {
        const v = Math.max(0, Math.min(255, Math.round(n)))
        return v.toString(16).padStart(2, '0')
      }
      return '#' + toHex(r) + toHex(g) + toHex(b)
    },
    rgbToHsl(r, g, b) {
      r /= 255; g /= 255; b /= 255
      const max = Math.max(r, g, b)
      const min = Math.min(r, g, b)
      let h = 0
      let s = 0
      const l = (max + min) / 2
      if (max !== min) {
        const d = max - min
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
        switch (max) {
          case r: h = (g - b) / d + (g < b ? 6 : 0); break
          case g: h = (b - r) / d + 2; break
          case b: h = (r - g) / d + 4; break
        }
        h /= 6
      }
      return { h: Math.round(h * 360), s: Math.round(s * 100), l: Math.round(l * 100) }
    },
    hslToRgb(h, s, l) {
      h /= 360; s /= 100; l /= 100
      let r, g, b
      if (s === 0) {
        r = g = b = l
      } else {
        const hue2rgb = (p, q, t) => {
          if (t < 0) t += 1
          if (t > 1) t -= 1
          if (t < 1 / 6) return p + (q - p) * 6 * t
          if (t < 1 / 2) return q
          if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6
          return p
        }
        const q = l < 0.5 ? l * (1 + s) : l + s - l * s
        const p = 2 * l - q
        r = hue2rgb(p, q, h + 1 / 3)
        g = hue2rgb(p, q, h)
        b = hue2rgb(p, q, h - 1 / 3)
      }
      return { r: r * 255, g: g * 255, b: b * 255 }
    },
    relativeLuminance(hx) {
      const rgb = this.hexToRgb(hx)
      const channel = (c) => {
        c /= 255
        return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
      }
      return 0.2126 * channel(rgb.r) + 0.7152 * channel(rgb.g) + 0.0722 * channel(rgb.b)
    },
    computeContrast(fg, bg) {
      const l1 = this.relativeLuminance(fg)
      const l2 = this.relativeLuminance(bg)
      const lighter = Math.max(l1, l2)
      const darker = Math.min(l1, l2)
      return (lighter + 0.05) / (darker + 0.05)
    },
    passesAA(threshold) {
      return this.contrastRatio >= threshold
    },
    async copyText(text) {
      if (!text) return
      try {
        await copyToClipboard(text)
        ElMessage.success(this.$t('common.copySuccess'))
      } catch {
        ElMessage.error(this.$t('common.copyFail'))
      }
    }
  }
}
</script>

<style scoped>
.tool-section {
  padding-bottom: var(--dt-spacing-md, 16px);
}

.picker-row {
  display: flex;
  gap: var(--dt-spacing-md, 16px);
  align-items: flex-end;
  margin-bottom: var(--dt-spacing-lg, 20px);
}

.picker-swatch {
  position: relative;
  width: 72px;
  height: 72px;
  border-radius: var(--dt-radius-md, 6px);
  border: 1px solid var(--dt-border-light, #dcdfe6);
  overflow: hidden;
  box-shadow: var(--dt-shadow-sm, 0 1px 4px rgba(0,0,0,0.08));
  flex-shrink: 0;
}

.native-color-input {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  border: none;
  padding: 0;
}

.native-color-input-sm {
  width: 40px;
  height: 32px;
  padding: 0;
  border: 1px solid var(--dt-border-light, #dcdfe6);
  border-radius: var(--dt-radius-md, 6px);
  background: none;
  cursor: pointer;
  flex-shrink: 0;
}

.picker-hex {
  flex: 1;
}

.picker-inline {
  display: flex;
  gap: var(--dt-spacing-sm, 8px);
  align-items: center;
}

.picker-inline :deep(.el-input) {
  flex: 1;
}

.field-label {
  font-size: var(--dt-font-size-sm, 13px);
  color: var(--dt-text-secondary, #909399);
  margin-bottom: var(--dt-spacing-xs, 6px);
}

.config-row {
  display: flex;
  gap: var(--dt-spacing-md, 16px);
  margin-bottom: var(--dt-spacing-md, 16px);
  align-items: flex-end;
  flex-wrap: wrap;
}

.config-item {
  flex: 1;
  min-width: 200px;
}

.format-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--dt-spacing-md, 16px);
}

.format-item {
  display: flex;
  flex-direction: column;
}

.format-line {
  display: flex;
  gap: var(--dt-spacing-xs, 4px);
}

.format-line :deep(.el-input) {
  flex: 1;
}

.section-title {
  font-size: var(--dt-font-size-base, 14px);
  font-weight: 600;
  color: var(--dt-text-primary, #303133);
  margin: 0 0 var(--dt-spacing-sm, 8px) 0;
}

.output-section {
  margin-top: var(--dt-spacing-lg, 20px);
}

.result-header {
  margin-bottom: var(--dt-spacing-sm, 8px);
}

.swatch-row {
  display: flex;
  gap: var(--dt-spacing-sm, 8px);
  flex-wrap: wrap;
}

.swatch {
  flex: 1;
  min-width: 90px;
  height: 72px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  border-radius: var(--dt-radius-md, 6px);
  cursor: pointer;
  border: 1px solid var(--dt-border-light, #dcdfe6);
  transition: transform var(--dt-transition-fast, 0.2s);
}

.swatch:hover {
  transform: translateY(-2px);
}

.swatch-label {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: var(--dt-font-size-xs, 12px);
  font-weight: 600;
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.75);
  border-radius: 3px;
  margin-bottom: var(--dt-spacing-xs, 4px);
}

.contrast-preview {
  display: flex;
  align-items: center;
  gap: var(--dt-spacing-md, 16px);
  padding: var(--dt-spacing-lg, 20px);
  border-radius: var(--dt-radius-md, 6px);
  border: 1px solid var(--dt-border-light, #dcdfe6);
  margin-bottom: var(--dt-spacing-md, 16px);
}

.preview-large {
  font-size: 36px;
  font-weight: 700;
}

.preview-small {
  font-size: var(--dt-font-size-base, 14px);
}

.ratio-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--dt-spacing-md, 16px);
  background: var(--dt-bg-section, #f5f7fa);
  border: 1px solid var(--dt-border-light, #dcdfe6);
  border-radius: var(--dt-radius-md, 6px);
  margin-bottom: var(--dt-spacing-md, 16px);
}

.ratio-label {
  font-size: var(--dt-font-size-base, 14px);
  color: var(--dt-text-secondary, #909399);
}

.ratio-value {
  font-size: var(--dt-font-size-lg, 18px);
  font-weight: 700;
  color: var(--dt-primary, #409eff);
}

.wcag-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--dt-spacing-sm, 8px);
}

.wcag-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--dt-spacing-sm, 8px) var(--dt-spacing-md, 12px);
  background: var(--dt-bg-section, #f5f7fa);
  border: 1px solid var(--dt-border-light, #dcdfe6);
  border-radius: var(--dt-radius-md, 6px);
}

.wcag-name {
  font-size: var(--dt-font-size-sm, 13px);
  color: var(--dt-text-primary, #303133);
}

@media (max-width: 768px) {
  .picker-row {
    flex-direction: column;
    align-items: stretch;
    gap: var(--dt-spacing-sm, 8px);
  }

  .picker-swatch {
    width: 100%;
    height: 56px;
  }

  .format-grid {
    grid-template-columns: 1fr;
  }

  .config-row {
    flex-direction: column;
  }

  .config-item {
    min-width: 100%;
  }

  .wcag-grid {
    grid-template-columns: 1fr;
  }

  .output-section {
    padding: var(--dt-spacing-md, 16px);
    background: var(--dt-bg-section, #f5f7fa);
    border-radius: var(--dt-radius-lg, 12px);
    border: 1px solid var(--dt-border-lighter, #ebeef5);
  }
}
</style>
