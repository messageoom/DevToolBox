<template>
  <div v-if="privateKey || publicKey" class="key-pair-display">
    <el-row :gutter="20">
      <el-col :span="12" class="key-col">
        <h4>{{ t('tools.crypto.shared.privateKey') }}</h4>
        <el-input
          :model-value="privateKey"
          type="textarea"
          :rows="rows"
          readonly
        />
        <el-button @click="handleCopy(privateKey)" size="small" class="copy-btn">
          {{ t('tools.crypto.shared.copyPrivateKey') }}
        </el-button>
      </el-col>
      <el-col :span="12" class="key-col">
        <h4>{{ t('tools.crypto.shared.publicKey') }}</h4>
        <el-input
          :model-value="publicKey"
          type="textarea"
          :rows="rows"
          readonly
        />
        <el-button @click="handleCopy(publicKey)" size="small" class="copy-btn">
          {{ t('tools.crypto.shared.copyPublicKey') }}
        </el-button>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { copyToClipboard } from '@/utils/format.js'

const { t } = useI18n()

defineProps({
  privateKey: {
    type: String,
    default: ''
  },
  publicKey: {
    type: String,
    default: ''
  },
  rows: {
    type: Number,
    default: 8
  }
})

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
.key-pair-display {
  margin-top: 20px;
}

.key-col h4 {
  margin-bottom: 10px;
  color: var(--dt-text-primary, #333);
  font-weight: bold;
}

.copy-btn {
  margin-top: 10px;
}

@media (max-width: 768px) {
  .key-pair-display :deep(.el-col) {
    max-width: 100%;
    flex: 0 0 100%;
    margin-bottom: 16px;
  }
}
</style>
