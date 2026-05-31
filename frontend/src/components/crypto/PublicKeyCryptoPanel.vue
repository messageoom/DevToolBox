<template>
  <div class="public-key-crypto-panel">
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
          <el-form-item label="公钥">
            <el-input
              v-model="encryptForm.publicKey"
              type="textarea"
              :rows="6"
              placeholder="请输入公钥..."
            />
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
          <el-form-item label="私钥">
            <el-input
              v-model="decryptForm.privateKey"
              type="textarea"
              :rows="6"
              placeholder="请输入私钥..."
            />
          </el-form-item>
          <el-form-item v-if="showDecryptPublicKey" label="公钥">
            <el-input
              v-model="decryptForm.publicKey"
              type="textarea"
              :rows="4"
              placeholder="请输入公钥..."
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
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

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
    ElMessage.warning('请输入要加密的文本')
    return
  }
  if (!encryptForm.publicKey.trim()) {
    ElMessage.warning('请输入公钥')
    return
  }
  emit('encrypt', { ...encryptForm })
}

function handleDecrypt() {
  if (!decryptForm.ciphertext.trim()) {
    ElMessage.warning('请输入要解密的密文')
    return
  }
  if (!decryptForm.privateKey.trim()) {
    ElMessage.warning('请输入私钥')
    return
  }
  if (props.showDecryptPublicKey && !decryptForm.publicKey.trim()) {
    ElMessage.warning('请输入公钥')
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
.public-key-crypto-panel {
  width: 100%;
}
</style>
