# 项目：智汇多模系统 (IntelliMulti-RAG)

intellimulti-backend 后端目录

其中temp文件夹内容和整体代码文件demo.py忽略







前端项目 “多模态大模型RAG系统” ( intellimulti-frontend ) 已构建完成。项目基于 Vite + React + TypeScript + Ant Design + Tailwind CSS 技术栈，实现了所有核心功能需求，包括首页导航、四个独立的功能对话页面（智能问答、图片分析、音频转写、PDF解析），并集成了流式对话和文件上传功能。

以下是项目的主要实现细节：

1. 项目初始化与架构

- 技术栈 : 使用 react-ts 模板初始化，集成了 antd (UI组件), tailwindcss (原子化样式), zustand (状态管理), react-router-dom (路由), lucide-react (图标)。
- 目录结构 :
  - src/pages/ : 包含 Home (功能入口) 和 ChatPage (复用的对话页面)。
  - src/components/ : 包含 Layout (侧边栏导航布局), MessageBubble (消息气泡，支持Markdown渲染), ChatInput (输入框与文件上传)。
  - src/modules/chat/ : 包含核心业务逻辑 service.ts (SSE流式请求), store.ts (Zustand状态管理), types.ts (类型定义)。
2. 核心功能实现

- 首页导航 : 清晰展示四个功能卡片，点击即可跳转至对应模块。
- 流式对话 (SSE) : 封装了 streamChat 服务，支持与后端 /api/chat/stream 接口进行流式交互，实时渲染大模型返回的文本。
- 多模态支持 :
  - 智能问答 : 纯文本对话。
  - 图片/音频/PDF : 支持在对话中上传相应格式的文件，文件以 FormData 形式发送给后端，前端展示上传预览。
- Markdown 渲染 : 使用 react-markdown 和 remark-gfm 渲染大模型返回的格式化文本。
3. 代码规范与最佳实践

- 组件分离 : 容器组件 ( ChatPage ) 管理状态与逻辑，展示组件 ( MessageBubble , ChatInput ) 专注 UI 渲染。
- 路由懒加载 : 使用 React.lazy 和 Suspense 对各功能页面进行按需加载，提升首屏性能。
- 样式管理 : 结合 Ant Design 的全局配置 ( ConfigProvider ) 与 Tailwind CSS 的灵活样式，确保界面现代简洁。
如何运行前端项目：

1. 进入前端目录：
   ```
   cd 
   c:\code\intellimulti-rag\intellimu
   lti-frontend
   ```
2. 启动开发服务器：
   ```
   npm run dev
   ```
3. 在浏览器访问控制台输出的地址（通常是 http://localhost:5173 ）。
注意 : 请确保后端服务 ( intellimulti-backend ) 已在 http://localhost:8000 启动，以便前端能够正常调用接口。前端接口。前端已配置为直接请求本地后端接口。