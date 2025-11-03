'use client'

import { useEffect, useState } from 'react'
import { useCharacterStore } from '@/lib/stores/characterStore'
import { fetchCharacters } from '@/lib/services/api'
import { Character } from '@/lib/types/character'

interface CharacterSelectorProps {
  selectedCharacter: string | null
  onSelectCharacter: (characterName: string) => void
}

export default function CharacterSelector({ selectedCharacter, onSelectCharacter }: CharacterSelectorProps) {
  const { characters, setCharacters, setLoading, setError } = useCharacterStore()
  const [isOpen, setIsOpen] = useState(false)
  
  useEffect(() => {
    loadCharacters()
  }, [])
  
  const loadCharacters = async () => {
    setLoading(true)
    try {
      const response = await fetchCharacters()
      setCharacters(response.characters)
      setError(null)
    } catch (error) {
      console.error('Error loading characters:', error)
      setError('Failed to load characters')
    } finally {
      setLoading(false)
    }
  }
  
  const handleSelect = (character: Character) => {
    onSelectCharacter(character.name)
    setIsOpen(false)
  }
  
  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="rounded-lg border bg-background px-4 py-2 text-sm font-medium hover:bg-accent transition-colors"
      >
        {selectedCharacter || 'Select Character'}
      </button>
      
      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 top-full mt-2 w-64 rounded-lg border bg-popover p-2 shadow-lg z-20">
            {characters.length === 0 ? (
              <div className="px-4 py-3 text-sm text-muted-foreground">
                No characters found
              </div>
            ) : (
              <div className="space-y-1">
                {characters.map((character) => (
                  <button
                    key={character.id}
                    onClick={() => handleSelect(character)}
                    className="w-full rounded-md px-4 py-3 text-left hover:bg-accent transition-colors"
                  >
                    <div className="font-medium">{character.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {character.race} {character.character_class} • Level {character.level}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}
