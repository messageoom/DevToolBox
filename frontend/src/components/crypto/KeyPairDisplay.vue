<template>
  <div v-if="privateKey || publicKey" class="key-pair-display">
    <el-row :gutter="20">
      <el-col :span="12" class="key-col">
        <h4>私钥</h4>
        <el-input
          :model-value="privateKey"
          type="textarea"
          :rows="rows"
          readonly
        />
        <el-button @click="handleCopy(privateKey)" size="small" class="copy-btn">
          复制私钥
        </el-button>
      </el-col>
      <el-col :span="12" class="key-col">
        <h4>公钥</h4>
        <el-input
          :model-value="publicKey"
          type="textarea"
          :rows="rows"
          readonly
        />
        <el-button @click="handleCopy(publicKey)" size="small" class="copy-btn">
          复制公钥
        </el-button>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ElMessage } from 'element-plus'

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

function handleCopy(text) {
  navigator.clipboard.writeText(text).then(() => {
    ElMessage.success('已复制到剪贴板')
  }).catch(() => {
    ElMessage.error('复制失败')
  })
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
