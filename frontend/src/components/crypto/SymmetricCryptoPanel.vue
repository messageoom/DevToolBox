<template>
  <div class="symmetric-crypto-panel">
    <el-tabs v-model="activeTab">
      <el-tab-pane :label="t('tools.crypto.shared.encrypt')" name="encrypt">
        <el-form :model="encryptForm" label-width="120px">
          <el-form-item :label="t('tools.crypto.shared.plaintext')">
            <el-input
              v-model="encryptForm.plaintext"
              type="textarea"
              :rows="4"
              :placeholder="t('tools.crypto.shared.encryptPlaceholder')"
            />
          </el-form-item>
          <el-form-item :label="t('tools.crypto.shared.key')">
            <el-input
              v-model="encryptForm.key"
              type="textarea"
              :rows="keyRows"
              :placeholder="keyPlaceholder"
            />
            <div v-if="showKeyGenerate" style="margin-top: 5px;">
              <el-button @click="$emit('generateKey')" size="small">{{ t('tools.crypto.shared.generateKey') }}</el-button>
            </div>
          </el-form-item>
          <el-form-item v-if="modes && modes.length > 0" :label="t('tools.crypto.shared.mode')"  >
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
              {{ algorithm }}{{ t('tools.crypto.shared.encrypt') }}
            </el-button>
          </el-form-item>
          <el-form-item v-if="encryptResult" :label="t('tools.crypto.shared.ciphertext')">
            <el-input
              :model-value="encryptResult"
              type="textarea"
              :rows="4"
              readonly
            />
            <el-button @click="handleCopy(encryptResult)" size="small" style="margin-top: 10px;">
              {{ t('tools.crypto.shared.copyCiphertext') }}
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
              {{ t('tools.crypto.shared.copy') }}{{ ivLabel }}
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane :label="t('tools.crypto.shared.decrypt')" name="decrypt">
        <el-form :model="decryptForm" label-width="120px">
          <el-form-item :label="t('tools.crypto.shared.ciphertext')">
            <el-input
              v-model="decryptForm.ciphertext"
              type="textarea"
              :rows="4"
              :placeholder="t('tools.crypto.shared.decryptPlaceholder')"
            />
          </el-form-item>
          <el-form-item :label="t('tools.crypto.shared.key')">
            <el-input
              v-model="decryptForm.key"
              type="textarea"
              :rows="keyRows"
              :placeholder="keyPlaceholder"
            />
          </el-form-item>
          <el-form-item v-if="modes && modes.length > 0" :label="t('tools.crypto.shared.mode')">
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
              {{ algorithm }}{{ t('tools.crypto.shared.decrypt') }}
            </el-button>
          </el-form-item>
          <el-form-item v-if="decryptResult" :label="t('tools.crypto.shared.plaintext')">
            <el-input
              :model-value="decryptResult"
              type="textarea"
              :rows="4"
              readonly
            />
            <el-button @click="handleCopy(decryptResult)" size="small" style="margin-top: 10px;">
              {{ t('tools.crypto.shared.copyPlaintext') }}
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
import { useI18n } from 'vue-i18n'
import { copyToClipboard } from '@/utils/format.js'

const { t } = useI18n()

const props = defineProps({
  algorithm: { type: String, required: true },
  modes: { type: Array, default: () => [] },
  encrypting: { type: Boolean, default: false },
  decrypting: { type: Boolean, default: false },
  encryptResult: { type: String, default: '' },
  decryptResult: { type: String, default: '' },
  encryptIV: { type: String, default: '' },
  showKeyGenerate: { type: Boolean, default: false },
  keyPlaceholder: { type: String, default: '' },
  keyRows: { type: Number, default: 3 },
  ivLabel: { type: String, default: 'IV' },
  ivPlaceholder: { type: String, default: '' },
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
    ElMessage.warning(t('tools.crypto.shared.inputPlaintextWarning'))
    return
  }
  if (!encryptForm.key.trim()) {
    ElMessage.warning(t('tools.crypto.shared.inputKeyWarning'))
    return
  }
  emit('encrypt', { ...encryptForm })
}

function handleDecrypt() {
  if (!decryptForm.ciphertext.trim()) {
    ElMessage.warning(t('tools.crypto.shared.inputCiphertextWarning'))
    return
  }
  if (!decryptForm.key.trim()) {
    ElMessage.warning(t('tools.crypto.shared.inputKeyWarning'))
    return
  }
  if (showDecryptIV.value && !decryptForm.iv.trim()) {
    ElMessage.warning(t('tools.crypto.shared.inputIvWarning', { label: props.ivLabel }))
    return
  }
  emit('decrypt', { ...decryptForm })
}

async function handleCopy(text) {
  try {
    await copyToClipboard(text)
    ElMessage.success(t('common.copySuccess'))
  } catch {
    ElMessage.error(t('common.copyFail'))
  }
}
</script>

<style scoped>
.symmetric-crypto-panel {
  width: 100%;
}
</style>
