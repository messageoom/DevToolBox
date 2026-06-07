# 文本传输功能设计文档

## 概述

为 DevToolBox 添加局域网文本传输功能，支持设备间实时发送文本消息。采用 WebSocket 信令 + WebRTC P2P 直连架构（与 LanDrop 相同思路），集成到现有 Flask + Vue 3 应用中。

## 功能范围

- **设备发现**：局域网内设备自动发现，实时显示在线设备列表
- **私聊文本传输**：选中设备发送文本，支持普通模式和 E2E 加密模式（WebRTC DataChannel）
- **群聊广播**：向所有在线设备广播消息（服务端中转）
- **历史记录**：本地存储最近 200 条传输记录（localStorage）

## 架构

```
浏览器 A ←── WebSocket ──→ Flask-SocketIO (信令) ←── WebSocket ──→ 浏览器 B
    │                                                                    │
    └──────────────── WebRTC DataChannel (P2P 直连) ────────────────────┘
```

- **信令服务**：Flask-SocketIO，集成到现有 Flask 应用，复用 Token 认证体系
- **P2P 传输**：WebRTC DataChannel，SDP 和 ICE 通过信令服务交换
- **ICE 服务器**：空列表（纯局域网直连）
- **设备注册表**：内存存储（Python dict + threading lock），断开即消失

## 信令协议

### 消息类型

| 类型 | 方向 | 用途 |
|------|------|------|
| `join` | 客户端→服务端 | 加入网络，注册设备 |
| `peers` | 服务端→客户端 | 在线设备列表更新 |
| `leave` | 服务端→客户端 | 设备离线通知 |
| `offer-text` | 发送方→接收方 | 文本传输请求 |
| `accept-text` | 接收方→发送方 | 接受传输 |
| `reject-text` | 接收方→发送方 | 拒绝传输 |
| `sdp-offer` | 双向 | WebRTC SDP offer |
| `sdp-answer` | 双向 | WebRTC SDP answer |
| `ice-candidate` | 双向 | ICE 候选交换 |
| `chat` | 客户端→服务端→广播 | 群聊消息 |
| `rename` | 客户端→服务端 | 重命名设备 |

### 私聊文本传输流程

```
A 发文本给 B:

1. A → Server:  offer-text {to: B_id, content: "...", secure: true}
2. Server → B:  offer-text {from: A_id, content: "...", secure: true}

secure=true (WebRTC P2P):
  3a. B → Server:  accept-text {to: A_id}
  3b. A → Server:  sdp-offer {to: B_id, sdp: ...}
  3c. B → Server:  sdp-answer {to: A_id, sdp: ...}
  3d. 双方交换 ice-candidate
  3e. DataChannel 建立 → 文本发送 → 确认

secure=false (服务端中转):
  3a. B → Server:  accept-text {to: A_id}
  3b. Server 转发文本内容给 B

B 拒绝:
  3x. B → Server: reject-text {to: A_id}
```

### 群聊广播流程

```
A 发群聊:
1. A → Server:  chat {content: "..."}
2. Server → 所有其他节点:  chat {from: A_id, fromName: "...", content: "...", timestamp: ...}
```

## 前端页面设计

### 布局：即时通讯风格双栏

```
┌─────────────────────────────────────────────────────┐
│  ToolPage: 文本传输                                   │
├──────────────┬──────────────────────────────────────┤
│  左栏 (30%)  │  右栏 (70%)                            │
│              │                                      │
│  在线设备     │  聊天头部：设备名 + E2E 标识           │
│  N台在线      │                                      │
│              │  消息流：                              │
│  🟣 设备1     │  - 对方消息：左对齐灰色气泡            │
│  🟡 设备2     │  - 自己消息：右对齐蓝色气泡            │
│  🔵 设备3     │  - 代码块：文件名+行数，可展开         │
│              │  - 每条带时间戳，已送达 ✓✓             │
│  # 群聊       │                                      │
│    N位成员    │  输入区：                              │
│              │  - textarea 自适应高度 (2-6行)         │
│              │  - Enter 发送，Shift+Enter 换行        │
│              │  - 🔒 加密开关 + 发送按钮              │
├──────────────┴──────────────────────────────────────┤
│  移动端: 左栏折叠为顶部设备选择器，聊天全屏              │
└─────────────────────────────────────────────────────┘
```

### 左栏设备列表

- 顶部「在线设备 N 台在线」+ 连接状态指示灯
- 设备卡片：彩色头像（首字）+ 名称 + IP + 在线绿点
- 群聊入口在底部，`#` 图标 + 成员数
- 当前选中项高亮（左边框 + 背景色变化）

### 右栏聊天区

