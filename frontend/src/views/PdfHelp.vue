<template>
  <div class="pdf-help">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-icon class="card-icon"><QuestionFilled /></el-icon>
          <span>PDF生成帮助</span>
        </div>
      </template>
      
      <div class="help-content">
        <el-alert
          title="PDF生成问题解决方案"
          type="warning"
          description="如果您在生成PDF时遇到问题，请按照以下步骤解决"
          show-icon
          style="margin-bottom: 20px;"
        />
        
        <el-tabs v-model="activeTab">
          <el-tab-pane label="问题描述" name="problem">
            <div class="tab-content">
              <h3>问题现象</h3>
              <p>在使用"Markdown转PDF"或"HTML转PDF"功能时，可能会遇到以下错误：</p>
              <el-alert
                title="Request failed with status code 500"
                type="error"
                description="这表示服务器内部错误，通常是由于缺少PDF生成工具导致的。"
                show-icon
              />
              
              <h3>问题原因</h3>
              <p>PDF生成功能依赖于外部的PDF转换工具，系统支持两种转换器：</p>
              <ol>
                <li><strong>WeasyPrint</strong>（默认，功能更强大但配置复杂）</li>
                <li><strong>wkhtmltopdf</strong>（备选，安装简单）</li>
              </ol>
              <p>当这些工具未正确安装或配置时，就会出现500错误。</p>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="解决方案一：安装wkhtmltopdf（推荐）" name="solution1">
            <div class="tab-content">
              <h3>步骤1：下载安装wkhtmltopdf</h3>
              <ol>
                <li>访问官网：<a href="https://wkhtmltopdf.org/downloads.html" target="_blank">https://wkhtmltopdf.org/downloads.html</a></li>
                <li>下载适用于Windows的安装包</li>
                <li>运行安装程序完成安装</li>
              </ol>
              
              <h3>步骤2：验证安装</h3>
              <p>打开命令提示符，执行以下命令：</p>
              <el-alert
                title="wkhtmltopdf --version"
                type="info"
              />
              <p>如果安装成功，应该会显示版本信息。</p>
              
              <h3>步骤3：重启开发服务器</h3>
              <p>安装完成后，重启DevToolBox开发服务器。</p>
              
              <el-alert
                title="提示"
                type="success"
                description="这是最简单快捷的解决方案，适合大多数用户。"
                show-icon
              />
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="解决方案二：配置WeasyPrint" name="solution2">
            <div class="tab-content">
              <h3>步骤1：安装MSYS2</h3>
              <ol>
                <li>访问官网：<a href="https://www.msys2.org/" target="_blank">https://www.msys2.org/</a></li>
                <li>下载并安装MSYS2</li>
              </ol>
              
              <h3>步骤2：安装GTK库</h3>
              <ol>
                <li>打开MSYS2终端</li>
                <li>执行命令：<code>pacman -S mingw-w64-x86_64-pango</code></li>
              </ol>
              
              <h3>步骤3：设置环境变量</h3>
              <p>在命令提示符中执行：</p>
              <el-alert
                title="set WEASYPRINT_DLL_DIRECTORIES=C:\msys64\mingw64\bin"
                type="info"
              />
              <p>注意：请根据实际安装路径调整上述命令。</p>
              
              <h3>步骤4：重启开发服务器</h3>
              <p>完成配置后，重启DevToolBox开发服务器。</p>
              
              <el-alert
                title="提示"
                type="warning"
                description="此方案适合需要更高级PDF生成功能的用户，配置相对复杂。"
                show-icon
              />
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="验证解决方案" name="verification">
            <div class="tab-content">
              <h3>验证方法</h3>
              <p>完成上述任一方案后，按照以下步骤验证解决方案：</p>
              <ol>
                <li>重新启动开发服务器</li>
                <li>打开DevToolBox应用</li>
                <li>导航到"数据互转"页面</li>
                <li>在"Markdown转PDF"或"HTML转PDF"功能中输入测试内容</li>
                <li>点击"生成PDF"按钮</li>
                <li>如果成功生成PDF文件，说明问题已解决</li>
              </ol>
              
              <h3>常见问题</h3>
              <el-collapse>
                <el-collapse-item title="安装wkhtmltopdf后仍然出现错误">
                  <p>请检查：</p>
                  <ul>
                    <li>wkhtmltopdf是否已正确安装</li>
                    <li>系统PATH环境变量是否包含了wkhtmltopdf的安装路径</li>
                    <li>是否已重启开发服务器</li>
                  </ul>
                </el-collapse-item>
                <el-collapse-item title="中文显示问题">
                  <p>请确保：</p>
                  <ul>
                    <li>系统中安装了适当的中文字体</li>
                    <li>在HTML中明确指定中文字体族</li>
                  </ul>
                </el-collapse-item>
                <el-collapse-item title="图片无法显示">
                  <p>请检查：</p>
                  <ul>
                    <li>图片路径是否正确</li>
                    <li>是否使用了绝对路径或base64编码</li>
                  </ul>
                </el-collapse-item>
              </el-collapse>
            </div>
          </el-tab-pane>
        </el-tabs>
        
        <div class="action-section">
          <el-button type="primary" @click="goBack">返回数据互转页面</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElCard, ElTabs, ElTabPane, ElAlert, ElButton, ElCollapse, ElCollapseItem, ElIcon } from 'element-plus'
import { QuestionFilled } from '@element-plus/icons-vue'

export default {
  name: 'PdfHelp',
  components: {
    ElCard,
    ElTabs,
    ElTabPane,
    ElAlert,
    ElButton,
    ElCollapse,
    ElCollapseItem,
    ElIcon,
    QuestionFilled
  },
  setup() {
    const router = useRouter()
    const activeTab = ref('problem')
    
    const goBack = () => {
      router.push('/data-conversion')
    }
    
    return {
      activeTab,
      goBack
    }
  }
}
</script>

<style scoped>
.pdf-help {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
}

.card-icon {
  margin-right: 8px;
  font-size: 18px;
}

.help-content {
  line-height: 1.6;
}

.tab-content {
  padding: 20px 0;
}

.tab-content h3 {
  margin-top: 0;
  color: #333;
}

.tab-content p {
  margin: 10px 0;
}

.tab-content ol,
.tab-content ul {
  margin: 10px 0;
  padding-left: 20px;
}

.tab-content li {
  margin-bottom: 8px;
}

.tab-content code {
  background-color: #f6f8fa;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

.action-section {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
</style>