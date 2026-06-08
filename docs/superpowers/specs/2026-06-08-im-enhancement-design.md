# IM 通信增强设计文档

## 概述

将当前「文本传输」功能从「纯文本聊天」升级为「完整的开发者 IM 工具」，支持发送文本、代码、图片、文件、链接、密码等。定位为局域网内设备间的即时通讯工具。

## 当前状态 vs 目标

| 能力 | 当前 | 目标 |
|------|------|------|
| 纯文本消息 | ✅ | ✅ |
| 代码块（语法高亮） | ❌ 纯 `<pre>` | ✅ highlight.js 自动语言检测 |
| 图片发送/预览 | ❌ | ✅ 粘贴/拖拽/选择上传，缩略图预览 |
| 文件发送 | ❌ | ✅ 任意文件上传，显示文件名+大小 |
| 链接预览 | ❌ | ✅ URL 自动识别，可点击跳转 |
| Markdown 渲染 | ❌ | ✅ 代码片段/配置自动 markdown 渲染 |
| 消息操作 | 仅复制 | 复制、删除、转发 |
| 加密模式 | WebRTC E2E | 移除（局域网内无必要，简化架构） |
| 群聊 | ✅ | ✅ 保留 |
| 消息持久化 | localStorage 200 条 | 服务端 SQLite + localStorage 缓存 |
| 离线消息 | ❌ | ✅ 设备上线后推送未读消息 |
| 消息搜索 | ❌ | ✅ 按关键词搜索历史消息 |
| 图片灯箱 | ❌ | ✅ 点击放大，左右切换 |
| 拖拽上传 | ❌ | ✅ 拖拽文件/图片到聊天区 |

## 架构

```
浏览器 A ←── SocketIO ──→ Flask-SocketIO (服务端中转) ←── SocketIO ──→ 浏览器 B
                                │
                          Flask REST API
                         /api/im/upload  ← 文件上传
                         /api/im/files/  ← 文件访问
                         /api/im/history ← 历史记录
```

**关键变化：移除 WebRTC，所有通信走服务端中转。** 理由：
1. 局域网内延迟极低，服务端中转无感知差异
2. 移除 WebRTC 后代码量减少 ~40%，维护成本大幅降低
3. 服务端中转才能支持离线消息、文件上传、历史记录
4. SDP/ICE 信令在部分网络环境下不稳定

## 后端设计

### 新增模块：`backend/modules/im.py`

独立的 IM 模块，不依赖 `text_transfer.py`（保留旧模块兼容，后续可删除）。

### 1. 数据库：SQLite（`data/im.db`）

使用 `sqlite3` 标准库，无需额外依赖。

```sql
-- 消息表
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    sender_id TEXT NOT NULL,
    sender_name TEXT NOT NULL,
    target_id TEXT,           -- NULL=群聊, 有值=私聊目标
    content TEXT NOT NULL,    -- 文本内容或 JSON
    msg_type TEXT NOT NULL,   -- text / code / image / file / link
    attachment TEXT,          -- JSON: {filename, url, size, mime, thumbnail}
    timestamp INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_msg_target ON messages(target_id, timestamp);
CREATE INDEX idx_msg_sender ON messages(sender_id, timestamp);
CREATE INDEX idx_msg_time ON messages(timestamp);

-- 设备表（持久化设备信息）
CREATE TABLE devices (
    node_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    last_seen INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 2. 文件上传/存储

```python
# 配置
IM_UPLOAD_DIR = os.path.join(config_manager.get_upload_dir(), 'im')
IM_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
IM_THUMBNAIL_SIZE = (200, 200)

# REST 端点
POST /api/im/upload          # 上传文件（multipart），返回 {id, url, filename, size, mime, thumbnail}
GET  /api/im/files/<path>    # 访问上传的文件
GET  /api/im/thumbs/<path>   # 访问缩略图

# 上传流程：
# 1. 客户端 POST 文件到 /api/im/upload
# 2. 服务端保存文件到 im/ 目录，生成唯一文件名
# 3. 如果是图片，用 Pillow 生成缩略图
# 4. 返回文件元信息（url, thumbnail_url, filename, size, mime）
# 5. 客户端通过 SocketIO 发送消息，attachment 字段携带文件元信息
```

### 3. SocketIO 事件（简化版）

```python
# 连接管理
'join'         → 注册设备，返回在线列表 + 未读消息
'disconnect'   → 设备离线，广播通知
'rename'       → 修改设备名

