<template>
  <div class="crypto-sub-menu">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><Key /></el-icon>
          <span>加密工具</span>
        </div>
      </template>

      <div class="sub-menu-content">
        <el-alert
          title="请选择加密功能类型"
          type="info"
          description="加密工具包含多种加密算法和哈希算法，请选择您需要的功能类型"
          show-icon
          style="margin-bottom: 30px;"
        />

        <el-row :gutter="30">
          <el-col :span="12">
            <el-card class="sub-menu-card" @click="goTo('/crypto-tools')">
              <div class="card-content">
                <el-icon class="menu-icon" :size="48"><Lock /></el-icon>
                <h3 class="menu-title">加密解密</h3>
                <p class="menu-description">支持RSA、ECC、AES、ChaCha20、SM2、SM4等对称和非对称加密算法</p>
                <div class="menu-tags">
                  <el-tag type="success" size="small">RSA</el-tag>
                  <el-tag type="success" size="small">ECC</el-tag>
                  <el-tag type="success" size="small">AES</el-tag>
                  <el-tag type="success" size="small">SM2</el-tag>
                  <el-tag type="success" size="small">SM4</el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card class="sub-menu-card" @click="goTo('/hash-tools')">
              <div class="card-content">
                <el-icon class="menu-icon" :size="48"><Document /></el-icon>
                <h3 class="menu-title">哈希算法</h3>
                <p class="menu-description">支持MD5、SHA系列、BLAKE系列、SM3等哈希算法</p>
                <div class="menu-tags">
                  <el-tag type="primary" size="small">SHA256</el-tag>
                  <el-tag type="primary" size="small">SHA3</el-tag>
                  <el-tag type="primary" size="small">BLAKE2</el-tag>
                  <el-tag type="primary" size="small">SM3</el-tag>
                  <el-tag type="primary" size="small">MD5</el-tag>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script>
import { Key, Lock, Document } from '@element-plus/icons-vue'

export default {
  name: 'CryptoSubMenu',
  components: {
    Key,
    Lock,
    Document
  },
  methods: {
    goTo(path) {
      this.$router.push(path)
    }
  }
}
</script>

<style scoped>
.crypto-sub-menu {
  padding: 20px;
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

.sub-menu-content {
  padding: 20px 0;
}

.sub-menu-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 100%;
}

.sub-menu-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 30px 20px;
}

.menu-icon {
  color: #409eff;
  margin-bottom: 20px;
}

.menu-title {
  margin: 0 0 15px 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.menu-description {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.menu-tags {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
}
</style>