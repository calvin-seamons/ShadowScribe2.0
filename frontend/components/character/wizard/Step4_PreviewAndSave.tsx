/**
 * Step 4: Preview & Save
 * 
 * Final preview of character with save to database
 */

'use client'

import { useState } from 'react'
import type { CharacterData } from '@/lib/types/character'

interface Step4_PreviewAndSaveProps {
  characterData: CharacterData | null
  savedCharacterId: number | null
  onSave: () => Promise<void>
  onReset: () => void
}

export function Step4_PreviewAndSave({
  characterData,
  savedCharacterId,
  onSave,
  onReset,
}: Step4_PreviewAndSaveProps) {
  const [isSaving, setIsSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)
  
  const handleSave = async () => {
    setIsSaving(true)
    setSaveError(null)
    try {
      await onSave()
    } catch (error) {
      setSaveError(error instanceof Error ? error.message : 'Failed to save character')
    } finally {
      setIsSaving(false)
    }
  }
  
  if (!characterData) {
    return (
      <div className="p-8 text-center">
        <p className="text-gray-600">No character data available</p>
      </div>
    )
  }
  
  // If character is already saved, show success state
  if (savedCharacterId) {
    return (
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-8">
            <div className="mb-4">
              <span className="text-6xl">🎉</span>
            </div>
            <h2 className="text-4xl font-bold text-green-600 mb-2">Character Saved Successfully!</h2>
            <p className="text-gray-600 text-lg">
              Your character has been saved to the database
            </p>
          </div>
          
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-8">
            <div className="text-center">
              <p className="text-green-800 font-bold text-lg mb-2">Character ID: {savedCharacterId}</p>
              <p className="text-green-700">
                {characterData.character_base?.name || 'Your character'} is now ready to use!
              </p>
            </div>
          </div>
          
          <div className="flex flex-col gap-4">
            <a
              href={`/characters/${savedCharacterId}`}
              className="px-6 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 font-bold text-lg transition-all transform hover:scale-105 active:scale-95 text-center"
            >
              View Character Details →
            </a>
            <button
              onClick={onReset}
              className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 font-medium transition-colors"
            >
              Import Another Character
            </button>
          </div>
        </div>
      </div>
    )
  }
  
  // Otherwise show preview and save UI
  const charBase = characterData.character_base
  const abilityScores = characterData.ability_scores
  const combatStats = characterData.combat_stats
  const inventory = characterData.inventory
  const spellList = characterData.spell_list
  const backstory = characterData.backstory
  const personality = characterData.personality
  
  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Character Preview</h2>
          <p className="text-gray-600">Review your character before saving to the database</p>
        </div>
        
        {/* Error Display */}
        {saveError && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <span className="text-red-600 text-xl">⚠️</span>
              <div>
                <h3 className="font-bold text-red-800">Save Failed</h3>
                <p className="text-red-700">{saveError}</p>
              </div>
            </div>
          </div>
        )}
        
        {/* Character Summary Card */}
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-8 mb-8 border-2 border-purple-200">
          <div className="text-center mb-6">
            <h3 className="text-4xl font-bold text-gray-900 mb-2">
              {charBase?.name || 'Unknown Character'}
            </h3>
            <p className="text-xl text-gray-700">
              {charBase?.race && charBase?.character_class
                ? `${charBase.race} ${charBase.character_class}`
                : 'Unknown Race/Class'}
            </p>
          </div>
          
          {/* Core Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg p-4 text-center border border-gray-200">
              <span className="text-sm text-gray-600 block mb-1">Level</span>
              <span className="text-3xl font-bold text-purple-600">
                {charBase?.total_level || '?'}
              </span>
            </div>
            <div className="bg-white rounded-lg p-4 text-center border border-gray-200">
              <span className="text-sm text-gray-600 block mb-1">Hit Points</span>
              <span className="text-3xl font-bold text-red-600">
                {combatStats?.current_hp || '?'}/{combatStats?.max_hp || '?'}
              </span>
            </div>
            <div className="bg-white rounded-lg p-4 text-center border border-gray-200">
              <span className="text-sm text-gray-600 block mb-1">Armor Class</span>
              <span className="text-3xl font-bold text-blue-600">
                {combatStats?.armor_class || '?'}
              </span>
            </div>
            <div className="bg-white rounded-lg p-4 text-center border border-gray-200">
              <span className="text-sm text-gray-600 block mb-1">Initiative</span>
              <span className="text-3xl font-bold text-green-600">
                {combatStats?.initiative_bonus !== undefined
                  ? combatStats.initiative_bonus >= 0
                    ? `+${combatStats.initiative_bonus}`
                    : combatStats.initiative_bonus
                  : '?'}
              </span>
            </div>
          </div>
          
          {/* Ability Scores */}
          {abilityScores && (
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <h4 className="font-bold text-gray-900 mb-3 text-center">Ability Scores</h4>
              <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                {[
                  { label: 'STR', value: abilityScores.strength },
                  { label: 'DEX', value: abilityScores.dexterity },
                  { label: 'CON', value: abilityScores.constitution },
                  { label: 'INT', value: abilityScores.intelligence },
                  { label: 'WIS', value: abilityScores.wisdom },
                  { label: 'CHA', value: abilityScores.charisma },
                ].map(({ label, value }) => (
                  <div key={label} className="text-center">
                    <span className="text-xs text-gray-600 block">{label}</span>
                    <span className="text-xl font-bold text-gray-900">{value || '?'}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {/* Section Summary */}
        <div className="grid md:grid-cols-2 gap-4 mb-8">
          {/* Inventory */}
          {inventory && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">🎒</span>
                <h4 className="font-bold text-gray-900">Inventory</h4>
              </div>
              <p className="text-sm text-gray-600">
                {Object.keys(inventory.equipped_items || {}).length} equipped items,{' '}
                {inventory.backpack?.length || 0} backpack items
              </p>
            </div>
          )}
          
          {/* Spells */}
          {spellList && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">✨</span>
                <h4 className="font-bold text-gray-900">Spells</h4>
              </div>
              <p className="text-sm text-gray-600">
                {spellList.spells?.length || 0} spells known
              </p>
            </div>
          )}
          
          {/* Backstory */}
          {backstory && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">📜</span>
                <h4 className="font-bold text-gray-900">Backstory</h4>
              </div>
              <p className="text-sm text-gray-600 line-clamp-2">
                {backstory.early_life || 'No backstory provided'}
              </p>
            </div>
          )}
          
          {/* Personality */}
          {personality && (
            <div className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">🎭</span>
                <h4 className="font-bold text-gray-900">Personality</h4>
              </div>
              <p className="text-sm text-gray-600 line-clamp-2">
                {personality.traits || 'No traits provided'}
              </p>
            </div>
          )}
        </div>
        
        {/* Save Button */}
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="w-full px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed font-bold text-lg transition-all transform hover:scale-105 active:scale-95 disabled:transform-none"
        >
          {isSaving ? 'Saving Character...' : 'Save Character to Database'}
        </button>
        
        {/* Info Box */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <span className="text-blue-600 text-xl">ℹ️</span>
            <div className="text-sm text-blue-800">
              <p className="font-bold mb-1">What happens when you save?</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Character data is stored in the database</li>
                <li>You can view and edit the character anytime</li>
                <li>Character becomes available for AI assistant queries</li>
                <li>Original D&D Beyond data is preserved</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
