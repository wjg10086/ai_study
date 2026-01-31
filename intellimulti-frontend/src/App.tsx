import React, { Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';

// Lazy load pages
// 使用 default export 进行懒加载
const Home = React.lazy(() => import('./pages/Home').then(module => ({ default: module.Home })));
const ChatPage = React.lazy(() => import('./pages/ChatPage'));

const Loading = () => (
  <div className="flex items-center justify-center h-screen w-screen bg-gray-50">
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
  </div>
);

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <BrowserRouter>
        <Suspense fallback={<Loading />}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/chat/qa" element={<ChatPage />} />
            <Route path="/chat/image" element={<ChatPage />} />
            <Route path="/chat/audio" element={<ChatPage />} />
            <Route path="/chat/pdf" element={<ChatPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
