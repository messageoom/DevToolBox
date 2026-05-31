export const FILE_CATEGORIES = [
  {
    key: 'images',
    name: '图片',
    icon: '🖼️',
    extensions: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico']
  },
  {
    key: 'documents',
    name: '文档',
    icon: '📄',
    extensions: ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.odt']
  },
  {
    key: 'data',
    name: '数据',
    icon: '📊',
    extensions: ['.json', '.xml', '.csv', '.yaml', '.yml', '.sql', '.db']
  },
  {
    key: 'archives',
    name: '压缩包',
    icon: '📦',
    extensions: ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']
  },
  {
    key: 'media',
    name: '媒体',
    icon: '🎵',
    extensions: ['.mp3', '.mp4', '.wav', '.avi', '.mov', '.flv', '.wmv', '.mkv']
  },
  {
    key: 'others',
    name: '其他',
    icon: '📁',
    extensions: []
  }
]

export function categorizeFile(filename, extension) {
  const ext = extension || '.' + filename.split('.').pop().toLowerCase()
  for (const cat of FILE_CATEGORIES) {
    if (cat.extensions.includes(ext)) return cat.key
  }
  return 'others'
}
