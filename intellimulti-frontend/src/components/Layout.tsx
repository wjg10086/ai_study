import React from 'react';
import { Layout as AntLayout, Menu, theme } from 'antd';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { MessageSquare, Image, Mic, FileText, Home } from 'lucide-react';

const { Header, Content, Sider } = AntLayout;

const items = [
  { key: '/', icon: <Home size={18} />, label: '首页' },
  { key: '/chat/qa', icon: <MessageSquare size={18} />, label: '智能问答' },
  { key: '/chat/image', icon: <Image size={18} />, label: '图片分析' },
  { key: '/chat/audio', icon: <Mic size={18} />, label: '音频转写' },
  { key: '/chat/pdf', icon: <FileText size={18} />, label: 'PDF解析' },
];

interface LayoutProps {
  title?: string;
  children?: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ title, children }) => {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();
  const navigate = useNavigate();
  const location = useLocation();

  // Highlight the current menu item based on path
  const getSelectedKey = () => {
    if (location.pathname === '/') return '/';
    // Match /chat/qa, /chat/image etc.
    const match = items.find(item => location.pathname.startsWith(item.key) && item.key !== '/');
    return match ? match.key : location.pathname;
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0">
        <div className="h-16 flex items-center justify-center">
          <div className="text-white text-lg font-bold">多模态 RAG</div>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[getSelectedKey()]}
          items={items.map(item => ({
            ...item, 
            onClick: () => navigate(item.key)
          }))}
        />
      </Sider>
      <AntLayout>
        <Header style={{ padding: 0, background: colorBgContainer }} className="flex items-center px-4 shadow-sm z-10">
          <h2 className="text-lg font-medium m-0">
            {title || items.find(i => i.key === getSelectedKey())?.label || '多模态 RAG 系统'}
          </h2>
        </Header>
        <Content style={{ margin: '16px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div
            style={{
              padding: 24,
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden'
            }}
          >
            {children || <Outlet />}
          </div>
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;
