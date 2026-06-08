<template>
  <div class="crypto-tools">
    <ToolPage :title="t('tools.crypto.title')" :icon="Key">
      <div class="tool-section">
        <el-alert
          :title="t('tools.crypto.supportedAlgorithms')"
          type="info"
          :description="t('tools.crypto.algorithmDesc')"
          show-icon
          closable
          style="margin-bottom: 20px;"
        />

        <!-- 顶部切换: 加密解密 / 哈希 -->
        <div class="top-tabs">
          <el-tabs v-model="activeMenu">
            <el-tab-pane :label="t('tools.crypto.tab.crypto')" name="encryption" />
            <el-tab-pane :label="t('tools.crypto.tab.hash')" name="hash" />
          </el-tabs>
        </div>

        <!-- ============ 加密解密工具 ============ -->
        <div v-if="activeMenu === 'encryption'">
          <AlgorithmCardSelector
            v-model="selectedAlgorithm"
            v-model:category="selectedCategory"
            :algorithms="availableAlgorithms"
            @category-change="onCategoryChange"
            class="algorithm-selector"
          />

          <!-- RSA -->
          <div v-if="selectedAlgorithm === 'RSA'" class="algorithm-section">
            <el-tabs v-model="rsaActiveTab">
              <el-tab-pane :label="t('tools.crypto.rsa.generateKeyPair')" name="generate">
                <el-form :model="rsaGenerateForm" label-width="120px">
                  <el-form-item :label="t('tools.crypto.rsa.keyLength')">
                    <el-select v-model="rsaGenerateForm.keySize">
                      <el-option :label="t('tools.crypto.rsa.bits2048')" :value="2048" />
                      <el-option :label="t('tools.crypto.rsa.bits3072')" :value="3072" />
                      <el-option :label="t('tools.crypto.rsa.bits4096')" :value="4096" />
                    </el-select>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="generateRSAKeyPair" :loading="generating">
                      {{ t('tools.crypto.rsa.generateKeyPair') }}
                    </el-button>
                  </el-form-item>
                </el-form>
                <KeyPairDisplay
                  :private-key="rsaKeys.privateKey"
                  :public-key="rsaKeys.publicKey"
                />
              </el-tab-pane>

              <el-tab-pane :label="t('tools.crypto.rsa.encryptDecrypt')" name="encryptDecrypt">
                <PublicKeyCryptoPanel
                  algorithm="RSA"
                  :encrypting="encrypting"
                  :decrypting="decrypting"
                  :encrypt-result="rsaEncryptResult"
                  :decrypt-result="rsaDecryptResult"
                  @encrypt="rsaEncrypt"
                  @decrypt="rsaDecrypt"
                />
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- ECC -->
          <div v-else-if="selectedAlgorithm === 'ECC'" class="algorithm-section">
            <el-tabs v-model="eccActiveTab">
              <el-tab-pane :label="t('tools.crypto.rsa.generateKeyPair')" name="generate">
                <el-form :model="eccGenerateForm" label-width="120px">
                  <el-form-item :label="t('tools.crypto.ecc.curve')">
                    <el-select v-model="eccGenerateForm.curve">
                      <el-option label="secp256r1" value="secp256r1" />
                      <el-option label="secp384r1" value="secp384r1" />
                      <el-option label="secp521r1" value="secp521r1" />
                    </el-select>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="generateECCKeyPair" :loading="generating">
                      {{ t('tools.crypto.rsa.generateKeyPair') }}
                    </el-button>
                  </el-form-item>
                </el-form>
                <KeyPairDisplay
                  :private-key="eccKeys.privateKey"
                  :public-key="eccKeys.publicKey"
                />
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- Ed25519 -->
          <div v-else-if="selectedAlgorithm === 'Ed25519'" class="algorithm-section">
            <el-tabs v-model="ed25519ActiveTab">
              <el-tab-pane :label="t('tools.crypto.rsa.generateKeyPair')" name="generate">
                <el-form>
                  <el-form-item>
                    <el-button type="primary" @click="generateEd25519KeyPair" :loading="generating">
                      {{ t('tools.crypto.rsa.generateKeyPair') }}
                    </el-button>
                  </el-form-item>
                </el-form>
                <KeyPairDisplay
                  :private-key="ed25519Keys.privateKey"
                  :public-key="ed25519Keys.publicKey"
                  :rows="4"
                />
              </el-tab-pane>

              <el-tab-pane :label="t('tools.crypto.ed25519.signVerify')" name="signVerify">
                <SignVerifyPanel
                  algorithm="Ed25519"
                  :signing="signing"
                  :verifying="verifying"
                  :sign-result="ed25519SignResult"
                  :verify-result="ed25519VerifyResult"
                  @sign="ed25519Sign"
                  @verify="ed25519Verify"
                />
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- AES -->
          <div v-else-if="selectedAlgorithm === 'AES'" class="algorithm-section">
            <SymmetricCryptoPanel
              algorithm="AES"
              :modes="aesModes"
              :encrypting="encrypting"
              :decrypting="decrypting"
              :encrypt-result="aesEncryptResult"
              :decrypt-result="aesDecryptResult"
              :encrypt-i-v="aesEncryptIV"
              :show-key-generate="true"
              :key-placeholder="t('tools.crypto.aes.keyPlaceholder')"
              :key-rows="3"
              default-mode="CBC"
              :generated-key="aesGeneratedKeyValue"
              @generate-key="generateAESKey"
              @encrypt="aesEncrypt"
              @decrypt="aesDecrypt"
            />
          </div>

          <!-- ChaCha20 -->
          <div v-else-if="selectedAlgorithm === 'ChaCha20'" class="algorithm-section">
            <SymmetricCryptoPanel
              algorithm="ChaCha20"
              :encrypting="encrypting"
              :decrypting="decrypting"
              :encrypt-result="chacha20EncryptResult"
              :decrypt-result="chacha20DecryptResult"
              :encrypt-i-v="chacha20EncryptNonce"
              :show-key-generate="true"
              :key-placeholder="t('tools.crypto.chacha20.keyPlaceholder')"
              :key-rows="3"
              :has-nonce="true"
              :iv-label="t('tools.crypto.chacha20.nonce')"
              :iv-placeholder="t('tools.crypto.chacha20.noncePlaceholder')"
              :generated-key="chacha20GeneratedKeyValue"
              @generate-key="generateChaCha20Key"
              @encrypt="chacha20Encrypt"
              @decrypt="chacha20Decrypt"
            />
          </div>

          <!-- SM2 -->
          <div v-else-if="selectedAlgorithm === 'SM2'" class="algorithm-section">
            <el-tabs v-model="sm2ActiveTab">
              <el-tab-pane :label="t('tools.crypto.rsa.generateKeyPair')" name="generate">
                <el-form>
                  <el-form-item>
                    <el-button type="primary" @click="generateSM2KeyPair" :loading="generating">
                      {{ t('tools.crypto.rsa.generateKeyPair') }}
                    </el-button>
                  </el-form-item>
                </el-form>
                <KeyPairDisplay
                  :private-key="sm2Keys.privateKey"
                  :public-key="sm2Keys.publicKey"
                  :rows="4"
                />
              </el-tab-pane>

              <el-tab-pane :label="t('tools.crypto.sm2.encryptDecrypt')" name="encryptDecrypt">
                <PublicKeyCryptoPanel
                  algorithm="SM2"
                  :encrypting="encrypting"
                  :decrypting="decrypting"
                  :encrypt-result="sm2EncryptResult"
                  :decrypt-result="sm2DecryptResult"
                  :show-decrypt-public-key="true"
                  @encrypt="sm2Encrypt"
                  @decrypt="sm2Decrypt"
                />
              </el-tab-pane>

              <el-tab-pane :label="t('tools.crypto.sm2.signVerify')" name="signVerify">
                <SignVerifyPanel
                  algorithm="SM2"
                  :signing="signing"
                  :verifying="verifying"
                  :sign-result="sm2SignResult"
                  :verify-result="sm2VerifyResult"
                  @sign="sm2Sign"
                  @verify="sm2Verify"
                />
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- SM4 -->
          <div v-else-if="selectedAlgorithm === 'SM4'" class="algorithm-section">
            <SymmetricCryptoPanel
              algorithm="SM4"
              :modes="sm4Modes"
              :encrypting="encrypting"
              :decrypting="decrypting"
              :encrypt-result="sm4EncryptResult"
              :decrypt-result="sm4DecryptResult"
              :encrypt-i-v="sm4EncryptIV"
              :show-key-generate="true"
              :key-placeholder="t('tools.crypto.sm4.keyPlaceholder')"
              :key-rows="2"
              default-mode="ECB"
              :iv-placeholder="t('tools.crypto.sm4.ivPlaceholder')"
              :generated-key="sm4GeneratedKeyValue"
              @generate-key="generateSM4Key"
              @encrypt="sm4Encrypt"
              @decrypt="sm4Decrypt"
            />
          </div>
        </div>

        <!-- ============ 哈希工具 ============ -->
        <div v-else-if="activeMenu === 'hash'" class="hash-tools-section">
          <div class="input-section">
            <h4>{{ t('tools.crypto.hash.inputText') }}</h4>
            <el-input
              v-model="hashInputText"
              type="textarea"
              :rows="6"
              :placeholder="t('tools.crypto.hash.inputPlaceholder')"
              clearable
            />
          </div>

          <HashAlgorithmCardSelector
            v-model="hashAlgorithm"
            :algorithms="availableHashAlgorithms"
            class="hash-algorithm-selector"
          />

          <div class="config-section">
            <el-row :gutter="20">
              <el-col :span="24">
                <div class="action-buttons">
                  <el-button type="primary" @click="handleGenerateHash" :loading="hashGenerating">
                    {{ t('tools.crypto.hash.generateHash') }}
                  </el-button>
                  <el-button @click="handleVerifyHash" :loading="hashVerifying">
                    {{ t('tools.crypto.hash.verifyHash') }}
                  </el-button>
                </div>
              </el-col>
            </el-row>
          </div>

          <div class="output-section">
            <h4>{{ t('tools.crypto.hash.hashResult') }}</h4>
            <el-input
              v-model="hashResult"
              readonly
              :placeholder="t('tools.crypto.hash.resultPlaceholder')"
              type="textarea"
              :rows="4"
            />
            <div class="field-toolbar" style="margin-top: 6px;">
              <el-button link size="small" type="primary" @click="copyText(hashResult)">
                <el-icon><CopyDocument /></el-icon> Copy
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </ToolPage>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDeviceStore } from '@/stores/device.js'
import { ElMessage } from 'element-plus'
import { Key, CopyDocument } from '@element-plus/icons-vue'
import axios from 'axios'

