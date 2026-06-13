<template>
  <div class="sign-verify-panel">
    <el-tabs v-model="activeTab">
      <el-tab-pane :label="t('tools.crypto.shared.sign')" name="sign">
        <el-form :model="signForm" label-width="120px">
          <el-form-item :label="t('tools.crypto.shared.message')">
            <el-input
              v-model="signForm.message"
              type="textarea"
              :rows="4"
              :placeholder="t('tools.crypto.shared.signMessagePlaceholder')"
            />
          </el-form-item>
          <el-form-item :label="t('tools.crypto.shared.privateKey')">
            <el-input
              v-model="signForm.privateKey"
              type="textarea"
              :rows="4"
              :placeholder="t('tools.crypto.shared.privateKeyPlaceholder')"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSign" :loading="signing">
              {{ algorithm }}{{ t('tools.crypto.shared.sign') }}
            </el-button>
          </el-form-item>
          <el-form-item v-if="signResult" :label="t('tools.crypto.shared.signature')">
            <el-input
              :model-value="signResult"
              type="textarea"
              :rows="4"
              readonly
            />
            <el-button @click="handleCopy(signResult)" size="small" style="margin-top: 10px;">
              {{ t('tools.crypto.shared.copySignature') }}
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane :label="t('tools.crypto.shared.verify')" name="verify">
        <el-form :model="verifyForm" label-width="120px">
          <el-form-item :label="t('tools.crypto.shared.message')">
            <el-input
              v-model="verifyForm.message"
              type="textarea"
              :rows="4"
              :placeholder="t('tools.crypto.shared.verifyMessagePlaceholder')"
            />
          </el-form-item>
          <el-form-item :label="t('tools.crypto.shared.signature')">
            <el-input
              v-model="verifyForm.signature"
              type="textarea"
              :rows="4"
              :placeholder="t('tools.crypto.shared.signaturePlaceholder')"
            />
          </el-form-item>
          <el-form-item :label="t('tools.crypto.shared.publicKey')">
            <el-input
              v-model="verifyForm.publicKey"
              type="textarea"
              :rows="4"
              :placeholder="t('tools.crypto.shared.publicKeyPlaceholder')"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleVerify" :loading="verifying">
              {{ algorithm }}{{ t('tools.crypto.shared.verify') }}
            </el-button>
          </el-form-item>
          <el-form-item v-if="verifyResult !== null" :label="t('tools.crypto.shared.verifyResult')">
            <el-tag :type="verifyResult ? 'success' : 'danger'">
              {{ verifyResult ? t('tools.crypto.shared.signatureValid') : t('tools.crypto.shared.signatureInvalid') }}
            </el-tag>
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
import { copyToClipboard } from '@/utils/format.js'

const { t } = useI18n()

const props = defineProps({
  algorithm: { type: String, required: true },
  signing: { type: Boolean, default: false },
  verifying: { type: Boolean, default: false },
  signResult: { type: String, default: '' },
  verifyResult: { type: [Boolean, null], default: null }
})

const emit = defineEmits(['sign', 'verify'])

const activeTab = ref('sign')

const signForm = reactive({
  message: '',
  privateKey: ''
})

const verifyForm = reactive({
  message: '',
  signature: '',
  publicKey: ''
})

function handleSign() {
  if (!signForm.message.trim()) {
    ElMessage.warning(t('tools.crypto.shared.inputSignMessageWarning'))
    return
  }
  if (!signForm.privateKey.trim()) {
    ElMessage.warning(t('tools.crypto.shared.inputPrivateKeyWarning'))
    return
  }
  emit('sign', { ...signForm })
}

function handleVerify() {
  if (!verifyForm.message.trim()) {
    ElMessage.warning(t('tools.crypto.shared.inputVerifyMessageWarning'))
    return
  }
  if (!verifyForm.signature.trim()) {
    ElMessage.warning(t('tools.crypto.shared.inputSignatureWarning'))
    return
  }
  if (!verifyForm.publicKey.trim()) {
    ElMessage.warning(t('tools.crypto.shared.inputPublicKeyWarning'))
    return
  }
  emit('verify', { ...verifyForm })
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
.sign-verify-panel {
  width: 100%;
}
</style>
