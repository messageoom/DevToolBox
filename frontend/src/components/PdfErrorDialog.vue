<template>
  <el-dialog
    v-model="visible"
    title="PDF生成错误"
    width="500px"
    :before-close="handleClose"
  >
    <div class="error-container">
      <div class="error-icon">
        <el-icon color="#F56C6C" size="48"><Warning /></el-icon>
      </div>
      <div class="error-content">
        <h3>PDF生成失败</h3>
        <p class="error-message">{{ formattedErrorMessage }}</p>
        <div class="solution">
          <h4>解决方案：</h4>
          <ol>
            <li>安装wkhtmltopdf工具（推荐）</li>
            <li>或配置WeasyPrint依赖</li>
          </ol>
          <p>详细安装说明请参考项目文档</p>
        </div>
      </div>
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="viewSolution">
          查看解决方案
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script>
import { ref, computed } from 'vue'
import { ElDialog, ElIcon, ElButton } from 'element-plus'
import { Warning } from '@element-plus/icons-vue'

export default {
  name: 'PdfErrorDialog',
  components: {
    ElDialog,
    ElIcon,
    ElButton,
    Warning
  },
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    errorMessage: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'view-solution'],
  setup(props, { emit }) {
    const visible = ref(props.modelValue)

    // 格式化错误信息，提取关键内容
    const formattedErrorMessage = computed(() => {
      if (!props.errorMessage) return '未知错误'
      
      // 如果是JSON格式的错误信息，尝试解析
      try {
        const parsed = JSON.parse(props.errorMessage)
        if (parsed.error) {
          return parsed.error
        }
      } catch (e) {
        // 不是JSON格式，直接使用原始信息
      }
      
      // 如果错误信息过长，截取前200个字符
      if (props.errorMessage.length > 200) {
        return props.errorMessage.substring(0, 200) + '...'
      }
      
      return props.errorMessage
    })

    const handleClose = () => {
      visible.value = false
      emit('update:modelValue', false)
    }

    const viewSolution = () => {
      emit('view-solution')
      handleClose()
    }

    return {
      visible,
      formattedErrorMessage,
      handleClose,
      viewSolution
    }
  }
}
</script>

<style scoped>
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.error-icon {
  margin-bottom: 20px;
}

.error-content h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.error-message {
  color: #666;
  margin-bottom: 20px;
  line-height: 1.5;
  word-wrap: break-word;
}

.solution {
  background-color: #f5f7fa;
  border-radius: 4px;
  padding: 15px;
  text-align: left;
  width: 100%;
}

.solution h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.solution ol {
  margin: 0 0 15px 20px;
  padding: 0;
}

.solution li {
  margin-bottom: 8px;
  line-height: 1.5;
}

.solution p {
  margin: 0;
  font-size: 14px;
  color: #999;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>