/**
 * Demo component for useCharacterCreation hook
 * 
 * This component demonstrates all features of the useCharacterCreation hook:
 * - URL input and character creation
 * - Real-time parser progress display
 * - Error handling
 * - Character summary display
 * - Progress reset
 * 
 * To use this component, add it to a page:
 * ```tsx
 * import { CharacterCreationDemo } from '@/components/character/CharacterCreationDemo'
 * 
 * export default function Page() {
 *   return <CharacterCreationDemo />
 * }
 * ```
 */

'use client'

import { useState } from 'react'
import { useCharacterCreation } from '@/lib/hooks/useCharacterCreation'
import type { ParserName } from '@/lib/types/character'

const PARSER_LABELS: Record<ParserName, string> = {
  core: 'Core Stats & Abilities',
  inventory: 'Inventory & Equipment',
  spells: 'Spells & Spellcasting',
  features: 'Features & Traits',
  background: 'Backstory & Personality',
  actions: 'Actions & Attacks',
}

const PARSER_ICONS: Record<ParserName, string> = {
  core: '⚡',
  inventory: '🎒',
  spells: '✨',
  features: '🎖️',
  background: '📜',
  actions: '⚔️',
}

const STATUS_COLORS = {
  idle: 'bg-gray-200',
  started: 'bg-blue-300',
  in_progress: 'bg-blue-500',
  complete: 'bg-green-500',
  error: 'bg-red-500',
}

const STATUS_ICONS = {
  idle: '⚪',
  started: '🔵',
  in_progress: '🔵',
  complete: '✅',
  error: '❌',
}

export function CharacterCreationDemo() {
  const [url, setUrl] = useState('https://www.dndbeyond.com/characters/152248393')
  
  const {
    createCharacter,
    parsers,
    isCreating,
    error,
    characterId,
    characterSummary,
    progressEvents,
    resetProgress,
    completedCount,
    totalCount,
  } = useCharacterCreation()
  
  const handleCreate = async () => {
    if (!url.trim()) return
    
    try {
      await createCharacter(url)
    } catch (err) {
      console.error('Character creation failed:', err)
    }
  }
  
  const handleReset = () => {
    resetProgress()
    setUrl('https://www.dndbeyond.com/characters/152248393')
  }
  
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold mb-2">Character Creation Demo</h1>
        <p className="text-gray-600 mb-6">
          Test the useCharacterCreation hook with real-time WebSocket progress
        </p>
        
        {/* URL Input */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">
            D&D Beyond Character URL
          </label>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://dndbeyond.com/characters/152248393"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isCreating}
          />
          <div className="flex gap-3">
            <button
              onClick={handleCreate}
              disabled={isCreating || !url.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {isCreating ? 'Creating Character...' : 'Create Character'}
            </button>
            {(characterId || error) && (
              <button
                onClick={handleReset}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-medium"
              >
                Reset
              </button>
            )}
          </div>
        </div>
      </div>
      
      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <span className="text-2xl">❌</span>
            <div>
              <h3 className="font-bold text-red-800 mb-1">Creation Failed</h3>
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Progress Display */}
      {isCreating && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">Parsing Progress</h2>
            <div className="text-sm font-medium text-gray-600">
              {completedCount} / {totalCount} parsers complete
            </div>
          </div>
          
          <div className="space-y-3">
            {Object.values(parsers).map((parser) => (
              <div key={parser.parser} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{PARSER_ICONS[parser.parser]}</span>
                    <span className="font-medium">{PARSER_LABELS[parser.parser]}</span>
                    <span className="text-sm">{STATUS_ICONS[parser.status]}</span>
                  </div>
                  {parser.execution_time_ms && (
                    <span className="text-sm text-gray-600">
                      {parser.execution_time_ms.toFixed(2)}ms
                    </span>
                  )}
                </div>
                
                {/* Progress Bar */}
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-300 ${STATUS_COLORS[parser.status]}`}
                    style={{
                      width: parser.status === 'complete' 
                        ? '100%' 
                        : parser.status === 'started' || parser.status === 'in_progress'
                        ? '50%'
                        : '0%'
                    }}
                  />
                </div>
                
                {parser.message && (
                  <p className="text-sm text-gray-600 ml-8">{parser.message}</p>
                )}
              </div>
            ))}
          </div>
          
          {/* Overall Progress */}
          <div className="mt-6 pt-4 border-t">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Overall Progress</span>
              <span className="text-sm font-bold">
                {Math.round((completedCount / totalCount) * 100)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-green-500 transition-all duration-500"
                style={{ width: `${(completedCount / totalCount) * 100}%` }}
              />
            </div>
          </div>
        </div>
      )}
      
      {/* Character Summary */}
      {characterSummary && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="flex items-start gap-3 mb-4">
            <span className="text-3xl">🎉</span>
            <div>
              <h2 className="text-2xl font-bold text-green-800 mb-1">
                Character Created Successfully!
              </h2>
              <p className="text-green-700">Character ID: {characterId}</p>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4 bg-white rounded-lg p-4">
            <div>
              <span className="text-sm text-gray-600">Name</span>
              <p className="font-bold text-lg">{characterSummary.name}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Race</span>
              <p className="font-bold text-lg">{characterSummary.race}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Class</span>
              <p className="font-bold text-lg">{characterSummary.character_class}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Level</span>
              <p className="font-bold text-lg">{characterSummary.level}</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Hit Points</span>
              <p className="font-bold text-lg">{characterSummary.hp} HP</p>
            </div>
            <div>
              <span className="text-sm text-gray-600">Armor Class</span>
              <p className="font-bold text-lg">{characterSummary.ac} AC</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Event Log (Debug) */}
      {progressEvents.length > 0 && (
        <details className="bg-gray-50 rounded-lg p-4">
          <summary className="cursor-pointer font-medium text-gray-700">
            Event Log ({progressEvents.length} events)
          </summary>
          <div className="mt-3 space-y-1 max-h-64 overflow-y-auto">
            {progressEvents.map((event, index) => (
              <div key={index} className="text-xs font-mono bg-white p-2 rounded">
                <span className="text-gray-500">[{index + 1}]</span>{' '}
                <span className="font-bold">{event.type}</span>
                {event.type === 'parser_started' && ` - ${event.parser}`}
                {event.type === 'parser_complete' && 
                  ` - ${event.parser} (${event.execution_time_ms}ms)`}
                {event.type === 'fetch_complete' && ` - ${event.character_name}`}
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  )
}