const { t } = useI18n()
const deviceStore = useDeviceStore()

import ToolPage from '@/components/ToolPage.vue'
import AlgorithmCardSelector from '@/components/AlgorithmCardSelector.vue'
import HashAlgorithmCardSelector from '@/components/HashAlgorithmCardSelector.vue'
import KeyPairDisplay from '@/components/crypto/KeyPairDisplay.vue'
import SymmetricCryptoPanel from '@/components/crypto/SymmetricCryptoPanel.vue'
import SignVerifyPanel from '@/components/crypto/SignVerifyPanel.vue'
import PublicKeyCryptoPanel from '@/components/crypto/PublicKeyCryptoPanel.vue'

// ---- Copy helper ----
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success(t('common.copySuccess'))
  } catch {
    const ta = document.createElement('textarea')
    ta.value = text
    ta.style.position = 'fixed'
    ta.style.opacity = '0'
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    ElMessage.success(t('common.copySuccess'))
  }
}

// ---- Top-level navigation ----
const activeMenu = ref('encryption')

// ---- Algorithm selection ----
const selectedCategory = ref('asymmetric')
const selectedAlgorithm = ref('RSA')
const availableAlgorithms = ref({
  asymmetric: ['RSA', 'ECC', 'Ed25519', 'SM2'],
  symmetric: ['AES', 'ChaCha20', 'SM4']
})

