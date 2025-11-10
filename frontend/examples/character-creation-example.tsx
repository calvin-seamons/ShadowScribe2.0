/**
 * Example usage of WebSocketService for character creation
 * 
 * This example demonstrates how to use the extended WebSocketService
 * to create a character with real-time progress updates.
 */

import { websocketService } from '@/lib/services/websocket'
import type { CharacterCreationEvent, CharacterSummary } from '@/lib/types/character'
import { useEffect, useState } from 'react'

export function useCharacterCreationExample() {
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [progress, setProgress] = useState<CharacterCreationEvent[]>([])
  const [characterSummary, setCharacterSummary] = useState<CharacterSummary | null>(null)
  
  // Register progress handler
  useEffect(() => {
    websocketService.onProgress((event: CharacterCreationEvent) => {
      setProgress(prev => [...prev, event])
    })
  }, [])
  
  const createFromUrl = async (url: string) => {
    setIsCreating(true)
    setError(null)
    setProgress([])
    setCharacterSummary(null)
    
    try {
      const summary = await websocketService.createCharacter(url)
      setCharacterSummary(summary)
      setIsCreating(false)
      return summary
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setIsCreating(false)
      throw err
    }
  }
  
  const createFromJson = async (jsonData: any) => {
    setIsCreating(true)
    setError(null)
    setProgress([])
    setCharacterSummary(null)
    
    try {
      const summary = await websocketService.createCharacter(jsonData)
      setCharacterSummary(summary)
      setIsCreating(false)
      return summary
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setIsCreating(false)
      throw err
    }
  }
  
  return {
    isCreating,
    error,
    progress,
    characterSummary,
    createFromUrl,
    createFromJson
  }
}

// Example component using the hook
export function CharacterCreationExample() {
  const {
    isCreating,
    error,
    progress,
    characterSummary,
    createFromUrl
  } = useCharacterCreationExample()
  
  const [url, setUrl] = useState('')
  
  const handleCreate = async () => {
    if (!url) return
    try {
      await createFromUrl(url)
    } catch (err) {
      console.error('Character creation failed:', err)
    }
  }
  
  return (
    <div className="space-y-4">
      <div>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://dndbeyond.com/characters/152248393"
          className="w-full px-4 py-2 border rounded"
          disabled={isCreating}
        />
        <button
          onClick={handleCreate}
          disabled={isCreating || !url}
          className="mt-2 px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
        >
          {isCreating ? 'Creating...' : 'Create Character'}
        </button>
      </div>
      
      {error && (
        <div className="p-4 bg-red-100 text-red-700 rounded">
          Error: {error}
        </div>
      )}
      
      {progress.length > 0 && (
        <div className="space-y-2">
          <h3 className="font-bold">Progress:</h3>
          {progress.map((event, index) => (
            <div key={index} className="text-sm">
              {event.type === 'fetch_started' && '📥 Fetching character...'}
              {event.type === 'fetch_complete' && `✅ Fetched: ${event.character_name}`}
              {event.type === 'parser_started' && `▶️ Starting parser: ${event.parser}`}
              {event.type === 'parser_complete' && 
                `✅ Parser complete: ${event.parser} (${event.execution_time_ms}ms)`}
              {event.type === 'assembly_started' && '🔧 Assembling character...'}
            </div>
          ))}
        </div>
      )}
      
      {characterSummary && (
        <div className="p-4 bg-green-100 rounded">
          <h3 className="font-bold mb-2">Character Created!</h3>
          <div className="space-y-1">
            <p>Name: {characterSummary.name}</p>
            <p>Race: {characterSummary.race}</p>
            <p>Class: {characterSummary.character_class}</p>
            <p>Level: {characterSummary.level}</p>
            <p>HP: {characterSummary.hp}</p>
            <p>AC: {characterSummary.ac}</p>
          </div>
        </div>
      )}
    </div>
  )
}