# 消息
'send-msg'     → 发送消息（文本/代码/图片/文件/链接），服务端存储+转发
# 替代原来的 offer-text, accept-text, reject-text, chat 四个事件

# 状态
'typing'       → 正在输入通知
'read'         → 已读回执

# 设备
'peers'        → 在线列表更新（服务端主动推送）
```

### 4. 消息流转

```
发送消息（统一流程）：

1. 客户端 emit('send-msg', {id, content, msgType, attachment?, targetId?})
2. 服务端收到：
   a. 存入 SQLite
   b. 添加 timestamp, senderName
   c. 如果 targetId 有值 → emit('new-msg', msg, room=target_sid)  （私聊）
      如果 targetId 为空 → emit('new-msg', msg, skip_sid=sender_sid)（群聊）
3. 回复发送方 emit('msg-sent', {id, timestamp}) 确认送达
```

### 5. 历史记录 API

```
GET /api/im/history?peer=<peerId|group>&limit=50&before=<timestamp>
GET /api/im/search?q=<keyword>&limit=20
```

## 前端设计

### 新增依赖

```json
{
  "highlight.js": "^11.9.0"
}
```

### 消息类型与渲染

| msgType | 发送方式 | 渲染方式 |
|---------|---------|---------|
| `text` | 直接输入 | 纯文本，链接自动可点击 |
| `code` | 直接输入（自动检测）或 ``` 包裹 | highlight.js 语法高亮 + 复制按钮 + 语言标签 |
| `image` | 粘贴/拖拽/点击上传 | 缩略图 + 点击放大（灯箱） |
| `file` | 拖拽/点击上传 | 文件卡片（图标 + 文件名 + 大小 + 下载按钮） |
| `link` | 直接输入（自动检测） | 链接卡片（URL + 可点击跳转） |

### 消息自动分类

保留并增强 `detectType()`:

```javascript
function detectType(text, hasAttachment) {
  if (hasAttachment) return hasAttachment.type  // image / file
  if (/^```/.test(text.trim())) return 'code'
  if (/^[a-zA-Z0-9+/=]{20,}$/.test(text.trim())) return 'code'  // base64 长串
  if (/[{}\[\];]/.test(text) && text.split('\n').length > 3) return 'code'
  if (/^https?:\/\//.test(text.trim())) return 'link'
  return 'text'
}
```

### UI 布局（增强版）

```
┌──────────────────────────────────────────────────────────┐
│  ToolPage: IM 通信                                        │
├──────────────┬───────────────────────────────────────────┤
│  左栏 (260px) │  右栏                                      │
│              │                                           │
│  搜索框 🔍    │  聊天头部：设备名 + 在线状态                 │
│              │                                           │
│  在线设备 N   │  消息流：                                   │
│  ──────────  │  ┌──────────────────────────────────────┐ │
│  🟢 设备A    │  │ [10:30]                              │ │
│    桌面端     │  │                                      │ │
│  🟢 设备B    │  │ 设备A:                                │ │
│    手机       │  │ ┌──────────────────────┐             │ │
│              │  │ │ const app = express() │  ← 代码高亮 │ │
│  ──────────  │  │ │ app.listen(3000)     │  [复制]      │ │
│  # 群聊       │  │ └──────────────────────┘             │ │
│    N位成员    │  │                                      │ │
│              │  │ 你:                                   │ │
│              │  │ ┌──────────┐ ┌──────┐ ┌─────────┐    │ │
│              │  │ │ 📷 图片   │ │ 📎  │ │ 📋 粘贴  │    │ │
│              │  │ └──────────┘ └──────┘ └─────────┘    │ │
│              │  │                                      │ │
│              │  │ 你: 收到，我试试 →                      │ │
│              │  └──────────────────────────────────────┘ │
│              │                                           │
│              │  ┌──────────────────────────────────────┐ │
│              │  │ [📎][📷]  输入消息...      [发送]     │ │
│              │  └──────────────────────────────────────┘ │
├──────────────┴───────────────────────────────────────────┤
│  移动端: 左栏→顶部设备条, 聊天全屏, 输入区固定底部           │
└──────────────────────────────────────────────────────────┘
```

### 输入区域增强

```
┌─────────────────────────────────────────────────┐
│ [📎 文件] [📷 图片]  │  textarea (自适应高度)  [发送] │
│                       │  Ctrl+V 粘贴图片              │
│  拖拽文件/图片到此处直接发送                         │
└─────────────────────────────────────────────────┘
```

功能：
- **📎 文件按钮**：点击打开文件选择器，选择任意文件上传
- **📷 图片按钮**：点击选择图片，或直接 Ctrl+V 粘贴剪贴板图片
- **拖拽上传**：拖拽文件/图片到输入区域或消息区域
- **粘贴上传**：Ctrl+V 检测剪贴板是否有图片，有则自动上传
- **自动检测**：输入文本自动判断类型（代码/链接/普通文本）
- 移除加密开关（简化）

### 代码块渲染

```
┌─────────────────────────────────────────┐
│ JavaScript                    [📋 复制]  │
│ ─────────────────────────────────────── │
│ const express = require('express')      │
│ const app = express()                   │
│ app.get('/', (req, res) => {            │
│   res.json({ status: 'ok' })            │
│ })                                      │
│ app.listen(3000)                        │
└─────────────────────────────────────────┘
```

- highlight.js 自动语言检测
- 左上角显示语言标签
- 右上角复制按钮
- 深色背景（暗色主题用深灰色，亮色主题用深蓝色）

### 图片消息

```
发送方:
┌──────────────────────┐  ← 点击放大
│                      │
│    [缩略图 200x200]   │
│                      │
└──────────────────────┘
              10:30 ✓✓

