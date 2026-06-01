<template>
  <div class="public-key-crypto-panel">
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
          <el-form-item :label="t('tools.crypto.shared.publicKey')">
            <el-input
              v-model="encryptForm.publicKey"
              type="textarea"
              :rows="6"
              :placeholder="t('tools.crypto.shared.publicKeyPlaceholder')"
            />
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
          <el-form-item :label="t('tools.crypto.shared.privateKey')">
            <el-input
              v-model="decryptForm.privateKey"
              type="textarea"
              :rows="6"
              :placeholder="t('tools.crypto.shared.privateKeyPlaceholder')"
            />
          </el-form-item>
          <el-form-item v-if="showDecryptPublicKey" :label="t('tools.crypto.shared.publicKey')">
            <el-input
              v-model="decryptForm.publicKey"
              type="textarea"
              :rows="4"
              :placeholder="t('tools.crypto.shared.publicKeyPlaceholder')"
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
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  algorithm: { type: String, required: true },
  encrypting: { type: Boolean, default: false },
  decrypting: { type: Boolean, default: false },
  encryptResult: { type: String, default: '' },
  decryptResult: { type: String, default: '' },
  showDecryptPublicKey: { type: Boolean, default: false }
})

const emit = defineEmits(['encrypt', 'decrypt'])

const activeTab = ref('encrypt')

const encryptForm = reactive({
  plaintext: '',
  publicKey: ''
})

const decryptForm = reactive({
  ciphertext: '',
  privateKey: '',
  publicKey: ''
})

function handleEncrypt() {
  if (!encryptForm.plaintext.trim()) {
    ElMessage.warning(t('tools.crypto.shared.inputPlaintextWarning'))
    return
  }
  if (!encryptForm.publicKey.trim()) {
    ElMessage.warning(t('tools.crypto.shared.inputPublicKeyWarning'))
    return
  }
  emit('encrypt', { ...encryptForm })
}

function handleDecrypt() {
  if (!decryptForm.ciphertext.trim()) {
    ElMessage.warning(t('tools.crypto.shared.inputCiphertextWarning'))
    return
  }
  if (!decryptForm.privateKey.trim()) {
    ElMessage.warning(t('tools.crypto.shared.inputPrivateKeyWarning'))
    return
  }
  if (props.showDecryptPublicKey && !decryptForm.publicKey.trim()) {
    ElMessage.warning(t('tools.crypto.shared.inputPublicKeyWarning'))
    return
  }
  emit('decrypt', { ...decryptForm })
}

function handleCopy(text) {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success(t('common.copySuccess'))
  }).catch(() => {
    ElMessage.error(t('common.copyFail'))
  })
}
</script>

<style scoped>
.public-key-crypto-panel {
  width: 100%;
}
</style>