- 头部显示当前对话设备名 + 🔒 E2E 标识（加密模式时）
- 聊天气泡：对方灰色左对齐，自己蓝色右对齐
- 代码/配置文件自动识别：显示文件名+行数，可展开
- 接收消息带「复制」按钮
- 输入框：自适应高度，Enter 发送 / Shift+Enter 换行
- 发送时 loading 状态

### 移动端适配 (<768px)

- 左栏收起为顶部水平滚动的设备头像条
- 聊天区全屏
- 底部导航新增「传输」入口

## 后端设计

### 设备注册表

```python
# backend/modules/text_transfer.py
connected_nodes = {}  # {nodeId: {sid, name, ip}}
_nodes_lock = threading.Lock()
```

### 设备命名

- 首次连接时后端随机生成中文名（形容词+动物+数字）
- 前端存入 sessionStorage，刷新保持一致性
- 支持通过 `rename` 事件修改

### SocketIO 事件处理

```python
@socketio.on('join')
def handle_join(data):
    # 注册设备到 connected_nodes
    # 回复当前在线列表
    # 广播更新给所有其他节点

@socketio.on('disconnect')
def handle_disconnect():
    # 从 connected_nodes 移除
    # 广播 leave 事件

@socketio.on('offer-text')
def handle_offer_text(data):
    # 验证目标设备在线
    # 转发 offer 给目标

@socketio.on('accept-text') / @socketio.on('reject-text')
def handle_response(data):
    # 转发响应给发送方

@socketio.on('sdp-offer') / @socketio.on('sdp-answer')
def handle_sdp(data):
    # 转发 SDP 给目标设备

@socketio.on('ice-candidate')
def handle_ice(data):
    # 转发 ICE candidate

@socketio.on('chat')
def handle_chat(data):
    # 广播给所有在线设备（排除发送者）

@socketio.on('rename')
def handle_rename(data):
    # 更新设备名称，广播新列表
```

### create_app() 改造

- 初始化 `SocketIO(app, cors_allowed_origins=..., async_mode='threading')`
- 注册 text_transfer 事件处理器
- 启动方式从 `app.run()` 改为 `socketio.run(app, host, port)`

## 前端设计

### 组件结构

- `TextTransfer.vue` — 主页面，双栏布局
- `useTextTransfer.js` — composable，封装 SocketIO 客户端 + WebRTC 逻辑

### useTextTransfer.js 职责

- SocketIO 连接管理（connect/disconnect/reconnect）
- 设备列表状态维护
- WebRTC RTCPeerConnection 生命周期管理
- DataChannel 文本收发
- 消息状态管理（发送中/已送达/已接收）

### WebRTC 配置

```javascript
const config = { iceServers: [] }
// DataChannel: ordered, reliable
// 每个 P2P 连接独立的 RTCPeerConnection
```

### 历史记录

存储在 localStorage key `text-transfer-history`，结构：

```json
[
  {
    "id": "uuid",
    "peerId": "xxx",
    "peerName": "敏捷的猫咪",
    "direction": "sent|received",
    "content": "...",
    "timestamp": 1706000100,
    "secure": true,
    "type": "text|code|url"
  }
]
```

保留最近 200 条，超出自动清理最早的。

## 文件变更清单

### 新增文件

| 文件 | 说明 |
|------|------|
| `backend/modules/text_transfer.py` | SocketIO 信令处理、设备注册、消息路由 |
| `frontend/src/views/TextTransfer.vue` | 主页面，IM 风格双栏布局 |
| `frontend/src/composables/useTextTransfer.js` | SocketIO + WebRTC 逻辑封装 |

### 修改文件

| 文件 | 变更 |
|------|------|
| `backend/app.py` | 初始化 SocketIO，注册事件，`app.run()` → `socketio.run()` |
| `requirements.txt` | 新增 `flask-socketio`、`python-engineio` |
| `frontend/src/router/index.js` | 新增 `/text-transfer` 路由 |
| `frontend/src/App.vue` | sidebar categoryToolMap 添加入口 |
| `frontend/src/data/toolCategories.js` | 新增文本传输分类 |
| `frontend/src/locales/zh.json` | 中文 i18n 词条 |
| `frontend/src/locales/en.json` | 英文 i18n 词条 |

### 新增依赖

- Python: `flask-socketio`, `python-engineio`
- npm: `socket.io-client`

## 技术决策

1. **Flask-SocketIO 而非独立信令服务**：单进程部署，复用 Token 认证，改动最小。信令数据量小（仅 SDP/ICE），性能足够。
2. **WebRTC DataChannel 加密传输**：复用 LanDrop 的 P2P 思路，DTLS 提供端到端加密。
3. **内存设备注册表而非数据库**：设备列表是临时的，不需要持久化，保持简单。
4. **localStorage 存历史**：无需服务端存储，简单无依赖，只在本机可见。
5. **空 ICE 服务器列表**：纯局域网场景，不需要 STUN/TURN 打洞。
