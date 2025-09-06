<template>
  <div class="crypto-tools">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><Key /></el-icon>
          <span>加密工具</span>
        </div>
      </template>

      <div class="tool-section">
        <!-- 算法分类说明 -->
        <div class="algorithm-info">
          <el-alert
            title="支持的加密算法"
            type="info"
            description="本工具支持多种国际标准和国密算法，包括非对称加密、对称加密"
            show-icon
            closable
            style="margin-bottom: 20px;"
          />
        </div>

        <!-- 加密解密工具 -->
        <div v-if="activeMenu === 'encryption'">
          <!-- 卡片式算法选择器 -->
          <AlgorithmCardSelector 
            v-model="selectedAlgorithm" 
            v-model:category="selectedCategory"
            :algorithms="availableAlgorithms"
            @category-change="onCategoryChange"
            class="algorithm-selector"
          />

          <!-- RSA工具 -->
          <div v-if="selectedAlgorithm === 'RSA'" class="algorithm-section">
            <el-tabs v-model="rsaActiveTab">
              <el-tab-pane label="生成密钥对" name="generate">
                <el-form :model="rsaGenerateForm" label-width="120px">
                  <el-form-item label="密钥长度">
                    <el-select v-model="rsaGenerateForm.keySize">
                      <el-option label="1024位" :value="1024" />
                      <el-option label="2048位" :value="2048" />
                      <el-option label="4096位" :value="4096" />
                    </el-select>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="generateRSAKeyPair" :loading="generating">
                      生成密钥对
                    </el-button>
                  </el-form-item>
                </el-form>
              
                <div v-if="rsaKeys.privateKey || rsaKeys.publicKey" class="key-display">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <h4>私钥</h4>
                      <el-input 
                        v-model="rsaKeys.privateKey" 
                        type="textarea" 
                        :rows="8" 
                        readonly 
                      />
                      <el-button @click="copyToClipboard(rsaKeys.privateKey)" size="small" style="margin-top: 10px;">
                        复制私钥
                      </el-button>
                    </el-col>
                    <el-col :span="12">
                      <h4>公钥</h4>
                      <el-input 
                        v-model="rsaKeys.publicKey" 
                        type="textarea" 
                        :rows="8" 
                        readonly 
                      />
                      <el-button @click="copyToClipboard(rsaKeys.publicKey)" size="small" style="margin-top: 10px;">
                        复制公钥
                      </el-button>
                    </el-col>
                  </el-row>
                </div>
              </el-tab-pane>
            
              <el-tab-pane label="加密/解密" name="encryptDecrypt">
                <el-tabs v-model="rsaCryptoTab">
                  <el-tab-pane label="加密" name="encrypt">
                    <el-form :model="rsaEncryptForm" label-width="120px">
                      <el-form-item label="明文">
                        <el-input 
                          v-model="rsaEncryptForm.plaintext" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入要加密的文本..."
                        />
                      </el-form-item>
                      <el-form-item label="公钥">
                        <el-input 
                          v-model="rsaEncryptForm.publicKey" 
                          type="textarea" 
                          :rows="6" 
                          placeholder="请输入公钥..."
                        />
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="rsaEncrypt" :loading="encrypting">
                          RSA加密
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="rsaEncryptResult" label="密文">
                        <el-input 
                          v-model="rsaEncryptResult" 
                          type="textarea" 
                          :rows="4" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(rsaEncryptResult)" size="small" style="margin-top: 10px;">
                          复制密文
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                
                  <el-tab-pane label="解密" name="decrypt">
                    <el-form :model="rsaDecryptForm" label-width="120px">
                      <el-form-item label="密文">
                        <el-input 
                          v-model="rsaDecryptForm.ciphertext" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入要解密的密文..."
                        />
                      </el-form-item>
                      <el-form-item label="私钥">
                        <el-input 
                          v-model="rsaDecryptForm.privateKey" 
                          type="textarea" 
                          :rows="6" 
                          placeholder="请输入私钥..."
                        />
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="rsaDecrypt" :loading="decrypting">
                          RSA解密
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="rsaDecryptResult" label="明文">
                        <el-input 
                          v-model="rsaDecryptResult" 
                          type="textarea" 
                          :rows="4" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(rsaDecryptResult)" size="small" style="margin-top: 10px;">
                          复制明文
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                </el-tabs>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- ECC工具 -->
          <div v-else-if="selectedAlgorithm === 'ECC'" class="algorithm-section">
            <el-tabs v-model="eccActiveTab">
              <el-tab-pane label="生成密钥对" name="generate">
                <el-form :model="eccGenerateForm" label-width="120px">
                  <el-form-item label="椭圆曲线">
                    <el-select v-model="eccGenerateForm.curve">
                      <el-option label="secp256r1" value="secp256r1" />
                      <el-option label="secp384r1" value="secp384r1" />
                      <el-option label="secp521r1" value="secp521r1" />
                    </el-select>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="generateECCKeyPair" :loading="generating">
                      生成密钥对
                    </el-button>
                  </el-form-item>
                </el-form>
              
                <div v-if="eccKeys.privateKey || eccKeys.publicKey" class="key-display">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <h4>私钥</h4>
                      <el-input 
                        v-model="eccKeys.privateKey" 
                        type="textarea" 
                        :rows="8" 
                        readonly 
                      />
                      <el-button @click="copyToClipboard(eccKeys.privateKey)" size="small" style="margin-top: 10px;">
                        复制私钥
                      </el-button>
                    </el-col>
                    <el-col :span="12">
                      <h4>公钥</h4>
                      <el-input 
                        v-model="eccKeys.publicKey" 
                        type="textarea" 
                        :rows="8" 
                        readonly 
                      />
                      <el-button @click="copyToClipboard(eccKeys.publicKey)" size="small" style="margin-top: 10px;">
                        复制公钥
                      </el-button>
                    </el-col>
                  </el-row>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- Ed25519工具 -->
          <div v-else-if="selectedAlgorithm === 'Ed25519'" class="algorithm-section">
            <el-tabs v-model="ed25519ActiveTab">
              <el-tab-pane label="生成密钥对" name="generate">
                <el-form>
                  <el-form-item>
                    <el-button type="primary" @click="generateEd25519KeyPair" :loading="generating">
                      生成密钥对
                    </el-button>
                  </el-form-item>
                </el-form>
              
                <div v-if="ed25519Keys.privateKey || ed25519Keys.publicKey" class="key-display">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <h4>私钥</h4>
                      <el-input 
                        v-model="ed25519Keys.privateKey" 
                        type="textarea" 
                        :rows="4" 
                        readonly 
                      />
                      <el-button @click="copyToClipboard(ed25519Keys.privateKey)" size="small" style="margin-top: 10px;">
                        复制私钥
                      </el-button>
                    </el-col>
                    <el-col :span="12">
                      <h4>公钥</h4>
                      <el-input 
                        v-model="ed25519Keys.publicKey" 
                        type="textarea" 
                        :rows="4" 
                        readonly 
                      />
                      <el-button @click="copyToClipboard(ed25519Keys.publicKey)" size="small" style="margin-top: 10px;">
                        复制公钥
                      </el-button>
                    </el-col>
                  </el-row>
                </div>
              </el-tab-pane>
            
              <el-tab-pane label="签名/验证" name="signVerify">
                <el-tabs v-model="ed25519SignTab">
                  <el-tab-pane label="签名" name="sign">
                    <el-form :model="ed25519SignForm" label-width="120px">
                      <el-form-item label="消息">
                        <el-input 
                          v-model="ed25519SignForm.message" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入要签名的消息..."
                        />
                      </el-form-item>
                      <el-form-item label="私钥">
                        <el-input 
                          v-model="ed25519SignForm.privateKey" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入私钥..."
                        />
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="ed25519Sign" :loading="signing">
                          Ed25519签名
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="ed25519SignResult" label="签名">
                        <el-input 
                          v-model="ed25519SignResult" 
                          type="textarea" 
                          :rows="4" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(ed25519SignResult)" size="small" style="margin-top: 10px;">
                          复制签名
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                
                  <el-tab-pane label="验证" name="verify">
                    <el-form :model="ed25519VerifyForm" label-width="120px">
                      <el-form-item label="消息">
                        <el-input 
                          v-model="ed25519VerifyForm.message" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入要验证的消息..."
                        />
                      </el-form-item>
                      <el-form-item label="签名">
                        <el-input 
                          v-model="ed25519VerifyForm.signature" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入签名..."
                        />
                      </el-form-item>
                      <el-form-item label="公钥">
                        <el-input 
                          v-model="ed25519VerifyForm.publicKey" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入公钥..."
                        />
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="ed25519Verify" :loading="verifying">
                          Ed25519验证
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="ed25519VerifyResult !== null" label="验证结果">
                        <el-tag :type="ed25519VerifyResult ? 'success' : 'danger'">
                          {{ ed25519VerifyResult ? '签名有效' : '签名无效' }}
                        </el-tag>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                </el-tabs>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- AES工具 -->
          <div v-else-if="selectedAlgorithm === 'AES'" class="algorithm-section">
            <el-tabs v-model="aesActiveTab">
              <el-tab-pane label="加密/解密" name="encryptDecrypt">
                <el-tabs v-model="aesCryptoTab">
                  <el-tab-pane label="加密" name="encrypt">
                    <el-form :model="aesEncryptForm" label-width="120px">
                      <el-form-item label="明文">
                        <el-input 
                          v-model="aesEncryptForm.plaintext" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入要加密的文本..."
                        />
                      </el-form-item>
                      <el-form-item label="密钥">
                        <el-input 
                          v-model="aesEncryptForm.key" 
                          type="textarea" 
                          :rows="3" 
                          placeholder="请输入Base64编码的密钥..."
                        />
                        <div style="margin-top: 5px;">
                          <el-button @click="generateAESKey" size="small">生成密钥</el-button>
                        </div>
                      </el-form-item>
                      <el-form-item label="模式">
                        <el-select v-model="aesEncryptForm.mode">
                          <el-option label="CBC" value="CBC" />
                          <el-option label="ECB" value="ECB" />
                          <el-option label="CFB" value="CFB" />
                          <el-option label="OFB" value="OFB" />
                        </el-select>
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="aesEncrypt" :loading="encrypting">
                          AES加密
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="aesEncryptResult" label="密文">
                        <el-input 
                          v-model="aesEncryptResult" 
                          type="textarea" 
                          :rows="4" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(aesEncryptResult)" size="small" style="margin-top: 10px;">
                          复制密文
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="aesEncryptIV" label="IV">
                        <el-input 
                          v-model="aesEncryptIV" 
                          type="textarea" 
                          :rows="2" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(aesEncryptIV)" size="small" style="margin-top: 10px;">
                          复制IV
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                
                  <el-tab-pane label="解密" name="decrypt">
                    <el-form :model="aesDecryptForm" label-width="120px">
                      <el-form-item label="密文">
                        <el-input 
                          v-model="aesDecryptForm.ciphertext" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入要解密的密文..."
                        />
                      </el-form-item>
                      <el-form-item label="密钥">
                        <el-input 
                          v-model="aesDecryptForm.key" 
                          type="textarea" 
                          :rows="3" 
                          placeholder="请输入Base64编码的密钥..."
                        />
                      </el-form-item>
                      <el-form-item label="模式">
                        <el-select v-model="aesDecryptForm.mode">
                          <el-option label="CBC" value="CBC" />
                          <el-option label="ECB" value="ECB" />
                          <el-option label="CFB" value="CFB" />
                          <el-option label="OFB" value="OFB" />
                        </el-select>
                      </el-form-item>
                      <el-form-item label="IV" v-if="aesDecryptForm.mode !== 'ECB'">
                        <el-input 
                          v-model="aesDecryptForm.iv" 
                          type="textarea" 
                          :rows="2" 
                          placeholder="请输入Base64编码的IV..."
                        />
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="aesDecrypt" :loading="decrypting">
                          AES解密
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="aesDecryptResult" label="明文">
                        <el-input 
                          v-model="aesDecryptResult" 
                          type="textarea" 
                          :rows="4" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(aesDecryptResult)" size="small" style="margin-top: 10px;">
                          复制明文
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                </el-tabs>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- ChaCha20工具 -->
          <div v-else-if="selectedAlgorithm === 'ChaCha20'" class="algorithm-section">
            <el-tabs v-model="chacha20ActiveTab">
              <el-tab-pane label="加密/解密" name="encryptDecrypt">
                <el-tabs v-model="chacha20CryptoTab">
                  <el-tab-pane label="加密" name="encrypt">
                    <el-form :model="chacha20EncryptForm" label-width="120px">
                      <el-form-item label="明文">
                        <el-input 
                          v-model="chacha20EncryptForm.plaintext" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入要加密的文本..."
                        />
                      </el-form-item>
                      <el-form-item label="密钥">
                        <el-input 
                          v-model="chacha20EncryptForm.key" 
                          type="textarea" 
                          :rows="3" 
                          placeholder="请输入Base64编码的32字节密钥..."
                        />
                        <div style="margin-top: 5px;">
                          <el-button @click="generateChaCha20Key" size="small">生成密钥</el-button>
                        </div>
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="chacha20Encrypt" :loading="encrypting">
                          ChaCha20加密
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="chacha20EncryptResult" label="密文">
                        <el-input 
                          v-model="chacha20EncryptResult" 
                          type="textarea" 
                          :rows="4" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(chacha20EncryptResult)" size="small" style="margin-top: 10px;">
                          复制密文
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="chacha20EncryptNonce" label="Nonce">
                        <el-input 
                          v-model="chacha20EncryptNonce" 
                          type="textarea" 
                          :rows="2" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(chacha20EncryptNonce)" size="small" style="margin-top: 10px;">
                          复制Nonce
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                
                  <el-tab-pane label="解密" name="decrypt">
                    <el-form :model="chacha20DecryptForm" label-width="120px">
                      <el-form-item label="密文">
                        <el-input 
                          v-model="chacha20DecryptForm.ciphertext" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入要解密的密文..."
                        />
                      </el-form-item>
                      <el-form-item label="密钥">
                        <el-input 
                          v-model="chacha20DecryptForm.key" 
                          type="textarea" 
                          :rows="3" 
                          placeholder="请输入Base64编码的32字节密钥..."
                        />
                      </el-form-item>
                      <el-form-item label="Nonce">
                        <el-input 
                          v-model="chacha20DecryptForm.nonce" 
                          type="textarea" 
                          :rows="2" 
                          placeholder="请输入Base64编码的16字节Nonce..."
                        />
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="chacha20Decrypt" :loading="decrypting">
                          ChaCha20解密
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="chacha20DecryptResult" label="明文">
                        <el-input 
                          v-model="chacha20DecryptResult" 
                          type="textarea" 
                          :rows="4" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(chacha20DecryptResult)" size="small" style="margin-top: 10px;">
                          复制明文
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                </el-tabs>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- SM2工具 -->
          <div v-else-if="selectedAlgorithm === 'SM2'" class="algorithm-section">
            <el-tabs v-model="sm2ActiveTab">
              <el-tab-pane label="生成密钥对" name="generate">
                <el-form>
                  <el-form-item>
                    <el-button type="primary" @click="generateSM2KeyPair" :loading="generating">
                      生成密钥对
                    </el-button>
                  </el-form-item>
                </el-form>
              
                <div v-if="sm2Keys.privateKey || sm2Keys.publicKey" class="key-display">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <h4>私钥</h4>
                      <el-input 
                        v-model="sm2Keys.privateKey" 
                        type="textarea" 
                        :rows="4" 
                        readonly 
                      />
                      <el-button @click="copyToClipboard(sm2Keys.privateKey)" size="small" style="margin-top: 10px;">
                        复制私钥
                      </el-button>
                    </el-col>
                    <el-col :span="12">
                      <h4>公钥</h4>
                      <el-input 
                        v-model="sm2Keys.publicKey" 
                        type="textarea" 
                        :rows="4" 
                        readonly 
                      />
                      <el-button @click="copyToClipboard(sm2Keys.publicKey)" size="small" style="margin-top: 10px;">
                        复制公钥
                      </el-button>
                    </el-col>
                  </el-row>
                </div>
              </el-tab-pane>
            
              <el-tab-pane label="加密/解密" name="encryptDecrypt">
                <el-tabs v-model="sm2CryptoTab">
                  <el-tab-pane label="加密" name="encrypt">
                    <el-form :model="sm2EncryptForm" label-width="120px">
                      <el-form-item label="明文">
                        <el-input 
                          v-model="sm2EncryptForm.plaintext" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入要加密的文本..."
                        />
                      </el-form-item>
                      <el-form-item label="公钥">
                        <el-input 
                          v-model="sm2EncryptForm.publicKey" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入公钥..."
                        />
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="sm2Encrypt" :loading="encrypting">
                          SM2加密
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="sm2EncryptResult" label="密文">
                        <el-input 
                          v-model="sm2EncryptResult" 
                          type="textarea" 
                          :rows="4" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(sm2EncryptResult)" size="small" style="margin-top: 10px;">
                          复制密文
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                
                  <el-tab-pane label="解密" name="decrypt">
                    <el-form :model="sm2DecryptForm" label-width="120px">
                      <el-form-item label="密文">
                        <el-input 
                          v-model="sm2DecryptForm.ciphertext" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入要解密的密文..."
                        />
                      </el-form-item>
                      <el-form-item label="私钥">
                        <el-input 
                          v-model="sm2DecryptForm.privateKey" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入私钥..."
                        />
                      </el-form-item>
                      <el-form-item label="公钥">
                        <el-input 
                          v-model="sm2DecryptForm.publicKey" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入公钥..."
                        />
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="sm2Decrypt" :loading="decrypting">
                          SM2解密
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="sm2DecryptResult" label="明文">
                        <el-input 
                          v-model="sm2DecryptResult" 
                          type="textarea" 
                          :rows="4" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(sm2DecryptResult)" size="small" style="margin-top: 10px;">
                          复制明文
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                </el-tabs>
              </el-tab-pane>
            
              <el-tab-pane label="签名/验证" name="signVerify">
                <el-tabs v-model="sm2SignTab">
                  <el-tab-pane label="签名" name="sign">
                    <el-form :model="sm2SignForm" label-width="120px">
                      <el-form-item label="消息">
                        <el-input 
                          v-model="sm2SignForm.message" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入要签名的消息..."
                        />
                      </el-form-item>
                      <el-form-item label="私钥">
                        <el-input 
                          v-model="sm2SignForm.privateKey" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入私钥..."
                        />
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="sm2Sign" :loading="signing">
                          SM2签名
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="sm2SignResult" label="签名">
                        <el-input 
                          v-model="sm2SignResult" 
                          type="textarea" 
                          :rows="4" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(sm2SignResult)" size="small" style="margin-top: 10px;">
                          复制签名
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                
                  <el-tab-pane label="验证" name="verify">
                    <el-form :model="sm2VerifyForm" label-width="120px">
                      <el-form-item label="消息">
                        <el-input 
                          v-model="sm2VerifyForm.message" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入要验证的消息..."
                        />
                      </el-form-item>
                      <el-form-item label="签名">
                        <el-input 
                          v-model="sm2VerifyForm.signature" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入签名..."
                        />
                      </el-form-item>
                      <el-form-item label="公钥">
                        <el-input 
                          v-model="sm2VerifyForm.publicKey" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入公钥..."
                        />
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="sm2Verify" :loading="verifying">
                          SM2验证
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="sm2VerifyResult !== null" label="验证结果">
                        <el-tag :type="sm2VerifyResult ? 'success' : 'danger'">
                          {{ sm2VerifyResult ? '签名有效' : '签名无效' }}
                        </el-tag>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                </el-tabs>
              </el-tab-pane>
            </el-tabs>
          </div>

          <!-- SM4工具 -->
          <div v-else-if="selectedAlgorithm === 'SM4'" class="algorithm-section">
            <el-tabs v-model="sm4ActiveTab">
              <el-tab-pane label="加密/解密" name="encryptDecrypt">
                <el-tabs v-model="sm4CryptoTab">
                  <el-tab-pane label="加密" name="encrypt">
                    <el-form :model="sm4EncryptForm" label-width="120px">
                      <el-form-item label="明文">
                        <el-input 
                          v-model="sm4EncryptForm.plaintext" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入要加密的文本..."
                        />
                      </el-form-item>
                      <el-form-item label="密钥">
                        <el-input 
                          v-model="sm4EncryptForm.key" 
                          type="textarea" 
                          :rows="2" 
                          placeholder="请输入32字符的十六进制密钥..."
                        />
                        <div style="margin-top: 5px;">
                          <el-button @click="generateSM4Key" size="small">生成密钥</el-button>
                        </div>
                      </el-form-item>
                      <el-form-item label="模式">
                        <el-select v-model="sm4EncryptForm.mode">
                          <el-option label="ECB" value="ECB" />
                          <el-option label="CBC" value="CBC" />
                        </el-select>
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="sm4Encrypt" :loading="encrypting">
                          SM4加密
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="sm4EncryptResult" label="密文">
                        <el-input 
                          v-model="sm4EncryptResult" 
                          type="textarea" 
                          :rows="4" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(sm4EncryptResult)" size="small" style="margin-top: 10px;">
                          复制密文
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="sm4EncryptIV" label="IV">
                        <el-input 
                          v-model="sm4EncryptIV" 
                          type="textarea" 
                          :rows="2" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(sm4EncryptIV)" size="small" style="margin-top: 10px;">
                          复制IV
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                
                  <el-tab-pane label="解密" name="decrypt">
                    <el-form :model="sm4DecryptForm" label-width="120px">
                      <el-form-item label="密文">
                        <el-input 
                          v-model="sm4DecryptForm.ciphertext" 
                          type="textarea" 
                          :rows="4" 
                          placeholder="请输入要解密的密文..."
                        />
                      </el-form-item>
                      <el-form-item label="密钥">
                        <el-input 
                          v-model="sm4DecryptForm.key" 
                          type="textarea" 
                          :rows="2" 
                          placeholder="请输入32字符的十六进制密钥..."
                        />
                      </el-form-item>
                      <el-form-item label="模式">
                        <el-select v-model="sm4DecryptForm.mode">
                          <el-option label="ECB" value="ECB" />
                          <el-option label="CBC" value="CBC" />
                        </el-select>
                      </el-form-item>
                      <el-form-item label="IV" v-if="sm4DecryptForm.mode === 'CBC'">
                        <el-input 
                          v-model="sm4DecryptForm.iv" 
                          type="textarea" 
                          :rows="2" 
                          placeholder="请输入32字符的十六进制IV..."
                        />
                      </el-form-item>
                      <el-form-item>
                        <el-button type="primary" @click="sm4Decrypt" :loading="decrypting">
                          SM4解密
                        </el-button>
                      </el-form-item>
                      <el-form-item v-if="sm4DecryptResult" label="明文">
                        <el-input 
                          v-model="sm4DecryptResult" 
                          type="textarea" 
                          :rows="4" 
                          readonly 
                        />
                        <el-button @click="copyToClipboard(sm4DecryptResult)" size="small" style="margin-top: 10px;">
                          复制明文
                        </el-button>
                      </el-form-item>
                    </el-form>
                  </el-tab-pane>
                </el-tabs>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>

        <!-- 哈希工具 -->
        <div v-else-if="activeMenu === 'hash'" class="hash-tools-section">
          <div class="input-section">
            <h4>输入文本</h4>
            <el-input
              v-model="hashInputText"
              type="textarea"
              :rows="6"
              placeholder="请输入要生成哈希的文本..."
              clearable
            />
          </div>

          <!-- 哈希算法卡片选择器 -->
          <HashAlgorithmCardSelector 
            v-model="hashAlgorithm" 
            :algorithms="availableHashAlgorithms"
            class="hash-algorithm-selector"
          />

          <div class="config-section">
            <el-row :gutter="20">
              <el-col :span="24">
                <div class="action-buttons">
                  <el-button type="primary" @click="generateHash" :loading="hashGenerating">
                    生成哈希
                  </el-button>
                  <el-button @click="verifyHash" :loading="hashVerifying">
                    验证哈希
                  </el-button>
                </div>
              </el-col>
            </el-row>
          </div>

          <div class="output-section">
            <h4>哈希结果</h4>
            <el-input
              v-model="hashResult"
              readonly
              placeholder="哈希结果将显示在这里..."
              type="textarea"
              :rows="4"
            />
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { Key } from '@element-plus/icons-vue'
import axios from 'axios'
import AlgorithmCardSelector from '@/components/AlgorithmCardSelector.vue'

