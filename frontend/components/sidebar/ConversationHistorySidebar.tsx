/**
 * Conversation History Sidebar - Shows past conversations and navigation
 */
'use client';

import { MessageSquare, Plus, Wand2 } from 'lucide-react';
import { useState } from 'react';

interface ConversationHistorySidebarProps {
  characterName: string;
}

export function ConversationHistorySidebar({ characterName }: ConversationHistorySidebarProps) {
  const [conversations] = useState([
    { id: '1', preview: 'What is my AC?', timestamp: new Date() },
    { id: '2', preview: 'Tell me about my spells', timestamp: new Date(Date.now() - 86400000) },
  ]);

  return (
    <div className="w-80 border-r border-border bg-card p-4 flex flex-col h-full">
      {/* Header with actions */}
      <div className="space-y-3 mb-6">
        <button
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
        
        <div className="space-y-2">
          {conversations.map((conv) => (
            <button
              key={conv.id}
              className="w-full text-left p-3 rounded-lg hover:bg-muted transition-colors group"
            >
              <div className="flex items-start gap-2">
                <MessageSquare className="w-4 h-4 mt-0.5 flex-shrink-0 text-muted-foreground group-hover:text-foreground" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm truncate">{conv.preview}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {formatTimestamp(conv.timestamp)}
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
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
