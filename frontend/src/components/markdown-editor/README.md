# Markdown 编辑器模块化架构

## 📁 目录结构

```
frontend/src/components/markdown-editor/
├── MarkdownEditorContainer.vue    # 主容器组件
├── MarkdownEditorToolbar.vue      # 工具栏组件
├── MarkdownEditorPanel.vue        # 编辑器面板组件
├── MarkdownPreviewPanel.vue       # 预览面板组件
├── index.js                       # 组件导出文件
└── README.md                      # 架构文档
```

## 🏗️ 架构设计

### 设计原则
- **模块化**：每个组件职责单一，易于维护和测试
- **可复用性**：组件可以独立使用或组合使用
- **可扩展性**：易于添加新功能和修改现有功能
- **性能优化**：使用 Vue 3 Composition API 和响应式系统

### 组件职责

#### 1. MarkdownEditorContainer.vue
- **职责**：主容器，协调各个子组件
- **功能**：
  - 组合所有子组件
  - 管理组件间通信
  - 处理全局状态
  - 响应路由变化

#### 2. MarkdownEditorToolbar.vue
- **职责**：提供格式化工具栏
- **功能**：
  - 16个格式化按钮（粗体、斜体、标题、链接等）
  - 工具提示显示
  - 响应式布局适配
  - 事件触发机制

#### 3. MarkdownEditorPanel.vue
- **职责**：文本编辑区域
- **功能**：
  - Markdown 文本输入
  - 字符和行数统计
  - 光标位置管理
  - 键盘事件处理

#### 4. MarkdownPreviewPanel.vue
- **职责**：实时预览区域
- **功能**：
  - HTML 渲染显示
  - 主题切换
  - 滚动同步
  - 样式美化

## 🔧 技术栈

- **Vue 3**：使用 Composition API
- **Element Plus**：UI 组件库
- **Marked**：Markdown 解析库
- **CSS Scoped**：样式隔离
- **ES6 Modules**：模块化导入导出

## 📊 数据流

```
用户输入 → MarkdownEditorPanel → MarkdownEditorContainer → useMarkdownEditor Composable
    ↓
实时更新 ← 状态管理 ← 事件处理 ← 工具栏操作
    ↓
预览渲染 ← MarkdownPreviewPanel ← 主题切换
```

## 🎯 核心特性

### 状态管理 (useMarkdownEditor)
- 使用 Vue 3 Composition API
- 响应式状态管理
- 业务逻辑封装
- 类型安全

### 组件通信
- Props 向下传递数据
- Events 向上触发事件
- 避免直接父子耦合
- 清晰的数据流向

### 性能优化
- 按需渲染
- 防抖更新
- 内存泄漏防护
- 代码分割

## 🚀 使用方法

### 基本使用
```vue
<template>
  <MarkdownEditorContainer />
</template>

<script>
import { MarkdownEditorContainer } from '@/components/markdown-editor'

export default {
  components: {
    MarkdownEditorContainer
  }
}
</script>
```

### 自定义配置
```vue
<template>
  <MarkdownEditorContainer
    :initial-content="customContent"
    :show-toolbar="true"
    :show-preview="true"
    :default-theme="'dark'"
  />
</template>
```

## 🔄 扩展指南

### 添加新格式化按钮
1. 在 `MarkdownEditorToolbar.vue` 中添加按钮
2. 在 `useMarkdownEditor.js` 中实现格式化逻辑
3. 更新样式和响应式布局

### 添加新预览主题
1. 在 `MarkdownPreviewPanel.vue` 中添加主题选项
2. 在样式文件中定义主题样式
3. 更新主题切换逻辑

### 添加新功能
1. 在 composable 中添加状态和方法
2. 在相应组件中添加 UI
3. 通过事件系统连接组件

## 🧪 测试策略

### 单元测试
- 每个组件的独立功能测试
- Composable 逻辑测试
- 工具函数测试

### 集成测试
- 组件间交互测试
- 数据流完整性测试
- 用户操作流程测试

### E2E 测试
- 完整用户场景测试
- 跨浏览器兼容性测试
- 性能测试

## 📈 性能监控

### 指标监控
- 组件渲染时间
- 内存使用情况
- 用户交互响应时间
- Markdown 解析性能

### 优化策略
- 虚拟滚动（大文档）
- 懒加载（预览内容）
- 防抖（实时更新）
- 缓存（解析结果）

## 🔒 安全性

### 输入验证
- Markdown 语法验证
- HTML 转义处理
- XSS 防护
- 文件上传安全检查

### 错误处理
- 优雅的错误提示
- 降级处理机制
- 日志记录
- 用户友好的错误信息

## 🎨 设计规范

### 视觉设计
- 现代化的 UI 设计
- 一致的颜色系统
- 清晰的视觉层次
- 优秀的可访问性

### 交互设计
- 直观的操作反馈
- 流畅的动画效果
- 键盘快捷键支持
- 移动端适配

## 📚 相关文档

- [Vue 3 官方文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Marked 文档](https://marked.js.org/)
- [Markdown 语法指南](https://www.markdownguide.org/)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交变更
4. 发起 Pull Request
5. 代码审查
6. 合并代码

## 📄 许可证

本项目采用 MIT 许可证。
