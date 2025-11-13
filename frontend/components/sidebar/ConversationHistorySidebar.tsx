/**
 * Conversation History Sidebar - Shows past conversations and navigation
 */
'use client';

import { MessageSquare, Plus, Wand2, Trash2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { getConversations, deleteConversation, createConversation, saveConversation } from '@/lib/services/localStorage';
import { Conversation } from '@/lib/types/conversation';

interface ConversationHistorySidebarProps {
  characterName: string;
  onConversationSelect?: (conversationId: string) => void;
  onNewConversation?: () => void;
}

export function ConversationHistorySidebar({ characterName, onConversationSelect, onNewConversation }: ConversationHistorySidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null);

  // Load conversations for the current character
  useEffect(() => {
    const loadConversations = () => {
      const allConversations = getConversations();
      const characterId = characterName.toLowerCase().replace(/\s+/g, '-');
      const characterConversations = allConversations
        .filter(conv => conv.characterId === characterId)
        .sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime());
      setConversations(characterConversations);
      
      // Auto-select the most recent conversation if none selected
      if (characterConversations.length > 0 && !selectedConversationId) {
        setSelectedConversationId(characterConversations[0].id);
      }
    };

    loadConversations();

    // Poll for updates (in case conversations are modified elsewhere)
    const interval = setInterval(loadConversations, 1000);
    return () => clearInterval(interval);
  }, [characterName, selectedConversationId]);

  const handleNewConversation = () => {
    onNewConversation?.();
    // Reload conversations after a brief delay to see the new one
    setTimeout(() => {
      const allConversations = getConversations();
      const characterId = characterName.toLowerCase().replace(/\s+/g, '-');
      const characterConversations = allConversations
        .filter(conv => conv.characterId === characterId)
        .sort((a, b) => b.updatedAt.getTime() - a.updatedAt.getTime());
      setConversations(characterConversations);
    }, 100);
  };

  const handleSelectConversation = (conversationId: string) => {
    setSelectedConversationId(conversationId);
    onConversationSelect?.(conversationId);
  };

  const handleDeleteConversation = (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this conversation?')) {
      deleteConversation(conversationId);
      setConversations(prev => prev.filter(conv => conv.id !== conversationId));
      if (selectedConversationId === conversationId) {
        setSelectedConversationId(null);
      }
    }
  };

  const getConversationPreview = (conv: Conversation): string => {
    const userMessages = conv.messages.filter(m => m.role === 'user');
    if (userMessages.length === 0) return 'New conversation';
    return userMessages[0].content.substring(0, 50);
  };

  return (
    <div className="w-80 border-r border-border bg-card p-4 flex flex-col h-full">
      {/* Header with actions */}
      <div className="space-y-3 mb-6">
        <button
          onClick={handleNewConversation}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity font-medium"
        >
          <Plus className="w-4 h-4" />
          New Conversation
        </button>
        
        <button
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 border border-border rounded-lg hover:bg-muted transition-colors"
          disabled
        >
          <Wand2 className="w-4 h-4" />
          Character Wizard
          <span className="text-xs text-muted-foreground ml-auto">(Soon)</span>
        </button>
      </div>

      {/* Conversations list */}
      <div className="flex-1 overflow-y-auto">
        <div className="text-sm font-medium text-muted-foreground mb-3">
          Recent Conversations
        </div>
        
        {conversations.length === 0 ? (
          <div className="text-sm text-muted-foreground text-center py-8">
            No conversations yet. Start chatting to create one!
          </div>
        ) : (
          <div className="space-y-2">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => handleSelectConversation(conv.id)}
                className={`w-full text-left p-3 rounded-lg hover:bg-muted transition-colors group relative ${
                  selectedConversationId === conv.id ? 'bg-muted' : ''
                }`}
              >
                <div className="flex items-start gap-2">
                  <MessageSquare className="w-4 h-4 mt-0.5 flex-shrink-0 text-muted-foreground group-hover:text-foreground" />
                  <div className="flex-1 min-w-0 pr-6">
                    <div className="text-sm truncate">{getConversationPreview(conv)}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {formatTimestamp(conv.updatedAt)}
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDeleteConversation(conv.id, e)}
                    className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 rounded transition-opacity"
                    title="Delete conversation"
                  >
                    <Trash2 className="w-3 h-3 text-destructive" />
                  </button>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Character info footer */}
      <div className="pt-4 border-t border-border mt-auto">
        <div className="text-xs text-muted-foreground">Current Character</div>
        <div className="text-sm font-medium mt-1 truncate">{characterName}</div>
      </div>
    </div>
  );
}

function formatTimestamp(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  
  if (days === 0) return 'Today';
  if (days === 1) return 'Yesterday';
  if (days < 7) return `${days} days ago`;
  return date.toLocaleDateString();
}