接收方:
┌──────────────────────┐
│                      │
│    [缩略图 200x200]   │
│                      │
└──────────────────────┘
              10:30  [下载]
```

- 缩略图最大 200x200，保持比例
- 点击打开灯箱（全屏查看，支持左右切换该对话中的所有图片）
- 移动端双指缩放

### 文件消息

```
┌──────────────────────────────────────┐
│  📄 nginx.conf                       │
│  1.2 KB · text/plain        [下载]   │
└──────────────────────────────────────┘
```

- 文件图标根据 MIME 类型变化（PDF、ZIP、代码等）
- 显示文件名 + 大小 + MIME 类型
- 点击「下载」触发下载

### 消息操作

悬停/长按消息显示操作菜单：

| 操作 | 文本 | 代码 | 图片 | 文件 |
|------|------|------|------|------|
| 复制内容 | ✅ | ✅ | - | - |
| 复制图片 | - | - | ✅ | - |
| 下载 | - | - | ✅ | ✅ |
| 删除 | ✅ | ✅ | ✅ | ✅ |
| 转发 | ✅ | ✅ | ✅ | ✅ |

### 灯箱组件

点击图片消息打开全屏灯箱：

```
┌──────────────────────────────────────────────┐
│                                          [✕] │
│                                              │
│              ←  [图片全屏预览]  →             │
│                                              │
│  1/5                              [下载]     │
│                                              │
│  ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐                   │
│  │①│ │②│ │③│ │④│ │⑤│  ← 底部缩略图条        │
│  └──┘ └──┘ └──┘ └──┘ └──┘                   │
└──────────────────────────────────────────────┘
```

### composable 重构：`useIm.js`

替代 `useTextTransfer.js`：

```javascript
// 状态
const myId = ref('')
const myName = ref('')
const connected = ref(false)
const peers = ref([])
const activePeer = ref(null)  // null=群聊
const messages = ref({})       // { peerId: [], group: [] }
const typingPeers = ref({})    // { peerId: boolean }

// 连接
function connect()
function disconnect()
function rename(name)

// 消息
function sendMessage(content, targetPeer, attachment)
function deleteMessage(msgId)
function forwardMessage(msgId, targetPeer)

// 文件
async function uploadFile(file)          // → POST /api/im/upload → {url, thumbnail, ...}
async function sendImage(file, target)   // uploadFile + sendMessage
async function sendFile(file, target)    // uploadFile + sendMessage

