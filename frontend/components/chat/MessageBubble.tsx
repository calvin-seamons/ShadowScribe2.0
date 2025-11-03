'use client'

import { Message } from '@/lib/types/conversation'
import { format } from 'date-fns'
import { cn } from '@/lib/utils'
import { MarkdownRenderer } from '@/components/markdown/MarkdownRenderer'

interface MessageBubbleProps {
  message: Message
  isStreaming?: boolean
}

export default function MessageBubble({ message, isStreaming = false }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  
  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div className={cn(
        'max-w-[80%] rounded-lg px-4 py-3',
        isUser 
          ? 'bg-primary text-primary-foreground' 
          : 'bg-muted text-muted-foreground'
      )}>
        {isUser ? (
          <div className="whitespace-pre-wrap">{message.content}</div>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <MarkdownRenderer content={message.content} />
            {isStreaming && (
              <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />
            )}
          </div>
        )}
        <div className={cn(
          'text-xs mt-2 opacity-70',
          isUser ? 'text-right' : 'text-left'
        )}>
          {format(message.timestamp, 'HH:mm')}
        </div>
      </div>
    </div>
  )
}
