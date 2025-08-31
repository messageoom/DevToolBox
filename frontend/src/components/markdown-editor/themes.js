// Markdown 编辑器主题配置
export const typographyThemes = [
  {
    id: 'classic',
    name: '经典优雅',
    description: '简洁大方的经典排版',
    sample: '优雅而简洁的文字排版',
    styles: {
      fontFamily: '"Times New Roman", serif',
      fontSize: '16px',
      lineHeight: '1.6',
      color: '#333',
      backgroundColor: '#fff',
      maxWidth: '800px',
      margin: '0 auto',
      padding: '20px'
    },
    headingStyles: {
      fontFamily: '"Georgia", serif',
      fontWeight: 'bold',
      color: '#222',
      marginTop: '1.5em',
      marginBottom: '0.5em'
    }
  },
  {
    id: 'modern',
    name: '现代简约',
    description: '现代感十足的简约设计',
    sample: '现代简约的设计风格',
    styles: {
      fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
      fontSize: '16px',
      lineHeight: '1.7',
      color: '#333',
      backgroundColor: '#fafafa',
      maxWidth: '900px',
      margin: '0 auto',
      padding: '30px',
      borderRadius: '8px'
    },
    headingStyles: {
      fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
      fontWeight: '300',
      color: '#222',
      marginTop: '2em',
      marginBottom: '0.8em',
      letterSpacing: '-0.02em'
    }
  },
  {
    id: 'book',
    name: '图书风格',
    description: '类似纸质图书的阅读体验',
    sample: '如同阅读纸质图书般舒适',
    styles: {
      fontFamily: '"Bookerly", "Times New Roman", serif',
      fontSize: '17px',
      lineHeight: '1.8',
      color: '#2c2c2c',
      backgroundColor: '#f9f6f0',
      maxWidth: '700px',
      margin: '0 auto',
      padding: '40px',
      boxShadow: '0 0 20px rgba(0,0,0,0.1)'
    },
    headingStyles: {
      fontFamily: '"Bookerly", "Times New Roman", serif',
      fontWeight: 'normal',
      color: '#1a1a1a',
      marginTop: '2.5em',
      marginBottom: '1em',
      textAlign: 'center'
    }
  },
  {
    id: 'magazine',
    name: '杂志风格',
    description: '时尚杂志般的精美排版',
    sample: '精美时尚的杂志风格',
    styles: {
      fontFamily: '"Playfair Display", serif',
      fontSize: '16px',
      lineHeight: '1.6',
      color: '#333',
      backgroundColor: '#fff',
      maxWidth: '1000px',
      margin: '0 auto',
      padding: '50px',
      backgroundImage: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)'
    },
    headingStyles: {
      fontFamily: '"Playfair Display", serif',
      fontWeight: '400',
      color: '#1a1a1a',
      marginTop: '2em',
      marginBottom: '0.5em',
      textTransform: 'uppercase',
      letterSpacing: '0.1em',
      fontSize: '1.2em'
    }
  },
  {
    id: 'academic',
    name: '学术论文',
    description: '适合学术论文的专业排版',
    sample: '专业严谨的学术风格',
    styles: {
      fontFamily: '"Times New Roman", serif',
      fontSize: '12pt',
      lineHeight: '1.5',
      color: '#000',
      backgroundColor: '#fff',
      maxWidth: '800px',
      margin: '0 auto',
      padding: '25px',
      textAlign: 'justify'
    },
    headingStyles: {
      fontFamily: '"Times New Roman", serif',
      fontWeight: 'bold',
      color: '#000',
      marginTop: '1.5em',
      marginBottom: '0.5em',
      textAlign: 'center'
    }
  },
  {
    id: 'novel',
    name: '小说阅读',
    description: '专为小说阅读优化的舒适体验',
    sample: '沉浸式的小说阅读体验',
    styles: {
      fontFamily: '"Palatino Linotype", "Book Antiqua", Palatino, serif',
      fontSize: '18px',
      lineHeight: '1.8',
      color: '#2c2c2c',
      backgroundColor: '#fefefe',
      maxWidth: '600px',
      margin: '0 auto',
      padding: '60px 40px',
      textAlign: 'justify',
      textIndent: '2em'
    },
    headingStyles: {
      fontFamily: '"Palatino Linotype", "Book Antiqua", Palatino, serif',
      fontWeight: 'normal',
      color: '#1a1a1a',
      marginTop: '3em',
      marginBottom: '1.5em',
      textAlign: 'center',
      fontSize: '1.5em'
    }
  }
]

