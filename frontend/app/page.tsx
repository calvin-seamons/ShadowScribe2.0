'use client'

import { useEffect, useState } from 'react'
import ChatContainer from '@/components/chat/ChatContainer'
import CharacterSelector from '@/components/character/CharacterSelector'
import { LogoText } from '@/components/Logo'
import { ConversationHistorySidebar } from '@/components/sidebar/ConversationHistorySidebar'
import { MetadataSidebar } from '@/components/sidebar/MetadataSidebar'
import { useMetadataStore } from '@/lib/stores/metadataStore'
import { Eye, EyeOff, Plus } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  const [selectedCharacter, setSelectedCharacter] = useState<string | null>(null)
  const { sidebarVisible, toggleSidebar } = useMetadataStore()

  return (
    <main className="flex min-h-screen flex-col">
      <header className="border-b border-border bg-card shadow-sm">
        <div className="container mx-auto flex items-center justify-between p-4">
          <LogoText />
          <div className="flex items-center gap-4">
            {selectedCharacter && (
              <button
                onClick={toggleSidebar}
                className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border hover:bg-muted transition-colors text-sm"
                title={sidebarVisible ? 'Hide metadata' : 'Show metadata'}
              >
                {sidebarVisible ? (
                  <>
                    <EyeOff className="w-4 h-4" />
                    Hide Analysis
                  </>
                ) : (
                  <>
                    <Eye className="w-4 h-4" />
                    Show Analysis
                  </>
                )}
              </button>
            )}
            <Link
              href="/characters/create"
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gradient-to-r from-primary to-accent text-primary-foreground hover:opacity-90 transition-opacity text-sm font-medium shadow-sm"
              title="Create new character"
            >
              <Plus className="w-4 h-4" />
              Create Character
            </Link>
            <CharacterSelector 
              selectedCharacter={selectedCharacter}
              onSelectCharacter={setSelectedCharacter}
            />
          </div>
        </div>
      </header>
      
      <div className="flex-1 flex overflow-hidden">
        {selectedCharacter ? (
          <>
            {/* Left sidebar - Conversation history */}
            <ConversationHistorySidebar characterName={selectedCharacter} />
            
            {/* Center - Chat */}
            <div className="flex-1 overflow-hidden">
              <ChatContainer characterName={selectedCharacter} />
            </div>
            
            {/* Right sidebar - Metadata */}
            {sidebarVisible && <MetadataSidebar />}
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center space-y-4">
              <h2 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Welcome to ShadowScribe
              </h2>
              <p className="text-muted-foreground text-lg">
                Your AI-powered D&D companion
              </p>
              <p className="text-sm text-muted-foreground max-w-md mx-auto">
                Select a character above to begin your adventure. ShadowScribe provides 
                intelligent answers about your character, rulebook rules, and campaign history.
              </p>
              <Link
                href="/characters/create"
                className="inline-flex items-center gap-2 px-6 py-3 mt-4 rounded-lg bg-gradient-to-r from-primary to-accent text-primary-foreground hover:opacity-90 transition-opacity font-medium shadow-md"
              >
                <Plus className="w-5 h-5" />
                Create Your First Character
              </Link>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
