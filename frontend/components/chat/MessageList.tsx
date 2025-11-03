'use client'

import { useEffect, useRef } from 'react'
import { useChatStore } from '@/lib/stores/chatStore'
import MessageBubble from './MessageBubble'

export default function MessageList() {
  const { messages, isStreaming, currentStreamingMessage, error } = useChatStore()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [messages, currentStreamingMessage])
  
  return (
    <div className="h-full overflow-y-auto p-4 space-y-4">
      {messages.length === 0 && !isStreaming && (
        <div className="flex h-full items-center justify-center">
          <div className="text-center text-muted-foreground">
            <p className="text-lg">No messages yet</p>
            <p className="text-sm mt-2">Start a conversation by typing a message below</p>
          </div>
        </div>
      )}
      
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      
      {isStreaming && currentStreamingMessage && (
        <MessageBubble 
          message={{
            id: 'streaming',
            role: 'assistant',
            content: currentStreamingMessage,
            timestamp: new Date()
          }}
          isStreaming
        />
      )}
      
      {error && (
        <div className="rounded-lg bg-destructive/10 border border-destructive p-4 text-destructive">
          <p className="font-semibold">Error</p>
          <p className="text-sm">{error}</p>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  )
}