// 历史
async function loadHistory(peer, limit, before)
async function searchHistory(query)

// 输入状态
function startTyping(targetPeer)
function stopTyping(targetPeer)

// 已读
function markAsRead(peerId)
```

### 灯箱 composable：`useLightbox.js`

```javascript
const visible = ref(false)
const images = ref([])
const currentIndex = ref(0)

function open(imageList, startIndex)
function close()
function next()
function prev()
```

## 文件变更清单

### 新增文件

| 文件 | 说明 |
|------|------|
| `backend/modules/im.py` | IM 模块：SocketIO 事件 + REST API + SQLite + 文件上传 |
| `frontend/src/composables/useIm.js` | IM composable（替代 useTextTransfer.js） |
| `frontend/src/composables/useLightbox.js` | 图片灯箱 composable |
| `frontend/src/components/ImMessage.vue` | 单条消息渲染组件（按 msgType 分支渲染） |
| `frontend/src/components/ImCodeBlock.vue` | 代码块组件（highlight.js 渲染 + 复制 + 语言标签） |
| `frontend/src/components/ImFileCard.vue` | 文件卡片组件（图标 + 文件名 + 大小 + 下载） |
| `frontend/src/components/ImImageMessage.vue` | 图片消息组件（缩略图 + 点击打开灯箱） |
| `frontend/src/components/ImLightbox.vue` | 图片灯箱组件 |
| `frontend/src/components/ImChatInput.vue` | 增强输入组件（文件/图片按钮 + 拖拽 + 粘贴） |

### 修改文件

| 文件 | 变更 |
|------|------|
| `frontend/src/views/TextTransfer.vue` | 重写，使用新组件和 useIm composable |
| `backend/app.py` | 注册 im blueprint，保留 text_transfer 兼容 |
| `frontend/src/locales/zh.json` | 新增 IM 相关 i18n 词条 |
| `frontend/src/locales/en.json` | 新增 IM 相关 i18n 词条 |
| `frontend/package.json` | 新增 `highlight.js` 依赖 |

### 可删除文件（功能已替代）

| 文件 | 说明 |
|------|------|
| `frontend/src/composables/useTextTransfer.js` | 被 useIm.js 替代 |
| `backend/modules/text_transfer.py` | 被 im.py 替代（可延迟删除，先保留兼容） |

## 实施阶段

### Phase 1：基础设施（后端）
1. 创建 `im.py` 模块（SQLite 初始化、SocketIO 事件、REST API）
2. 文件上传端点 + 图片缩略图生成
3. 历史记录 API
4. 注册 blueprint 到 `app.py`

### Phase 2：前端消息组件
1. `ImCodeBlock.vue`（highlight.js 代码高亮）
2. `ImFileCard.vue`（文件卡片）
3. `ImImageMessage.vue`（图片缩略图）
4. `ImMessage.vue`（统一消息渲染器）

### Phase 3：输入增强
1. `ImChatInput.vue`（文件/图片按钮 + 拖拽 + 粘贴）
2. 消息自动分类增强

### Phase 4：高级功能
1. `ImLightbox.vue`（图片灯箱）
2. 消息操作（删除、转发）
3. 历史记录加载 + 搜索
4. 正在输入提示

### Phase 5：收尾
1. 重写 `TextTransfer.vue` 集成所有新组件
2. 移动端适配优化
3. i18n 完善
4. 移除旧 `useTextTransfer.js` 和 `text_transfer.py`

## 技术决策

1. **移除 WebRTC**：局域网场景服务端中转零延迟差异，换取离线消息、历史记录、文件上传能力，且大幅降低代码复杂度。
2. **SQLite 而非纯内存**：支持离线消息和历史搜索，数据量极小（局域网 IM），无需 Redis/PostgreSQL。
3. **服务端文件中转**：不搞 P2P 文件传输，服务端统一存储和转发，稳定可靠。
4. **highlight.js**：前端最成熟的代码高亮库，支持 190+ 语言自动检测。
5. **Pillow 缩略图**：已安装，直接用于生成图片缩略图，无需额外依赖。
6. **组件化消息渲染**：每种消息类型独立组件，便于维护和扩展新类型。
