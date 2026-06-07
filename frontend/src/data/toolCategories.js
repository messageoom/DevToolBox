/**
 * Shared tool categories data used by both Home.vue and MobileHome.vue.
 * icon: Material Symbols Rounded icon name (used via <span class="material-symbols-rounded">)
 */

export const toolCategories = [
  {
    id: 'file',
    icon: 'upload_file',
    route: '/file-upload',
    color: '#3b82f6',
    tools: ['fileUpload', 'fileManage', 'batchProcess']
  },
  {
    id: 'transfer',
    icon: 'chat',
    route: '/text-transfer',
    color: '#10b981',
    tools: ['textTransfer']
  },
  {
    id: 'data',
    icon: 'data_object',
    route: '/json-tools',
    color: '#8b5cf6',
    tools: ['JSON', 'YAML', 'Markdown', 'Base64']
  },
  {
    id: 'encoding',
    icon: 'encode',
    route: '/base64-tools',
    color: '#f59e0b',
    tools: ['base64', 'urlEncode', 'timestamp']
  },
  {
    id: 'crypto',
    icon: 'shield',
    route: '/crypto-tools',
    color: '#ef4444',
    tools: ['RSA', 'ECC', 'AES', 'ChaCha20', 'SM2', 'SM4', 'MD5', 'SHA256', 'SM3', 'BLAKE3']
  },
  {
    id: 'time',
    icon: 'schedule',
    route: '/timestamp-tools',
    color: '#06b6d4',
    tools: ['timestampConvert', 'dateCalc']
  },
  {
    id: 'generator',
    icon: 'auto_awesome',
    route: '/uuid-tools',
    color: '#ec4899',
    tools: ['uuidGen', 'passwordGen', 'apikeyGen', 'jwtDebug', 'textDiff']
  },
  {
    id: 'other',
    icon: 'qr_code_2',
    route: '/qr-tools',
    color: '#64748b',
    tools: ['qrGenerate', 'qrBeautify']
  }
]
