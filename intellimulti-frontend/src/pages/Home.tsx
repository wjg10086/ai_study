import React from 'react';
import { Card, Typography } from 'antd';
import { useNavigate } from 'react-router-dom';
import { MessageSquare, Image, Mic, FileText } from 'lucide-react';

const { Title } = Typography;

/**
 * 首页功能配置
 */
const features = [
  {
    title: '智能问答',
    description: '与大模型进行纯文本对话，获取智能回答。',
    icon: <MessageSquare size={48} className="text-blue-500" />,
    path: '/chat/qa'
  },
  {
    title: '图片分析',
    description: '上传图片，让大模型帮您分析图片内容。',
    icon: <Image size={48} className="text-green-500" />,
    path: '/chat/image'
  },
  {
    title: '音频转写',
    description: '上传音频文件，快速转换为文本并进行问答。',
    icon: <Mic size={48} className="text-purple-500" />,
    path: '/chat/audio'
  },
  {
    title: 'PDF解析',
    description: '上传PDF文档，基于文档内容进行精准问答。',
    icon: <FileText size={48} className="text-red-500" />,
    path: '/chat/pdf'
  }
];

/**
 * 首页组件
 * 展示系统四大核心功能入口
 */
export const Home: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="h-full flex flex-col items-center justify-center p-8 animate-fade-in">
      <Title level={2} className="mb-12 text-gray-800 font-bold">欢迎使用多模态大模型 RAG 系统</Title>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl w-full">
        {features.map((feature) => (
          <Card
            key={feature.path}
            hoverable
            className="flex flex-col items-center text-center p-6 border-gray-200 shadow-sm hover:shadow-md transition-all hover:-translate-y-1"
            onClick={() => navigate(feature.path)}
          >
            <div className="mb-6 flex justify-center">{feature.icon}</div>
            <Title level={4} className="mb-3">{feature.title}</Title>
            <p className="text-gray-500 text-base">{feature.description}</p>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Home;