export default {
  name: 'CryptoTools',
  components: {
    Key,
    AlgorithmCardSelector
  },
  data() {
    return {
      activeMenu: 'encryption', // 默认显示加密解密工具
      selectedCategory: 'asymmetric',
      selectedAlgorithm: 'RSA',
      availableAlgorithms: {
        asymmetric: ['RSA', 'ECC', 'Ed25519', 'SM2'],
        symmetric: ['AES', 'ChaCha20', 'SM4']
      },
      hasCryptography: true,
      hasGmssl: true,
      
      // 哈希工具数据
      hashInputText: '',
      hashAlgorithm: 'sha256',
      hashResult: '',
      hashGenerating: false,
      hashVerifying: false,
      availableHashAlgorithms: [],
      
      // RSA相关数据
      rsaActiveTab: 'generate',
      rsaCryptoTab: 'encrypt',
      rsaGenerateForm: {
        keySize: 2048
      },
      rsaEncryptForm: {
        plaintext: '',
        publicKey: ''
      },
      rsaDecryptForm: {
        ciphertext: '',
        privateKey: ''
      },
      rsaKeys: {
        privateKey: '',
        publicKey: ''
      },
      rsaEncryptResult: '',
      rsaDecryptResult: '',
      generating: false,
      encrypting: false,
      decrypting: false,
      
      // ECC相关数据
      eccActiveTab: 'generate',
      eccGenerateForm: {
        curve: 'secp256r1'
      },
      eccKeys: {
        privateKey: '',
        publicKey: ''
      },
      
      // Ed25519相关数据
      ed25519ActiveTab: 'generate',
      ed25519SignTab: 'sign',
      ed25519Keys: {
        privateKey: '',
        publicKey: ''
      },
      ed25519SignForm: {
        message: '',
        privateKey: ''
      },
      ed25519VerifyForm: {
        message: '',
        signature: '',
        publicKey: ''
      },
      ed25519SignResult: '',
      ed25519VerifyResult: null,
      signing: false,
      verifying: false,
      
      // AES相关数据
      aesActiveTab: 'encryptDecrypt',
      aesCryptoTab: 'encrypt',
      aesEncryptForm: {
        plaintext: '',
        key: '',
        mode: 'CBC'
      },
      aesDecryptForm: {
        ciphertext: '',
        key: '',
        mode: 'CBC',
        iv: ''
      },
      aesEncryptResult: '',
      aesDecryptResult: '',
      aesEncryptIV: '',
      
      // ChaCha20相关数据
      chacha20ActiveTab: 'encryptDecrypt',
      chacha20CryptoTab: 'encrypt',
      chacha20EncryptForm: {
        plaintext: '',
        key: ''
      },
      chacha20DecryptForm: {
        ciphertext: '',
        key: '',
        nonce: ''
      },
      chacha20EncryptResult: '',
      chacha20DecryptResult: '',
      chacha20EncryptNonce: '',
      
      // SM2相关数据
      sm2ActiveTab: 'generate',
      sm2CryptoTab: 'encrypt',
      sm2SignTab: 'sign',
      sm2Keys: {
        privateKey: '',
        publicKey: ''
      },
      sm2EncryptForm: {
        plaintext: '',
        publicKey: ''
      },
      sm2DecryptForm: {
        ciphertext: '',
        privateKey: '',
        publicKey: ''
      },
      sm2SignForm: {
        message: '',
        privateKey: ''
      },
      sm2VerifyForm: {
        message: '',
        signature: '',
        publicKey: ''
      },
      sm2EncryptResult: '',
      sm2DecryptResult: '',
      sm2SignResult: '',
      sm2VerifyResult: null,
      
      // SM4相关数据
      sm4ActiveTab: 'encryptDecrypt',
      sm4CryptoTab: 'encrypt',
      sm4EncryptForm: {
        plaintext: '',
        key: '',
        mode: 'ECB'
      },
      sm4DecryptForm: {
        ciphertext: '',
        key: '',
        mode: 'ECB',
        iv: ''
      },
      sm4EncryptResult: '',
      sm4DecryptResult: '',
      sm4EncryptIV: '',
      
      // 哈希相关数据
      activeMenu: 'encryption',
      hashActiveTab: 'sha256',
      sha256Form: {
        input: ''
      },
      sha512Form: {
        input: ''
      },
      sm3Form: {
        input: ''
      },
      sha256Result: '',
      sha512Result: '',
      sm3Result: '',
      hashing: false
    }
  },
  async mounted() {
    // 获取支持的算法列表
    try {
      const response = await axios.get('/api/crypto-tools/algorithms')
      if (response.data.success) {
        this.availableAlgorithms = response.data.algorithms
        this.hasCryptography = response.data.has_cryptography
        this.hasGmssl = response.data.has_gmssl
        
        // 设置默认算法
        if (this.availableAlgorithms.asymmetric && this.availableAlgorithms.asymmetric.length > 0) {
          this.selectedAlgorithm = this.availableAlgorithms.asymmetric[0]
        } else if (this.availableAlgorithms.symmetric && this.availableAlgorithms.symmetric.length > 0) {
          this.selectedAlgorithm = this.availableAlgorithms.symmetric[0]
        }
        console.log('获取到的算法列表:', this.availableAlgorithms)
      }
    } catch (error) {
      console.error('获取算法列表失败:', error)
      ElMessage.error('获取算法列表失败: ' + (error.response?.data?.error || error.message))
    }
    
    // 获取哈希算法列表
    try {
      const response = await axios.get('/api/hash-tools/algorithms')
      if (response.data.success) {
        this.availableHashAlgorithms = response.data.algorithms
      }
    } catch (error) {
      console.error('获取哈希算法列表失败:', error)
    }
  },
  methods: {
    handleMenuSelect(index) {
      this.activeMenu = index;
    },
    
    onCategoryChange() {
      // 当切换类别时，选择该类别下的第一个算法
      if (this.availableAlgorithms[this.selectedCategory].length > 0) {
        this.selectedAlgorithm = this.availableAlgorithms[this.selectedCategory][0]
      }
    },
    
    async generateRSAKeyPair() {
      if (!this.rsaGenerateForm.keySize) {
        ElMessage.warning('请选择密钥长度')
        return
      }
      
      this.generating = true
      try {
        const response = await axios.post('/api/crypto-tools/rsa/generate', {
          key_size: this.rsaGenerateForm.keySize
        })
        
        if (response.data.success) {
          this.rsaKeys.privateKey = response.data.private_key
          this.rsaKeys.publicKey = response.data.public_key
          ElMessage.success('RSA密钥对生成成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('RSA密钥对生成失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.generating = false
      }
    },
    
    async rsaEncrypt() {
      if (!this.rsaEncryptForm.plaintext.trim()) {
        ElMessage.warning('请输入要加密的文本')
        return
      }
      
      if (!this.rsaEncryptForm.publicKey.trim()) {
        ElMessage.warning('请输入公钥')
        return
      }
      
      this.encrypting = true
      try {
        const response = await axios.post('/api/crypto-tools/rsa/encrypt', {
          plaintext: this.rsaEncryptForm.plaintext,
          public_key: this.rsaEncryptForm.publicKey
        })
        
        if (response.data.success) {
          this.rsaEncryptResult = response.data.ciphertext
          ElMessage.success('RSA加密成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('RSA加密失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.encrypting = false
      }
    },
    
    async rsaDecrypt() {
      if (!this.rsaDecryptForm.ciphertext.trim()) {
        ElMessage.warning('请输入要解密的密文')
        return
      }
      
      if (!this.rsaDecryptForm.privateKey.trim()) {
        ElMessage.warning('请输入私钥')
        return
      }
      
      this.decrypting = true
      try {
        const response = await axios.post('/api/crypto-tools/rsa/decrypt', {
          ciphertext: this.rsaDecryptForm.ciphertext,
          private_key: this.rsaDecryptForm.privateKey
        })
        
        if (response.data.success) {
          this.rsaDecryptResult = response.data.plaintext
          ElMessage.success('RSA解密成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('RSA解密失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.decrypting = false
      }
    },
    
    async generateECCKeyPair() {
      this.generating = true
      try {
        const response = await axios.post('/api/crypto-tools/ecc/generate', {
          curve: this.eccGenerateForm.curve
        })
        
        if (response.data.success) {
          this.eccKeys.privateKey = response.data.private_key
          this.eccKeys.publicKey = response.data.public_key
          ElMessage.success('ECC密钥对生成成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('ECC密钥对生成失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.generating = false
      }
    },
    
    async generateEd25519KeyPair() {
      this.generating = true
      try {
        const response = await axios.post('/api/crypto-tools/ed25519/generate')
        
        if (response.data.success) {
          this.ed25519Keys.privateKey = response.data.private_key
          this.ed25519Keys.publicKey = response.data.public_key
          ElMessage.success('Ed25519密钥对生成成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('Ed25519密钥对生成失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.generating = false
      }
    },
    
    async ed25519Sign() {
      if (!this.ed25519SignForm.message.trim()) {
        ElMessage.warning('请输入要签名的消息')
        return
      }
      
      if (!this.ed25519SignForm.privateKey.trim()) {
        ElMessage.warning('请输入私钥')
        return
      }
      
      this.signing = true
      try {
        const response = await axios.post('/api/crypto-tools/ed25519/sign', {
          message: this.ed25519SignForm.message,
          private_key: this.ed25519SignForm.privateKey
        })
        
        if (response.data.success) {
          this.ed25519SignResult = response.data.signature
          ElMessage.success('Ed25519签名成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('Ed25519签名失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.signing = false
      }
    },
    
    async ed25519Verify() {
      if (!this.ed25519VerifyForm.message.trim()) {
        ElMessage.warning('请输入要验证的消息')
        return
      }
      
      if (!this.ed25519VerifyForm.signature.trim()) {
        ElMessage.warning('请输入签名')
        return
      }
      
      if (!this.ed25519VerifyForm.publicKey.trim()) {
        ElMessage.warning('请输入公钥')
        return
      }
      
      this.verifying = true
      try {
        const response = await axios.post('/api/crypto-tools/ed25519/verify', {
          message: this.ed25519VerifyForm.message,
          signature: this.ed25519VerifyForm.signature,
          public_key: this.ed25519VerifyForm.publicKey
        })
        
        if (response.data.success) {
          this.ed25519VerifyResult = response.data.valid
          ElMessage.success('Ed25519验证完成')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('Ed25519验证失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.verifying = false
      }
    },
    
    async generateAESKey() {
      try {
        // 生成随机的256位密钥（32字节）
        const keyBytes = new Uint8Array(32)
        window.crypto.getRandomValues(keyBytes)
        const keyBase64 = btoa(String.fromCharCode(...keyBytes))
        this.aesEncryptForm.key = keyBase64
        ElMessage.success('AES密钥生成成功')
      } catch (error) {
        ElMessage.error('AES密钥生成失败: ' + error.message)
      }
    },
    
    async aesEncrypt() {
      if (!this.aesEncryptForm.plaintext.trim()) {
        ElMessage.warning('请输入要加密的文本')
        return
      }
      
      if (!this.aesEncryptForm.key.trim()) {
        ElMessage.warning('请输入密钥')
        return
      }
      
      this.encrypting = true
      try {
        const response = await axios.post('/api/crypto-tools/aes/encrypt', {
          plaintext: this.aesEncryptForm.plaintext,
          key: this.aesEncryptForm.key,
          mode: this.aesEncryptForm.mode
        })
        
        if (response.data.success) {
          this.aesEncryptResult = response.data.ciphertext
          this.aesEncryptIV = response.data.iv || ''
          ElMessage.success('AES加密成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('AES加密失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.encrypting = false
      }
    },
    
    async aesDecrypt() {
      if (!this.aesDecryptForm.ciphertext.trim()) {
        ElMessage.warning('请输入要解密的密文')
        return
      }
      
      if (!this.aesDecryptForm.key.trim()) {
        ElMessage.warning('请输入密钥')
        return
      }
      
      // 对于需要IV的模式，检查IV是否提供
      if (this.aesDecryptForm.mode !== 'ECB' && !this.aesDecryptForm.iv.trim()) {
        ElMessage.warning('请输入IV')
        return
      }
      
      this.decrypting = true
      try {
        const response = await axios.post('/api/crypto-tools/aes/decrypt', {
          ciphertext: this.aesDecryptForm.ciphertext,
          key: this.aesDecryptForm.key,
          mode: this.aesDecryptForm.mode,
          iv: this.aesDecryptForm.iv
        })
        
        if (response.data.success) {
          this.aesDecryptResult = response.data.plaintext
          ElMessage.success('AES解密成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('AES解密失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.decrypting = false
      }
    },
    
    async generateChaCha20Key() {
      try {
        // 生成随机的256位密钥（32字节）
        const keyBytes = new Uint8Array(32)
        window.crypto.getRandomValues(keyBytes)
        const keyBase64 = btoa(String.fromCharCode(...keyBytes))
        this.chacha20EncryptForm.key = keyBase64
        ElMessage.success('ChaCha20密钥生成成功')
      } catch (error) {
        ElMessage.error('ChaCha20密钥生成失败: ' + error.message)
      }
    },
    
    async chacha20Encrypt() {
      if (!this.chacha20EncryptForm.plaintext.trim()) {
        ElMessage.warning('请输入要加密的文本')
        return
      }
      
      if (!this.chacha20EncryptForm.key.trim()) {
        ElMessage.warning('请输入密钥')
        return
      }
      
      this.encrypting = true
      try {
        const response = await axios.post('/api/crypto-tools/chacha20/encrypt', {
          plaintext: this.chacha20EncryptForm.plaintext,
          key: this.chacha20EncryptForm.key
        })
        
        if (response.data.success) {
          this.chacha20EncryptResult = response.data.ciphertext
          this.chacha20EncryptNonce = response.data.nonce
          ElMessage.success('ChaCha20加密成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('ChaCha20加密失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.encrypting = false
      }
    },
    
    async chacha20Decrypt() {
      if (!this.chacha20DecryptForm.ciphertext.trim()) {
        ElMessage.warning('请输入要解密的密文')
        return
      }
      
      if (!this.chacha20DecryptForm.key.trim()) {
        ElMessage.warning('请输入密钥')
        return
      }
      
      if (!this.chacha20DecryptForm.nonce.trim()) {
        ElMessage.warning('请输入Nonce')
        return
      }
      
      this.decrypting = true
      try {
        const response = await axios.post('/api/crypto-tools/chacha20/decrypt', {
          ciphertext: this.chacha20DecryptForm.ciphertext,
          key: this.chacha20DecryptForm.key,
          nonce: this.chacha20DecryptForm.nonce
        })
        
        if (response.data.success) {
          this.chacha20DecryptResult = response.data.plaintext
          ElMessage.success('ChaCha20解密成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('ChaCha20解密失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.decrypting = false
      }
    },
    
    async generateSM2KeyPair() {
      this.generating = true
      try {
        const response = await axios.post('/api/crypto-tools/sm2/generate')
        
        if (response.data.success) {
          this.sm2Keys.privateKey = response.data.private_key
          this.sm2Keys.publicKey = response.data.public_key
          ElMessage.success('SM2密钥对生成成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('SM2密钥对生成失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.generating = false
      }
    },
    
    async sm2Encrypt() {
      if (!this.sm2EncryptForm.plaintext.trim()) {
        ElMessage.warning('请输入要加密的文本')
        return
      }
      
      if (!this.sm2EncryptForm.publicKey.trim()) {
        ElMessage.warning('请输入公钥')
        return
      }
      
      this.encrypting = true
      try {
        const response = await axios.post('/api/crypto-tools/sm2/encrypt', {
          plaintext: this.sm2EncryptForm.plaintext,
          public_key: this.sm2EncryptForm.publicKey
        })
        
        if (response.data.success) {
          this.sm2EncryptResult = response.data.ciphertext
          ElMessage.success('SM2加密成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('SM2加密失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.encrypting = false
      }
    },
    
    async sm2Decrypt() {
      if (!this.sm2DecryptForm.ciphertext.trim()) {
        ElMessage.warning('请输入要解密的密文')
        return
      }
      
      if (!this.sm2DecryptForm.privateKey.trim()) {
        ElMessage.warning('请输入私钥')
        return
      }
      
      if (!this.sm2DecryptForm.publicKey.trim()) {
        ElMessage.warning('请输入公钥')
        return
      }
      
      this.decrypting = true
      try {
        const response = await axios.post('/api/crypto-tools/sm2/decrypt', {
          ciphertext: this.sm2DecryptForm.ciphertext,
          private_key: this.sm2DecryptForm.privateKey,
          public_key: this.sm2DecryptForm.publicKey
        })
        
        if (response.data.success) {
          this.sm2DecryptResult = response.data.plaintext
          ElMessage.success('SM2解密成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('SM2解密失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.decrypting = false
      }
    },
    
    async sm2Sign() {
      if (!this.sm2SignForm.message.trim()) {
        ElMessage.warning('请输入要签名的消息')
        return
      }
      
      if (!this.sm2SignForm.privateKey.trim()) {
        ElMessage.warning('请输入私钥')
        return
      }
      
      this.signing = true
      try {
        const response = await axios.post('/api/crypto-tools/sm2/sign', {
          message: this.sm2SignForm.message,
          private_key: this.sm2SignForm.privateKey
        })
        
        if (response.data.success) {
          this.sm2SignResult = response.data.signature
          ElMessage.success('SM2签名成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('SM2签名失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.signing = false
      }
    },
    
    async sm2Verify() {
      if (!this.sm2VerifyForm.message.trim()) {
        ElMessage.warning('请输入要验证的消息')
        return
      }
      
      if (!this.sm2VerifyForm.signature.trim()) {
        ElMessage.warning('请输入签名')
        return
      }
      
      if (!this.sm2VerifyForm.publicKey.trim()) {
        ElMessage.warning('请输入公钥')
        return
      }
      
      this.verifying = true
      try {
        const response = await axios.post('/api/crypto-tools/sm2/verify', {
          message: this.sm2VerifyForm.message,
          signature: this.sm2VerifyForm.signature,
          public_key: this.sm2VerifyForm.publicKey
        })
        
        if (response.data.success) {
          this.sm2VerifyResult = response.data.valid
          ElMessage.success('SM2验证完成')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('SM2验证失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.verifying = false
      }
    },
    
    async generateSM4Key() {
      try {
        // 生成随机的128位密钥（16字节），转换为32字符的十六进制字符串
        const keyBytes = new Uint8Array(16)
        window.crypto.getRandomValues(keyBytes)
        const keyHex = Array.from(keyBytes).map(b => b.toString(16).padStart(2, '0')).join('')
        this.sm4EncryptForm.key = keyHex
        ElMessage.success('SM4密钥生成成功')
      } catch (error) {
        ElMessage.error('SM4密钥生成失败: ' + error.message)
      }
    },
    
    async sm4Encrypt() {
      if (!this.sm4EncryptForm.plaintext.trim()) {
        ElMessage.warning('请输入要加密的文本')
        return
      }
      
      if (!this.sm4EncryptForm.key.trim()) {
        ElMessage.warning('请输入密钥')
        return
      }
      
      this.encrypting = true
      try {
        const response = await axios.post('/api/crypto-tools/sm4/encrypt', {
          plaintext: this.sm4EncryptForm.plaintext,
          key: this.sm4EncryptForm.key,
          mode: this.sm4EncryptForm.mode
        })
        
        if (response.data.success) {
          this.sm4EncryptResult = response.data.ciphertext
          this.sm4EncryptIV = response.data.iv || ''
          ElMessage.success('SM4加密成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('SM4加密失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.encrypting = false
      }
    },
    
    async sm4Decrypt() {
      if (!this.sm4DecryptForm.ciphertext.trim()) {
        ElMessage.warning('请输入要解密的密文')
        return
      }
      
      if (!this.sm4DecryptForm.key.trim()) {
        ElMessage.warning('请输入密钥')
        return
      }
      
      // 对于CBC模式，检查IV是否提供
      if (this.sm4DecryptForm.mode === 'CBC' && !this.sm4DecryptForm.iv.trim()) {
        ElMessage.warning('请输入IV')
        return
      }
      
      this.decrypting = true
      try {
        const response = await axios.post('/api/crypto-tools/sm4/decrypt', {
          ciphertext: this.sm4DecryptForm.ciphertext,
          key: this.sm4DecryptForm.key,
          mode: this.sm4DecryptForm.mode,
          iv: this.sm4DecryptForm.iv
        })
        
        if (response.data.success) {
          this.sm4DecryptResult = response.data.plaintext
          ElMessage.success('SM4解密成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('SM4解密失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.decrypting = false
      }
    },
    
    async sha256Hash() {
      if (!this.sha256Form.input.trim()) {
        ElMessage.warning('请输入要哈希的文本')
        return
      }
      
      this.hashing = true
      try {
        const response = await axios.post('/api/crypto-tools/sha256', {
          input: this.sha256Form.input
        })
        
        if (response.data.success) {
          this.sha256Result = response.data.output
          ElMessage.success('SHA-256哈希成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('SHA-256哈希失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.hashing = false
      }
    },
    
    async sha512Hash() {
      if (!this.sha512Form.input.trim()) {
        ElMessage.warning('请输入要哈希的文本')
        return
      }
      
      this.hashing = true
      try {
        const response = await axios.post('/api/crypto-tools/sha512', {
          input: this.sha512Form.input
        })
        
        if (response.data.success) {
          this.sha512Result = response.data.output
          ElMessage.success('SHA-512哈希成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('SHA-512哈希失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.hashing = false
      }
    },
    
    async sm3Hash() {
      if (!this.sm3Form.input.trim()) {
        ElMessage.warning('请输入要哈希的文本')
        return
      }
      
      this.hashing = true
      try {
        const response = await axios.post('/api/crypto-tools/sm3', {
          input: this.sm3Form.input
        })
        
        if (response.data.success) {
          this.sm3Result = response.data.output
          ElMessage.success('SM3哈希成功')
        } else {
          ElMessage.error(response.data.error)
        }
      } catch (error) {
        ElMessage.error('SM3哈希失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.hashing = false
      }
    },
    
    copyToClipboard(text) {
      navigator.clipboard.writeText(text).then(() => {
        ElMessage.success('已复制到剪贴板')
      }).catch(() => {
        ElMessage.error('复制失败')
      })
    }
  }
}
</script>

<style scoped>
.crypto-tools {
  padding: 20px;
}

.algorithm-info {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-icon {
  margin-right: 8px;
  font-size: 18px;
}

.card-header span {
  font-weight: bold;
}

.key-display {
  margin-top: 20px;
}

.key-display h4 {
  margin-bottom: 10px;
  color: #333;
  font-weight: bold;
}

html.dark .key-display h4 {
  color: #e5eaf3;
}

/* 暗黑主题下的表单标签颜色 */
html.dark :deep(.el-form-item__label) {
  color: #e5eaf3;
}

/* 暗黑主题下的输入框背景色 */
html.dark :deep(.el-textarea__inner) {
  background-color: #2d2d2d;
  color: #e5eaf3;
  border-color: #434343;
}

html.dark :deep(.el-input__inner) {
  background-color: #2d2d2d;
  color: #e5eaf3;
  border-color: #434343;
}

/* 暗黑主题下的卡片背景色 */
html.dark :deep(.el-card) {
  background-color: #1d1e1f;
  border-color: #434343;
}

html.dark :deep(.el-card__header) {
  background-color: #2d2d2d;
  border-color: #434343;
}

/* 暗黑主题下的标签页 */
html.dark :deep(.el-tabs__item) {
  color: #a3a6ad;
}

html.dark :deep(.el-tabs__item.is-active) {
  color: #409eff;
}

html.dark :deep(.el-tabs__nav-wrap::after) {
  background-color: #434343;
}

html.dark :deep(.el-tabs__active-bar) {
  background-color: #409eff;
}

/* 暗黑主题下的按钮 */
html.dark :deep(.el-button) {
  background-color: #2d2d2d;
  border-color: #434343;
  color: #e5eaf3;
}

html.dark :deep(.el-button:hover) {
  background-color: #3d3d3d;
  border-color: #535353;
  color: #e5eaf3;
}

/* 暗黑主题下的选择器 */
html.dark :deep(.el-select) {
  background-color: #2d2d2d;
}

html.dark :deep(.el-select .el-input__inner) {
  background-color: #2d2d2d;
}

/* 暗黑主题下的警告框 */
html.dark :deep(.el-alert) {
  background-color: #2d2d2d;
  border-color: #434343;
}

html.dark :deep(.el-alert__title) {
  color: #e5eaf3;
}

html.dark :deep(.el-alert__description) {
  color: #a3a6ad;
}
</style>