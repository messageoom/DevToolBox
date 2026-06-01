export const FILE_CATEGORIES = [
  {
    key: 'images',
    icon: '🖼️',
    extensions: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico']
  },
  {
    key: 'documents',
    icon: '📄',
    extensions: ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.rtf', '.odt']
  },
  {
    key: 'data',
    icon: '📊',
    extensions: ['.json', '.xml', '.csv', '.yaml', '.yml', '.sql', '.db']
  },
  {
    key: 'archives',
    icon: '📦',
    extensions: ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']
  },
  {
    key: 'media',
    icon: '🎵',
    extensions: ['.mp3', '.mp4', '.wav', '.avi', '.mov', '.flv', '.wmv', '.mkv']
  },
  {
    key: 'others',
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
