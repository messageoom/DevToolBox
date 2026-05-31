/**
 * Shared tool categories data used by both Home.vue and MobileHome.vue.
 */

export const MOBILE_BREAKPOINT = 768

export const toolCategories = [
  {
    id: 'file',
    name: '文件工具',
    description: '文件上传、管理与处理',
    icon: 'FolderOpened',
    route: '/file-upload',
    tools: ['文件上传', '文件管理', '批量处理']
  },
  {
    id: 'crypto',
    name: '加密工具',
    description: '哈希算法、对称与非对称加密',
    icon: 'Key',
    route: '/crypto-tools',
    tools: ['RSA', 'ECC', 'AES', 'ChaCha20', 'SM2', 'SM4', 'MD5', 'SHA256', 'SM3', 'BLAKE3']
  },
  {
    id: 'data',
    name: '数据工具',
    description: '数据格式转换与处理',
    icon: 'DocumentCopy',
    route: '/json-tools',
    tools: ['JSON', 'YAML', 'Markdown', 'Base64']
  },
  {
    id: 'encoding',
    name: '编码工具',
    description: '各种编码解码工具',
    icon: 'Lock',
    route: '/base64-tools',
    tools: ['Base64', 'URL编码', '时间戳']
  },
  {
    id: 'time',
    name: '时间工具',
    description: '时间戳与日期时间处理',
    icon: 'Clock',
    route: '/timestamp-tools',
    tools: ['时间戳转换', '日期计算']
  },
  {
    id: 'other',
    name: '其他工具',
    description: '二维码生成等其他实用工具',
    icon: 'Crop',
    route: '/qr-tools',
    tools: ['二维码生成', '二维码美化']
  }
]
