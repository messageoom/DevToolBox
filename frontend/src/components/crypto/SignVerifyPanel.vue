<template>
  <div class="sign-verify-panel">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="签名" name="sign">
        <el-form :model="signForm" label-width="120px">
          <el-form-item label="消息">
            <el-input
              v-model="signForm.message"
              type="textarea"
              :rows="4"
              placeholder="请输入要签名的消息..."
            />
          </el-form-item>
          <el-form-item label="私钥">
            <el-input
              v-model="signForm.privateKey"
              type="textarea"
              :rows="4"
              placeholder="请输入私钥..."
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSign" :loading="signing">
              {{ algorithm }}签名
            </el-button>
          </el-form-item>
          <el-form-item v-if="signResult" label="签名">
            <el-input
              :model-value="signResult"
              type="textarea"
              :rows="4"
              readonly
            />
            <el-button @click="handleCopy(signResult)" size="small" style="margin-top: 10px;">
              复制签名
            </el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="验证" name="verify">
        <el-form :model="verifyForm" label-width="120px">
          <el-form-item label="消息">
            <el-input
              v-model="verifyForm.message"
              type="textarea"
              :rows="4"
              placeholder="请输入要验证的消息..."
            />
          </el-form-item>
          <el-form-item label="签名">
            <el-input
              v-model="verifyForm.signature"
              type="textarea"
              :rows="4"
              placeholder="请输入签名..."
            />
          </el-form-item>
          <el-form-item label="公钥">
            <el-input
              v-model="verifyForm.publicKey"
              type="textarea"
              :rows="4"
              placeholder="请输入公钥..."
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleVerify" :loading="verifying">
              {{ algorithm }}验证
            </el-button>
          </el-form-item>
          <el-form-item v-if="verifyResult !== null" label="验证结果">
            <el-tag :type="verifyResult ? 'success' : 'danger'">
              {{ verifyResult ? '签名有效' : '签名无效' }}
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
    ElMessage.warning('请输入要签名的消息')
    return
  }
  if (!signForm.privateKey.trim()) {
    ElMessage.warning('请输入私钥')
    return
  }
  emit('sign', { ...signForm })
}

function handleVerify() {
  if (!verifyForm.message.trim()) {
    ElMessage.warning('请输入要验证的消息')
    return
  }
  if (!verifyForm.signature.trim()) {
    ElMessage.warning('请输入签名')
    return
  }
  if (!verifyForm.publicKey.trim()) {
    ElMessage.warning('请输入公钥')
    return
  }
  emit('verify', { ...verifyForm })
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
.sign-verify-panel {
  width: 100%;
}
</style>
