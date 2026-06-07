/**
 * Shared tool categories data used by both Home.vue and MobileHome.vue.
 */

export const toolCategories = [
  {
    id: 'file',
    icon: 'FolderOpened',
    route: '/file-upload',
    tools: ['fileUpload', 'fileManage', 'batchProcess']
  },
  {
    id: 'crypto',
    icon: 'Key',
    route: '/crypto-tools',
    tools: ['RSA', 'ECC', 'AES', 'ChaCha20', 'SM2', 'SM4', 'MD5', 'SHA256', 'SM3', 'BLAKE3']
  },
  {
    id: 'data',
    icon: 'DocumentCopy',
    route: '/json-tools',
    tools: ['JSON', 'YAML', 'Markdown', 'Base64']
  },
  {
    id: 'encoding',
    icon: 'Lock',
    route: '/base64-tools',
    tools: ['base64', 'urlEncode', 'timestamp']
  },
  {
    id: 'time',
    icon: 'Clock',
    route: '/timestamp-tools',
    tools: ['timestampConvert', 'dateCalc']
  },
  {
    id: 'other',
    icon: 'Crop',
    route: '/qr-tools',
    tools: ['qrGenerate', 'qrBeautify']
  },
  {
    id: 'generator',
    icon: 'MagicStick',
    route: '/uuid-tools',
    tools: ['uuidGen', 'passwordGen', 'apikeyGen', 'jwtDebug', 'textDiff']
  },
  {
    id: 'transfer',
    icon: 'ChatDotRound',
    route: '/text-transfer',
    tools: ['textTransfer']
  }
]
