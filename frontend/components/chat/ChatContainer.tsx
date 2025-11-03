'use client'

import { useEffect, useRef, useState } from 'react'
import { useChatStore } from '@/lib/stores/chatStore'
import { useMetadataStore } from '@/lib/stores/metadataStore'
import { websocketService } from '@/lib/services/websocket'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import { Message } from '@/lib/types/conversation'
import { getConversationByCharacter, saveConversation, createConversation } from '@/lib/services/localStorage'

interface ChatContainerProps {
  characterName: string
}

export default function ChatContainer({ characterName }: ChatContainerProps) {
  const { messages, addMessage, startStreaming, appendToStreamingMessage, completeStreaming, setError, clearMessages } = useChatStore()
  const { updateCurrentMetadata, saveMessageMetadata, clearCurrentMetadata } = useMetadataStore()
  const [isConnecting, setIsConnecting] = useState(true)
  const conversationIdRef = useRef<string | null>(null)
  const currentMessageIdRef = useRef<string | null>(null)
  
  useEffect(() => {
    // Load conversation history from localStorage
    const characterId = characterName.toLowerCase().replace(/\s+/g, '-')
    let conversation = getConversationByCharacter(characterId)
    
    if (!conversation) {
      conversation = createConversation(characterId, characterName)
      saveConversation(conversation)
    }
    
    conversationIdRef.current = conversation.id
    
    // Load messages into store
    clearMessages()
    conversation.messages.forEach(msg => addMessage(msg))
    
    // Connect WebSocket
    const connect = async () => {
      try {
        await websocketService.connect()
        setIsConnecting(false)
        
        // Set up message handlers
        websocketService.onMessage((chunk) => {
          appendToStreamingMessage(chunk)
        })
        
        websocketService.onComplete(() => {
          completeStreaming()
        })
        
        websocketService.onError((error) => {
          setError(error)
        })
        
        // Set up metadata handler
        websocketService.onMetadata((type, data) => {
          console.log(`Received metadata: ${type}`, data)
          
          switch (type) {
            case 'routing_metadata':
              updateCurrentMetadata({ routing: data })
              break
            case 'entities_metadata':
              updateCurrentMetadata({ entities: data })
              break
            case 'context_sources':
              updateCurrentMetadata({ sources: data })
              break
            case 'performance_metrics':
              updateCurrentMetadata({ performance: data })
              // Save complete metadata when performance arrives (last event)
              if (currentMessageIdRef.current) {
                const currentMetadata = useMetadataStore.getState().currentMetadata
                if (currentMetadata) {
                  saveMessageMetadata(currentMessageIdRef.current, currentMetadata)
                }
              }
              break
          }
        })
      } catch (error) {
        console.error('Failed to connect:', error)
        setError('Failed to connect to server')
        setIsConnecting(false)
      }
    }
    
    connect()
    
    return () => {
      websocketService.disconnect()
    }
  }, [characterName])
  
  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (conversationIdRef.current && messages.length > 0) {
      const characterId = characterName.toLowerCase().replace(/\s+/g, '-')
      const conversation = getConversationByCharacter(characterId)
      if (conversation) {
        conversation.messages = messages
        conversation.updatedAt = new Date()
        saveConversation(conversation)
      }
    }
  }, [messages, characterName])
  
  const handleSendMessage = async (content: string) => {
    if (!websocketService.isConnected()) {
      setError('Not connected to server')
      return
    }
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date()
    }
    addMessage(userMessage)
    
    // Clear previous metadata and start streaming assistant response
    clearCurrentMetadata()
    startStreaming()
    
    // Store message ID for metadata association
    currentMessageIdRef.current = (Date.now() + 1).toString()
    
    try {
      websocketService.sendMessage(content, characterName)
    } catch (error) {
      console.error('Error sending message:', error)
      setError('Failed to send message')
    }
  }
  
  if (isConnecting) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Connecting...</p>
        </div>
      </div>
    )
  }
  
  return (
    <div className="flex h-full flex-col">
      <MessageList />
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  )
}
