const STORAGE_KEY = 'dt-recent-tools'
const MAX_RECENT = 6

export function getRecentTools() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    return []
  }
}

export function addRecentTool(tool) {
  const list = getRecentTools().filter(t => t.route !== tool.route)
  list.unshift({ route: tool.route, label: tool.label, icon: tool.icon, color: tool.color })
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list.slice(0, MAX_RECENT)))
}
