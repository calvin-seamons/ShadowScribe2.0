'use client'

import { useEffect, useRef, useState } from 'react'
import { useChatStore } from '@/lib/stores/chatStore'
import { useMetadataStore } from '@/lib/stores/metadataStore'
import { websocketService } from '@/lib/services/websocket'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import { Message } from '@/lib/types/conversation'
import { getConversationByCharacter, getConversationById, saveConversation, createConversation } from '@/lib/services/localStorage'

interface ChatContainerProps {
  characterName: string
  conversationId?: string | null
  onConversationCreated?: (conversationId: string) => void
}

export default function ChatContainer({ characterName, conversationId, onConversationCreated }: ChatContainerProps) {
  const { messages, addMessage, startStreaming, appendToStreamingMessage, completeStreaming, setError, clearMessages, clearHistory, setMessages } = useChatStore()
  const { updateCurrentMetadata, saveMessageMetadata, clearCurrentMetadata } = useMetadataStore()
  const [isConnecting, setIsConnecting] = useState(true)
  const [connectionError, setConnectionError] = useState<string | null>(null)
  const [retryCount, setRetryCount] = useState(0)
  const conversationIdRef = useRef<string | null>(null)
  const currentMessageIdRef = useRef<string | null>(null)
  
  // Load or create conversation when component mounts or conversationId changes
  useEffect(() => {
    const characterId = characterName.toLowerCase().replace(/\s+/g, '-')
    const chatStore = useChatStore.getState()
    
    if (conversationId) {
      // Load existing conversation by ID
      const conversation = getConversationById(conversationId)
      if (conversation) {
        conversationIdRef.current = conversation.id
        chatStore.setMessages(conversation.messages)
        return
      }
    }
    
    // Create new conversation if none specified or not found
    const conversation = createConversation(characterId, characterName)
    saveConversation(conversation)
    conversationIdRef.current = conversation.id
    chatStore.clearMessages()
    onConversationCreated?.(conversation.id)
  }, [conversationId, characterName, onConversationCreated])
  
  useEffect(() => {
    // Connect WebSocket
    const connect = async () => {
      try {
        setIsConnecting(true)
        setConnectionError(null)
        console.log('Attempting to connect WebSocket...')
        
        // Give it more time on first attempt
        const maxWaitTime = retryCount === 0 ? 10000 : 5000
        const connectionPromise = websocketService.connect()
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Connection timeout')), maxWaitTime)
        )
        
        await Promise.race([connectionPromise, timeoutPromise])
        
        console.log('WebSocket connected successfully!')
        setIsConnecting(false)
        setRetryCount(0) // Reset retry count on success
        
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
        console.error('Failed to connect WebSocket:', error)
        const errorMessage = error instanceof Error ? error.message : 'Unknown error'
        
        // Only show error after a few retries (give WebSocket time to establish)
        setRetryCount(prev => prev + 1)
        
        if (retryCount < 2) {
          // Retry silently without showing error
          console.log(`Silent retry attempt ${retryCount + 1}...`)
          setTimeout(() => connect(), 1000)
        } else {
          // After retries, show error
          setConnectionError(`Failed to connect to server: ${errorMessage}. Please check if the backend is running.`)
          setIsConnecting(false)
        }
      }
    }
    
    connect()
    
    return () => {
      websocketService.disconnect()
    }
  }, [characterName])
  
  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (conversationIdRef.current) {
      const conversation = getConversationById(conversationIdRef.current)
      if (conversation) {
        // Only save if messages actually changed
        const messagesChanged = JSON.stringify(conversation.messages) !== JSON.stringify(messages)
        if (messagesChanged) {
          conversation.messages = messages
          conversation.updatedAt = new Date()
          saveConversation(conversation)
        }
      }
    }
  }, [messages])
  
  const clearConversation = async () => {
    if (!websocketService.isConnected()) {
      setError('Not connected to server')
      return
    }
    
    try {
      // Clear backend conversation history
      await websocketService.clearHistory(characterName)
      
      // Clear frontend state using store directly
      const chatStore = useChatStore.getState()
      chatStore.clearHistory()
      
      // Create new conversation in localStorage
      const characterId = characterName.toLowerCase().replace(/\s+/g, '-')
      const conversation = createConversation(characterId, characterName)
      saveConversation(conversation)
      conversationIdRef.current = conversation.id
      
      // Clear metadata
      clearCurrentMetadata()
      
      // Notify parent about new conversation
      onConversationCreated?.(conversation.id)
    } catch (error) {
      console.error('Error clearing conversation:', error)
      setError('Failed to clear conversation')
    }
  }
  
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
          <p className="text-muted-foreground">Connecting to server...</p>
        </div>
      </div>
    )
  }

  if (connectionError) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h3 className="text-xl font-bold text-red-600 mb-2">Connection Error</h3>
          <p className="text-muted-foreground mb-4">{connectionError}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity"
          >
            Retry Connection
          </button>
        </div>
      </div>
    )
  }
  
  return (
    <div className="h-full flex flex-col">
      <div className="flex-shrink-0 border-b border-border p-3">
        <button
          onClick={clearConversation}
          className="px-4 py-2 text-sm rounded-lg border border-border hover:bg-muted transition-colors"
          disabled={isConnecting || messages.length === 0}
        >
          New Conversation
        </button>
      </div>
      <div className="flex-1 overflow-hidden">
        <MessageList />
      </div>
      <div className="flex-shrink-0">
        <MessageInput onSendMessage={handleSendMessage} />
      </div>
    </div>
  )
}