export const codeThemes = [
  {
    id: 'github',
    name: 'GitHub 主题',
    description: 'GitHub 官方代码高亮主题',
    sample: 'function hello() {\n  console.log("Hello World!");\n}',
    styles: {
      backgroundColor: '#f6f8fa',
      color: '#24292e',
      border: '1px solid #e1e4e8',
      borderRadius: '6px',
      fontFamily: '"SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace',
      fontSize: '12px',
      lineHeight: '1.45',
      padding: '16px',
      overflow: 'auto'
    },
    keywordColor: '#d73a49',
    stringColor: '#032f62',
    commentColor: '#6a737d',
    functionColor: '#6f42c1'
  },
  {
    id: 'monokai',
    name: 'Monokai 主题',
    description: '经典的 Monokai 代码主题',
    sample: 'def fibonacci(n):\n    if n <= 1:\n        return n',
    styles: {
      backgroundColor: '#272822',
      color: '#f8f8f2',
      border: '1px solid #49483e',
      borderRadius: '6px',
      fontFamily: '"Monaco", "Menlo", "Ubuntu Mono", monospace',
      fontSize: '12px',
      lineHeight: '1.45',
      padding: '16px',
      overflow: 'auto'
    },
    keywordColor: '#f92672',
    stringColor: '#e6db74',
    commentColor: '#75715e',
    functionColor: '#a6e22e'
  },
  {
    id: 'dracula',
    name: 'Dracula 主题',
    description: '深受喜爱的暗色代码主题',
    sample: 'const greet = (name) => {\n  return `Hello, ${name}!`;\n};',
    styles: {
      backgroundColor: '#282a36',
      color: '#f8f8f2',
      border: '1px solid #44475a',
      borderRadius: '6px',
      fontFamily: '"Fira Code", "Monaco", "Menlo", monospace',
      fontSize: '12px',
      lineHeight: '1.45',
      padding: '16px',
      overflow: 'auto'
    },
    keywordColor: '#ff79c6',
    stringColor: '#f1fa8c',
    commentColor: '#6272a4',
    functionColor: '#50fa7b'
  },
  {
    id: 'solarized',
    name: 'Solarized 主题',
    description: '精心调校的配色方案',
    sample: 'public class Hello {\n    public static void main(String[] args) {\n        System.out.println("Hello World");\n    }\n}',
    styles: {
      backgroundColor: '#fdf6e3',
      color: '#586e75',
      border: '1px solid #eee8d5',
      borderRadius: '6px',
      fontFamily: '"Source Code Pro", "Monaco", monospace',
      fontSize: '12px',
      lineHeight: '1.45',
      padding: '16px',
      overflow: 'auto'
    },
    keywordColor: '#dc322f',
    stringColor: '#2aa198',
    commentColor: '#93a1a1',
    functionColor: '#268bd2'
  },
  {
    id: 'atom',
    name: 'Atom One 主题',
    description: 'Atom 编辑器的经典主题',
    sample: 'import React from "react";\n\nfunction App() {\n  return <div>Hello React!</div>;\n}',
    styles: {
      backgroundColor: '#fafafa',
      color: '#383a42',
      border: '1px solid #e5e5e6',
      borderRadius: '6px',
      fontFamily: '"Fira Code", "Monaco", monospace',
      fontSize: '12px',
      lineHeight: '1.45',
      padding: '16px',
      overflow: 'auto'
    },
    keywordColor: '#a626a4',
    stringColor: '#50a14f',
    commentColor: '#a0a1a7',
    functionColor: '#4078f2'
  },
  {
    id: 'vs-code',
    name: 'VS Code 主题',
    description: 'Visual Studio Code 默认主题',
    sample: 'let message = "Hello TypeScript!";\nconsole.log(message);',
    styles: {
      backgroundColor: '#1e1e1e',
      color: '#d4d4d4',
      border: '1px solid #3e3e42',
      borderRadius: '6px',
      fontFamily: '"Consolas", "Monaco", monospace',
      fontSize: '12px',
      lineHeight: '1.45',
      padding: '16px',
      overflow: 'auto'
    },
    keywordColor: '#569cd6',
    stringColor: '#ce9178',
    commentColor: '#6a9955',
    functionColor: '#dcdcaa'
  }
]

// 默认主题
export const defaultTypographyTheme = typographyThemes[0]
export const defaultCodeTheme = codeThemes[0]

// 获取主题配置
export function getTypographyTheme(themeId) {
  return typographyThemes.find(theme => theme.id === themeId) || defaultTypographyTheme
}

export function getCodeTheme(themeId) {
  return codeThemes.find(theme => theme.id === themeId) || defaultCodeTheme
}

// 应用主题样式到元素
export function applyTypographyTheme(element, theme) {
  if (!element || !theme) return

  Object.assign(element.style, theme.styles)

  // 应用标题样式
  const headings = element.querySelectorAll('h1, h2, h3, h4, h5, h6')
  headings.forEach(heading => {
    Object.assign(heading.style, theme.headingStyles)
  })
}

export function applyCodeTheme(element, theme) {
  if (!element || !theme) return

  const codeBlocks = element.querySelectorAll('pre')
  codeBlocks.forEach(block => {
    Object.assign(block.style, theme.styles)
  })

  const inlineCodes = element.querySelectorAll('code')
  inlineCodes.forEach(code => {
    if (!code.closest('pre')) {
      Object.assign(code.style, {
        backgroundColor: theme.styles.backgroundColor,
        color: theme.keywordColor,
        padding: '2px 4px',
        borderRadius: '3px',
        fontSize: '0.9em'
      })
    }
  })
}
