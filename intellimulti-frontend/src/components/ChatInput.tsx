import React, { useState, useRef } from 'react';
import { Input, Button } from 'antd';
import { Send, Paperclip, X } from 'lucide-react';
import { ChatMode } from '../modules/chat/types';

const { TextArea } = Input;

interface ChatInputProps {
  onSend: (text: string, files: File[]) => void;
  mode: ChatMode;
  disabled: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ 
  onSend, 
  mode,
  disabled
}) => {
  const [text, setText] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const getAcceptType = () => {
    switch (mode) {
      case 'image': return 'image/*';
      case 'audio': return 'audio/*';
      case 'pdf': return '.pdf';
      default: return undefined;
    }
  };

  const allowUpload = mode !== 'qa';

  const handleSend = () => {
    if ((!text.trim() && files.length === 0) || disabled) return;
    onSend(text, files);
    setText('');
    setFiles([]);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(Array.from(e.target.files));
    }
    // Reset value so same file can be selected again
    e.target.value = '';
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="border-t p-4 bg-white">
      {files.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-2 animate-fade-in">
          {files.map((file, index) => (
            <div key={index} className="flex items-center gap-2 bg-gray-100 p-2 rounded w-fit text-sm">
              <Paperclip size={14} />
              <span className="max-w-xs truncate">{file.name}</span>
              <button onClick={() => removeFile(index)} className="text-gray-500 hover:text-red-500">
                <X size={14} />
              </button>
            </div>
          ))}
        </div>
      )}
      
      <div className="flex gap-2 items-end">
        {allowUpload && (
          <>
            <input 
              type="file" 
              ref={fileInputRef} 
              className="hidden" 
              accept={getAcceptType()} 
              onChange={handleFileChange}
            />
            <Button 
              icon={<Paperclip size={18} />} 
              onClick={() => fileInputRef.current?.click()}
              className="flex-shrink-0 mb-1"
            />
          </>
        )}
        
        <TextArea
          value={text}
          onChange={e => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入您的问题..."
          autoSize={{ minRows: 1, maxRows: 4 }}
          className="flex-1"
          disabled={disabled}
        />
        
        <Button 
          type="primary" 
          icon={<Send size={16} />} 
          onClick={handleSend}
          loading={disabled}
          disabled={!text.trim() && files.length === 0}
          className="flex-shrink-0 mb-1 bg-blue-600 hover:bg-blue-500"
        >
          发送
        </Button>
      </div>
    </div>
  );
};

export default ChatInput;