function onCategoryChange() {
  const list = availableAlgorithms.value[selectedCategory.value]
  if (list && list.length > 0) {
    selectedAlgorithm.value = list[0]
  }
}

// ---- Shared loading flags ----
const generating = ref(false)
const encrypting = ref(false)
const decrypting = ref(false)
const signing = ref(false)
const verifying = ref(false)

// ---- AES mode options ----
const aesModes = [
  { label: 'CBC', value: 'CBC' },
  { label: 'ECB', value: 'ECB' },
  { label: 'CFB', value: 'CFB' },
  { label: 'OFB', value: 'OFB' }
]

// ---- SM4 mode options ----
const sm4Modes = [
  { label: 'ECB', value: 'ECB' },
  { label: 'CBC', value: 'CBC' }
]

// ==================== RSA ====================
const rsaActiveTab = ref('generate')
const rsaGenerateForm = reactive({ keySize: 2048 })
const rsaKeys = reactive({ privateKey: '', publicKey: '' })
const rsaEncryptResult = ref('')
const rsaDecryptResult = ref('')

async function generateRSAKeyPair() {
  if (!rsaGenerateForm.keySize) {
    ElMessage.warning(t('tools.crypto.rsa.selectKeyLength'))
    return
  }
  generating.value = true
  try {
    const { data } = await axios.post('/api/crypto-tools/rsa/generate', {
      key_size: rsaGenerateForm.keySize
    })
    if (data.success) {
      rsaKeys.privateKey = data.private_key
      rsaKeys.publicKey = data.public_key
      ElMessage.success(t('tools.crypto.rsa.keyPairSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  } catch (error) {
    ElMessage.error(t('tools.crypto.rsa.keyPairFail') + ': ' + (error.response?.data?.error || error.message))
  } finally {
    generating.value = false
  }
}

function rsaEncrypt(form) {
  encrypting.value = true
  axios.post('/api/crypto-tools/rsa/encrypt', {
    plaintext: form.plaintext,
    public_key: form.publicKey
  }).then(({ data }) => {
    if (data.success) {
      rsaEncryptResult.value = data.ciphertext
      ElMessage.success(t('tools.crypto.rsa.encryptSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  }).catch(error => {
    ElMessage.error(t('tools.crypto.rsa.encryptFail') + ': ' + (error.response?.data?.error || error.message))
  }).finally(() => {
    encrypting.value = false
  })
}

function rsaDecrypt(form) {
  decrypting.value = true
  axios.post('/api/crypto-tools/rsa/decrypt', {
    ciphertext: form.ciphertext,
    private_key: form.privateKey
  }).then(({ data }) => {
    if (data.success) {
      rsaDecryptResult.value = data.plaintext
      ElMessage.success(t('tools.crypto.rsa.decryptSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  }).catch(error => {
    ElMessage.error(t('tools.crypto.rsa.decryptFail') + ': ' + (error.response?.data?.error || error.message))
  }).finally(() => {
    decrypting.value = false
  })
}

// ==================== ECC ====================
const eccActiveTab = ref('generate')
const eccGenerateForm = reactive({ curve: 'secp256r1' })
const eccKeys = reactive({ privateKey: '', publicKey: '' })

async function generateECCKeyPair() {
  generating.value = true
  try {
    const { data } = await axios.post('/api/crypto-tools/ecc/generate', {
      curve: eccGenerateForm.curve
    })
    if (data.success) {
      eccKeys.privateKey = data.private_key
      eccKeys.publicKey = data.public_key
      ElMessage.success(t('tools.crypto.ecc.keyPairSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  } catch (error) {
    ElMessage.error(t('tools.crypto.ecc.keyPairFail') + ': ' + (error.response?.data?.error || error.message))
  } finally {
    generating.value = false
  }
}

// ==================== Ed25519 ====================
const ed25519ActiveTab = ref('generate')
const ed25519Keys = reactive({ privateKey: '', publicKey: '' })
const ed25519SignResult = ref('')
const ed25519VerifyResult = ref(null)

async function generateEd25519KeyPair() {
  generating.value = true
  try {
    const { data } = await axios.post('/api/crypto-tools/ed25519/generate')
    if (data.success) {
      ed25519Keys.privateKey = data.private_key
      ed25519Keys.publicKey = data.public_key
      ElMessage.success(t('tools.crypto.rsa.keyPairSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  } catch (error) {
    ElMessage.error(t('tools.crypto.rsa.keyPairFail') + ': ' + (error.response?.data?.error || error.message))
  } finally {
    generating.value = false
  }
}

function ed25519Sign(form) {
  signing.value = true
  axios.post('/api/crypto-tools/ed25519/sign', {
    message: form.message,
    private_key: form.privateKey
  }).then(({ data }) => {
    if (data.success) {
      ed25519SignResult.value = data.signature
      ElMessage.success(t('tools.crypto.ed25519.signSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  }).catch(error => {
    ElMessage.error(t('tools.crypto.ed25519.signFail') + ': ' + (error.response?.data?.error || error.message))
  }).finally(() => {
    signing.value = false
  })
}

function ed25519Verify(form) {
  verifying.value = true
  axios.post('/api/crypto-tools/ed25519/verify', {
    message: form.message,
    signature: form.signature,
    public_key: form.publicKey
  }).then(({ data }) => {
    if (data.success) {
      ed25519VerifyResult.value = data.valid
      ElMessage.success(t('tools.crypto.ed25519.verifyComplete'))
    } else {
      ElMessage.error(data.error)
    }
  }).catch(error => {
    ElMessage.error(t('tools.crypto.ed25519.verifyFail') + ': ' + (error.response?.data?.error || error.message))
  }).finally(() => {
    verifying.value = false
  })
}

// ==================== AES ====================
const aesEncryptResult = ref('')
const aesDecryptResult = ref('')
const aesEncryptIV = ref('')

function generateAESKey() {
  try {
    const keyBytes = new Uint8Array(32)
    window.crypto.getRandomValues(keyBytes)
    // We set the key on the SymmetricCryptoPanel's encrypt form via a trick:
    // SymmetricCryptoPanel manages its own form internally, so we use a ref approach.
    // Since the panel emits generateKey and manages its own encryptForm.key,
    // we need a different approach - use a provide/inject or just emit a value.
    // Simplest: expose a method or use a key ref that the panel watches.
    // For now, we store the generated key and pass it via a prop/event.
    aesGeneratedKeyValue.value = btoa(String.fromCharCode(...keyBytes))
    ElMessage.success(t('tools.crypto.aes.keyGenSuccess'))
  } catch (error) {
    ElMessage.error(t('tools.crypto.aes.keyGenFail') + ': ' + error.message)
  }
}

const aesGeneratedKeyValue = ref('')

function aesEncrypt(form) {
  encrypting.value = true
  axios.post('/api/crypto-tools/aes/encrypt', {
    plaintext: form.plaintext,
    key: form.key,
    mode: form.mode
  }).then(({ data }) => {
    if (data.success) {
      aesEncryptResult.value = data.ciphertext
      aesEncryptIV.value = data.iv || ''
      ElMessage.success(t('tools.crypto.rsa.encryptSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  }).catch(error => {
    ElMessage.error(t('tools.crypto.rsa.encryptFail') + ': ' + (error.response?.data?.error || error.message))
  }).finally(() => {
    encrypting.value = false
  })
}

function aesDecrypt(form) {
  decrypting.value = true
  axios.post('/api/crypto-tools/aes/decrypt', {
    ciphertext: form.ciphertext,
    key: form.key,
    mode: form.mode,
    iv: form.iv
  }).then(({ data }) => {
    if (data.success) {
      aesDecryptResult.value = data.plaintext
      ElMessage.success(t('tools.crypto.rsa.decryptSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  }).catch(error => {
    ElMessage.error(t('tools.crypto.rsa.decryptFail') + ': ' + (error.response?.data?.error || error.message))
  }).finally(() => {
    decrypting.value = false
  })
}

// ==================== ChaCha20 ====================
const chacha20EncryptResult = ref('')
const chacha20DecryptResult = ref('')
const chacha20EncryptNonce = ref('')
const chacha20GeneratedKeyValue = ref('')

function generateChaCha20Key() {
  try {
    const keyBytes = new Uint8Array(32)
    window.crypto.getRandomValues(keyBytes)
    chacha20GeneratedKeyValue.value = btoa(String.fromCharCode(...keyBytes))
    ElMessage.success(t('tools.crypto.aes.keyGenSuccess'))
  } catch (error) {
    ElMessage.error(t('tools.crypto.aes.keyGenFail') + ': ' + error.message)
  }
}

function chacha20Encrypt(form) {
  encrypting.value = true
  axios.post('/api/crypto-tools/chacha20/encrypt', {
    plaintext: form.plaintext,
    key: form.key
  }).then(({ data }) => {
    if (data.success) {
      chacha20EncryptResult.value = data.ciphertext
      chacha20EncryptNonce.value = data.nonce
      ElMessage.success(t('tools.crypto.rsa.encryptSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  }).catch(error => {
    ElMessage.error(t('tools.crypto.rsa.encryptFail') + ': ' + (error.response?.data?.error || error.message))
  }).finally(() => {
    encrypting.value = false
  })
}

function chacha20Decrypt(form) {
  decrypting.value = true
  axios.post('/api/crypto-tools/chacha20/decrypt', {
    ciphertext: form.ciphertext,
    key: form.key,
    nonce: form.nonce
  }).then(({ data }) => {
    if (data.success) {
      chacha20DecryptResult.value = data.plaintext
      ElMessage.success(t('tools.crypto.rsa.decryptSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  }).catch(error => {
    ElMessage.error(t('tools.crypto.rsa.decryptFail') + ': ' + (error.response?.data?.error || error.message))
  }).finally(() => {
    decrypting.value = false
  })
}

// ==================== SM2 ====================
const sm2ActiveTab = ref('generate')
const sm2Keys = reactive({ privateKey: '', publicKey: '' })
const sm2EncryptResult = ref('')
const sm2DecryptResult = ref('')
const sm2SignResult = ref('')
const sm2VerifyResult = ref(null)

async function generateSM2KeyPair() {
  generating.value = true
  try {
    const { data } = await axios.post('/api/crypto-tools/sm2/generate')
    if (data.success) {
      sm2Keys.privateKey = data.private_key
      sm2Keys.publicKey = data.public_key
      ElMessage.success(t('tools.crypto.ecc.keyPairSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  } catch (error) {
    ElMessage.error(t('tools.crypto.ecc.keyPairFail') + ': ' + (error.response?.data?.error || error.message))
  } finally {
    generating.value = false
  }
}

function sm2Encrypt(form) {
  encrypting.value = true
  axios.post('/api/crypto-tools/sm2/encrypt', {
    plaintext: form.plaintext,
    public_key: form.publicKey
  }).then(({ data }) => {
    if (data.success) {
      sm2EncryptResult.value = data.ciphertext
      ElMessage.success(t('tools.crypto.rsa.encryptSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  }).catch(error => {
    ElMessage.error(t('tools.crypto.rsa.encryptFail') + ': ' + (error.response?.data?.error || error.message))
  }).finally(() => {
    encrypting.value = false
  })
}

function sm2Decrypt(form) {
  decrypting.value = true
  axios.post('/api/crypto-tools/sm2/decrypt', {
    ciphertext: form.ciphertext,
    private_key: form.privateKey,
    public_key: form.publicKey
  }).then(({ data }) => {
    if (data.success) {
      sm2DecryptResult.value = data.plaintext
      ElMessage.success(t('tools.crypto.rsa.decryptSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  }).catch(error => {
    ElMessage.error(t('tools.crypto.rsa.decryptFail') + ': ' + (error.response?.data?.error || error.message))
  }).finally(() => {
    decrypting.value = false
  })
}

function sm2Sign(form) {
  signing.value = true
  axios.post('/api/crypto-tools/sm2/sign', {
    message: form.message,
    private_key: form.privateKey
  }).then(({ data }) => {
    if (data.success) {
      sm2SignResult.value = data.signature
      ElMessage.success(t('tools.crypto.ed25519.signSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  }).catch(error => {
    ElMessage.error(t('tools.crypto.ed25519.signFail') + ': ' + (error.response?.data?.error || error.message))
  }).finally(() => {
    signing.value = false
  })
}

function sm2Verify(form) {
  verifying.value = true
  axios.post('/api/crypto-tools/sm2/verify', {
    message: form.message,
    signature: form.signature,
    public_key: form.publicKey
  }).then(({ data }) => {
    if (data.success) {
      sm2VerifyResult.value = data.valid
      ElMessage.success(t('tools.crypto.ed25519.verifyComplete'))
    } else {
      ElMessage.error(data.error)
    }
  }).catch(error => {
    ElMessage.error(t('tools.crypto.ed25519.verifyFail') + ': ' + (error.response?.data?.error || error.message))
  }).finally(() => {
    verifying.value = false
  })
}

// ==================== SM4 ====================
const sm4EncryptResult = ref('')
const sm4DecryptResult = ref('')
const sm4EncryptIV = ref('')
const sm4GeneratedKeyValue = ref('')

function generateSM4Key() {
  try {
    const keyBytes = new Uint8Array(16)
    window.crypto.getRandomValues(keyBytes)
    sm4GeneratedKeyValue.value = Array.from(keyBytes).map(b => b.toString(16).padStart(2, '0')).join('')
    ElMessage.success(t('tools.crypto.aes.keyGenSuccess'))
  } catch (error) {
    ElMessage.error(t('tools.crypto.aes.keyGenFail') + ': ' + error.message)
  }
}

function sm4Encrypt(form) {
  encrypting.value = true
  axios.post('/api/crypto-tools/sm4/encrypt', {
    plaintext: form.plaintext,
    key: form.key,
    mode: form.mode
  }).then(({ data }) => {
    if (data.success) {
      sm4EncryptResult.value = data.ciphertext
      sm4EncryptIV.value = data.iv || ''
      ElMessage.success(t('tools.crypto.rsa.encryptSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  }).catch(error => {
    ElMessage.error(t('tools.crypto.rsa.encryptFail') + ': ' + (error.response?.data?.error || error.message))
  }).finally(() => {
    encrypting.value = false
  })
}

function sm4Decrypt(form) {
  decrypting.value = true
  axios.post('/api/crypto-tools/sm4/decrypt', {
    ciphertext: form.ciphertext,
    key: form.key,
    mode: form.mode,
    iv: form.iv
  }).then(({ data }) => {
    if (data.success) {
      sm4DecryptResult.value = data.plaintext
      ElMessage.success(t('tools.crypto.rsa.decryptSuccess'))
    } else {
      ElMessage.error(data.error)
    }
  }).catch(error => {
    ElMessage.error(t('tools.crypto.rsa.decryptFail') + ': ' + (error.response?.data?.error || error.message))
  }).finally(() => {
    decrypting.value = false
  })
}

// ==================== Hash ====================
const hashInputText = ref('')
const hashAlgorithm = ref('sha256')
const hashResult = ref('')
const hashGenerating = ref(false)
const hashVerifying = ref(false)
const availableHashAlgorithms = ref([])

async function handleGenerateHash() {
  if (!hashInputText.value.trim()) {
    ElMessage.warning(t('tools.crypto.hash.inputVerifyRequired'))
    return
  }
  hashGenerating.value = true
  try {
    const { data } = await axios.post('/api/hash-tools/generate', {
      text: hashInputText.value,
      algorithm: hashAlgorithm.value
    })
    if (data.success) {
      hashResult.value = data.hash
      ElMessage.success(t('tools.crypto.hash.hashSuccess'))
    } else {
      ElMessage.error(data.error || t('tools.crypto.hash.hashFail'))
    }
  } catch (error) {
    ElMessage.error(t('tools.crypto.hash.hashFail') + ': ' + (error.response?.data?.error || error.message))
  } finally {
    hashGenerating.value = false
  }
}

async function handleVerifyHash() {
  if (!hashInputText.value.trim()) {
    ElMessage.warning(t('tools.crypto.hash.inputVerifyRequired'))
    return
  }
  if (!hashResult.value.trim()) {
    ElMessage.warning(t('tools.crypto.hash.generateOrInputHash'))
    return
  }
  hashVerifying.value = true
  try {
    const { data } = await axios.post('/api/hash-tools/verify', {
      text: hashInputText.value,
      expected_hash: hashResult.value,
      algorithm: hashAlgorithm.value
    })
    if (data.success) {
      if (data.valid) {
        ElMessage.success(t('tools.crypto.hash.verifyPass'))
      } else {
        ElMessage.error(t('tools.crypto.hash.verifyFail'))
      }
    } else {
      ElMessage.error(data.error || t('tools.crypto.hash.verifyFail'))
    }
  } catch (error) {
    ElMessage.error(t('tools.crypto.hash.verifyFail') + ': ' + (error.response?.data?.error || error.message))
  } finally {
    hashVerifying.value = false
  }
}

// ==================== Init ====================
onMounted(async () => {
  try {
    const { data } = await axios.get('/api/crypto-tools/algorithms')
    if (data.success) {
      availableAlgorithms.value = data.algorithms
      if (availableAlgorithms.value.asymmetric?.length > 0) {
        selectedAlgorithm.value = availableAlgorithms.value.asymmetric[0]
      } else if (availableAlgorithms.value.symmetric?.length > 0) {
        selectedAlgorithm.value = availableAlgorithms.value.symmetric[0]
      }
    }
  } catch (error) {
    console.error('获取算法列表失败:', error)
    ElMessage.error(t('tools.crypto.hash.getAlgorithmsFail') + ': ' + (error.response?.data?.error || error.message))
  }

  try {
    const { data } = await axios.get('/api/hash-tools/algorithms')
    if (data.success) {
      availableHashAlgorithms.value = data.algorithms
    }
  } catch (error) {
    console.error('获取哈希算法列表失败:', error)
  }
})
</script>

<style scoped>
.crypto-tools {
  padding: 20px;
}

.algorithm-selector {
  margin-bottom: 20px;
}

.hash-tools-section {
  margin-top: 10px;
}

.hash-tools-section h4 {
  margin-bottom: 10px;
  color: var(--dt-text-primary, #333);
  font-weight: bold;
}

.input-section {
  margin-bottom: 20px;
}

.hash-algorithm-selector {
  margin-bottom: 20px;
}

.config-section {
  margin-bottom: 20px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.output-section {
  margin-top: 20px;
}

.top-tabs {
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .crypto-tools { padding: 0 !important; }
  .algorithm-selector :deep(.algorithm-grid) {
    grid-template-columns: 1fr !important;
  }
  .el-tabs :deep(.el-tabs__content) { padding: 8px; }
}
</style>
