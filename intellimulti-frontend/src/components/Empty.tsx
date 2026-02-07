import { cn } from '@/lib/utils'
import { ChatMode } from '../modules/chat/types'
import { MessageSquare, Image as ImageIcon, Mic, FileText, Sparkles } from 'lucide-react'
import { Typography } from 'antd'

const { Title, Text } = Typography

interface EmptyProps {
  mode?: ChatMode;
}

const modeConfig = {
  qa: {
    icon: <MessageSquare size={48} className="text-blue-500/50" />,
    title: '智能问答',
    desc: '您可以向我提问任何问题，我会尽力为您解答。'
  },
  image: {
    icon: <ImageIcon size={48} className="text-green-500/50" />,
    title: '图片分析',
    desc: '上传图片，我可以帮您分析图片中的内容、文字或场景。'
  },
  audio: {
    icon: <Mic size={48} className="text-purple-500/50" />,
    title: '音频转写',
    desc: '上传音频文件，我可以将其转录为文字并回答相关问题。'
  },
  pdf: {
    icon: <FileText size={48} className="text-red-500/50" />,
    title: 'PDF 解析',
    desc: '上传 PDF 文档，我可以基于文档内容进行深度解析和问答。'
  }
}

// Empty component
export default function Empty({ mode = 'qa' }: EmptyProps) {
  const config = modeConfig[mode as keyof typeof modeConfig] || modeConfig.qa

  return (
    <div className={cn('flex h-full flex-col items-center justify-center p-8 text-center animate-fade-in')}>
      <div className="relative mb-6">
        <div className="absolute -inset-4 rounded-full bg-gray-50 blur-xl" />
        <div className="relative flex h-20 w-20 items-center justify-center rounded-2xl bg-white shadow-sm ring-1 ring-gray-100">
          {config.icon}
        </div>
        <Sparkles className="absolute -right-2 -top-2 h-6 w-6 text-yellow-400 animate-pulse" />
      </div>
      
      <Title level={3} className="mb-2 !text-gray-800">
        {config.title}
      </Title>
      
      <Text className="max-w-md text-gray-500 text-base leading-relaxed">
        {config.desc}
      </Text>

      <div className="mt-12 flex gap-4 text-xs text-gray-400 font-medium">
        <span className="flex items-center gap-1.5">
          <div className="h-1.5 w-1.5 rounded-full bg-blue-400" />
          多模态理解
        </span>
        <span className="flex items-center gap-1.5">
          <div className="h-1.5 w-1.5 rounded-full bg-green-400" />
          RAG 检索
        </span>
        <span className="flex items-center gap-1.5">
          <div className="h-1.5 w-1.5 rounded-full bg-purple-400" />
          实时响应
        </span>
      </div>
    </div>
  )
}
