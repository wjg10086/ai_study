import { cn } from '@/lib/utils'
import { ChatMode } from '../modules/chat/types'

interface EmptyProps {
  mode?: ChatMode;
}

// Empty component
export default function Empty({ mode }: EmptyProps) {
  return (
    <div className={cn('flex h-full items-center justify-center')}>Empty {mode}</div>
  )
}
