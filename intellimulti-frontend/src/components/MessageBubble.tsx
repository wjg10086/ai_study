import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { User, Bot, FileText, Music } from 'lucide-react';
import clsx from 'clsx';
import { Message } from '@/modules/chat/types';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={clsx("flex gap-3 mb-4", isUser ? "flex-row-reverse" : "flex-row")}>
      <div className={clsx(
        "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
        isUser ? "bg-blue-500 text-white" : "bg-emerald-600 text-white"
      )}>
        {isUser ? <User size={18} /> : <Bot size={18} />}
      </div>
      
      <div className={clsx(
        "max-w-[80%] rounded-lg p-3 text-sm overflow-hidden",
        isUser ? "bg-blue-50 text-gray-800 border border-blue-100" : "bg-gray-50 text-gray-800 border border-gray-200"
      )}>
        {/* Render content blocks for user if any */}
        {isUser && message.content_blocks && message.content_blocks.length > 0 && (
          <div className="mb-2 space-y-2">
            {message.content_blocks.map((block, idx) => {
              if (block.type === 'image' && block.content) {
                return <img key={idx} src={block.content} alt="Uploaded" className="max-h-60 rounded border border-gray-200" />;
              }
              if (block.type === 'audio') {
                return (
                  <div key={idx} className="flex items-center gap-2 bg-gray-100 p-2 rounded">
                    <Music size={16} />
                    <span>Audio Uploaded</span>
                  </div>
                );
              }
              if (block.type === 'text' && block.content && block.content.startsWith('data:application/pdf')) {
                // This logic depends on how we store PDF content in blocks, 
                // but usually we just upload file and don't store base64 in block unless needed for preview.
                // Here we just show a placeholder if detected
                return (
                  <div key={idx} className="flex items-center gap-2 bg-gray-100 p-2 rounded">
                    <FileText size={16} />
                    <span>PDF Uploaded</span>
                  </div>
                );
              }
              return null;
            })}
          </div>
        )}

        <div className="prose prose-sm max-w-none break-words">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        </div>
        
        {/* PDF References */}
        {/* If message has references, display them */}
      </div>
    </div>
  );
};

export default MessageBubble;
