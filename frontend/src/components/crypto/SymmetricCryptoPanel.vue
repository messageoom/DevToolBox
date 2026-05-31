<template>
  <div class="symmetric-crypto-panel">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="加密" name="encrypt">
        <el-form :model="encryptForm" label-width="120px">
          <el-form-item label="明文">
            <el-input
              v-model="encryptForm.plaintext"
              type="textarea"
              :rows="4"
              placeholder="请输入要加密的文本..."
            />
          </el-form-item>
          <el-form-item label="密钥">
            <el-input
              v-model="encryptForm.key"
              type="textarea"
              :rows="keyRows"
              :placeholder="keyPlaceholder"
            />
            <div v-if="showKeyGenerate" style="margin-top: 5px;">
              <el-button @click="$emit('generateKey')" size="small">生成密钥</el-button>
            </div>
          </el-form-item>
          <el-form-item v-if="modes && modes.length > 0" label="模式">
            <el-select v-model="encryptForm.mode">
              <el-option
                v-for="mode in modes"
                :key="mode.value"
                :label="mode.label"
                :value="mode.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleEncrypt" :loading="encrypting">
              {{ algorithm }}加密
            </el-button>
          </el-form-item>
          <el-form-item v-if="encryptResult" label="密文">
            <el-input
              :model-value="encryptResult"
              type="textarea"
              :rows="4"
              readonly
            />
            <el-button @click="handleCopy(encryptResult)" size="small" style="margin-top: 10px;">
              复制密文
            </el-button>
          </el-form-item>
          <el-form-item v-if="encryptIV" :label="ivLabel">
            <el-input
              :model-value="encryptIV"
              type="textarea"
              :rows="2"
              readonly
            />
            <el-button @click="handleCopy(encryptIV)" size="small" style="margin-top: 10px;">
              复制{{ ivLabel }}
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="解密" name="decrypt">
        <el-form :model="decryptForm" label-width="120px">
          <el-form-item label="密文">
            <el-input
              v-model="decryptForm.ciphertext"
              type="textarea"
              :rows="4"
              placeholder="请输入要解密的密文..."
            />
          </el-form-item>
          <el-form-item label="密钥">
            <el-input
              v-model="decryptForm.key"
              type="textarea"
              :rows="keyRows"
              :placeholder="keyPlaceholder"
            />
          </el-form-item>
          <el-form-item v-if="modes && modes.length > 0" label="模式">
            <el-select v-model="decryptForm.mode">
              <el-option
                v-for="mode in modes"
                :key="mode.value"
                :label="mode.label"
                :value="mode.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item
            v-if="showDecryptIV"
            :label="ivLabel"
          >
            <el-input
              v-model="decryptForm.iv"
              type="textarea"
              :rows="2"
              :placeholder="ivPlaceholder"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleDecrypt" :loading="decrypting">
              {{ algorithm }}解密
            </el-button>
          </el-form-item>
          <el-form-item v-if="decryptResult" label="明文">
            <el-input
              :model-value="decryptResult"
              type="textarea"
              :rows="4"
              readonly
            />
            <el-button @click="handleCopy(decryptResult)" size="small" style="margin-top: 10px;">
              复制明文
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  algorithm: { type: String, required: true },
  modes: { type: Array, default: () => [] },
  encrypting: { type: Boolean, default: false },
  decrypting: { type: Boolean, default: false },
  encryptResult: { type: String, default: '' },
  decryptResult: { type: String, default: '' },
  encryptIV: { type: String, default: '' },
  showKeyGenerate: { type: Boolean, default: false },
  keyPlaceholder: { type: String, default: '请输入密钥...' },
  keyRows: { type: Number, default: 3 },
  ivLabel: { type: String, default: 'IV' },
  ivPlaceholder: { type: String, default: '请输入IV...' },
  hasNonce: { type: Boolean, default: false },
  defaultMode: { type: String, default: '' },
  generatedKey: { type: String, default: '' }
})

const emit = defineEmits(['encrypt', 'decrypt', 'generateKey'])

const activeTab = ref('encrypt')

const encryptForm = reactive({
  plaintext: '',
  key: '',
  mode: props.defaultMode
})

const decryptForm = reactive({
  ciphertext: '',
  key: '',
  mode: props.defaultMode,
  iv: ''
})

const showDecryptIV = computed(() => {
  if (props.hasNonce) return true
  if (props.modes.length > 0 && decryptForm.mode !== 'ECB') return true
  return false
})

watch(() => props.defaultMode, (val) => {
  if (val) {
    encryptForm.mode = val
    decryptForm.mode = val
  }
})

watch(() => props.generatedKey, (val) => {
  if (val) {
    encryptForm.key = val
  }
})

function handleEncrypt() {
  if (!encryptForm.plaintext.trim()) {
    ElMessage.warning('请输入要加密的文本')
    return
  }
  if (!encryptForm.key.trim()) {
    ElMessage.warning('请输入密钥')
    return
  }
  emit('encrypt', { ...encryptForm })
}

function handleDecrypt() {
  if (!decryptForm.ciphertext.trim()) {
    ElMessage.warning('请输入要解密的密文')
    return
  }
  if (!decryptForm.key.trim()) {
    ElMessage.warning('请输入密钥')
    return
  }
  if (showDecryptIV.value && !decryptForm.iv.trim()) {
    ElMessage.warning(`请输入${props.ivLabel}`)
    return
  }
  emit('decrypt', { ...decryptForm })
}

function handleCopy(text) {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
}
</script>

<style scoped>
.symmetric-crypto-panel {
  width: 100%;
}
</style>
