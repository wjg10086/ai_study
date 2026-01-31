import React, { useEffect, useRef } from 'react';
import { useLocation, useParams } from 'react-router-dom';
import { useChatStore } from '../modules/chat/store';
import { streamChat } from '../modules/chat/service';
import Layout from '../components/Layout';
import MessageBubble from '../components/MessageBubble';
import ChatInput from '../components/ChatInput';
import Empty from '../components/Empty';
import { ChatMode } from '../modules/chat/types';

/**
 * 聊天页面组件
 * 根据路由参数 mode 渲染不同的聊天模式（QA、图片、音频、PDF）
 */
const ChatPage: React.FC = () => {
  const { mode } = useParams<{ mode: string }>();
  const location = useLocation();
  
  // 正确从 store 中解构状态和方法
  const { histories, isLoading, addMessage, updateLastMessage, setLoading, clearHistory } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  /**
   * 根据当前路径判断聊天模式
   */
  const currentMode: ChatMode = (() => {
    if (location.pathname.includes('/image')) return 'image';
    if (location.pathname.includes('/audio')) return 'audio';
    if (location.pathname.includes('/pdf')) return 'pdf';
    return 'qa';
  })();

  // 获取当前模式的消息列表
  const messages = histories[currentMode] || [];

  // 模式切换时清空消息 (可选，根据需求决定是否保留历史)
  // 如果希望保留历史，可以注释掉这个 useEffect
  // useEffect(() => {
  //   clearHistory(currentMode);
  // }, [currentMode, clearHistory]);

  // 消息更新时自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  /**
   * 发送消息处理函数
   * @param content 用户输入的文本内容
   * @param files 用户上传的文件列表
   */
  const handleSendMessage = async (content: string, files: File[]) => {
    if (!content.trim() && files.length === 0) return;

    // 添加用户消息到界面
    const userMessage = {
      role: 'user' as const,
      content,
      files: files.map(f => ({
        name: f.name,
        type: f.type,
        url: URL.createObjectURL(f)
      }))
    };
    // 调用 store 方法需传入 currentMode
    addMessage(currentMode, userMessage);

    // 准备文件对象
    let image_file: File | undefined;
    let audio_file: File | undefined;
    let pdf_file: File | undefined;

    if (files.length > 0) {
      const file = files[0];
      if (file.type.startsWith('image/')) image_file = file;
      else if (file.type.startsWith('audio/')) audio_file = file;
      else if (file.type === 'application/pdf') pdf_file = file;
    }

    // 添加初始助手消息占位符
    setLoading(true);
    addMessage(currentMode, {
      role: 'assistant',
      content: ''
    });

    try {
      // 调用流式聊天服务
      await streamChat(
        {
          content_blocks: [{ type: 'text', content }],
          history: messages.map(m => ({
            role: m.role,
            content: m.content,
            content_blocks: [{ type: 'text', content: m.content }] // 简化的历史记录格式
          })),
          image_file,
          audio_file,
          pdf_file
        },
        (chunk) => {
          updateLastMessage(currentMode, chunk); // 实时更新消息内容
        },
        (fullContent) => {
          updateLastMessage(currentMode, fullContent); // 完成时更新完整内容
          setLoading(false);
        },
        (error) => {
          console.error(error);
          updateLastMessage(currentMode, '抱歉，出错了，请稍后重试。');
          setLoading(false);
        }
      );
    } catch (error) {
      console.error(error);
      setLoading(false);
    }
  };

  /**
   * 获取页面标题
   */
  const getPageTitle = () => {
    switch (currentMode) {
      case 'qa': return '智能问答';
      case 'image': return '图片分析';
      case 'audio': return '音频转写';
      case 'pdf': return 'PDF解析';
      default: return '智能问答';
    }
  };

  return (
    <Layout title={getPageTitle()}>
      <div className="flex flex-col h-full">
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <Empty mode={currentMode} />
          ) : (
            messages.map((msg, index) => (
              <MessageBubble key={index} message={msg} />
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
               <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
               </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <div className="p-4 bg-white border-t border-gray-200">
          <ChatInput 
            onSend={handleSendMessage} 
            mode={currentMode}
            disabled={isLoading} 
          />
        </div>
      </div>
    </Layout>
  );
};

export default ChatPage;
