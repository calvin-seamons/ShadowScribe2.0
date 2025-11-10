/**
 * Ability Scores Editor
 * 
 * Editor for the 6 core D&D ability scores with automatic modifier calculation
 */

'use client'

import { useState } from 'react'

interface AbilityScoresData {
  strength?: number
  dexterity?: number
  constitution?: number
  intelligence?: number
  wisdom?: number
  charisma?: number
  [key: string]: any
}

interface AbilityScoresEditorProps {
  data: AbilityScoresData | null
  onSave: (data: AbilityScoresData) => void
}

const ABILITIES = [
  { key: 'strength', label: 'Strength', abbr: 'STR', description: 'Physical power, melee attacks' },
  { key: 'dexterity', label: 'Dexterity', abbr: 'DEX', description: 'Agility, AC, ranged attacks' },
  { key: 'constitution', label: 'Constitution', abbr: 'CON', description: 'Endurance, hit points' },
  { key: 'intelligence', label: 'Intelligence', abbr: 'INT', description: 'Reasoning, knowledge' },
  { key: 'wisdom', label: 'Wisdom', abbr: 'WIS', description: 'Awareness, insight' },
  { key: 'charisma', label: 'Charisma', abbr: 'CHA', description: 'Force of personality' },
]

export function AbilityScoresEditor({ data, onSave }: AbilityScoresEditorProps) {
  const [scores, setScores] = useState<AbilityScoresData>(data || {
    strength: 10,
    dexterity: 10,
    constitution: 10,
    intelligence: 10,
    wisdom: 10,
    charisma: 10,
  })
  const [isSaving, setIsSaving] = useState(false)
  
  const calculateModifier = (score: number): number => {
    return Math.floor((score - 10) / 2)
  }
  
  const formatModifier = (modifier: number): string => {
    return modifier >= 0 ? `+${modifier}` : `${modifier}`
  }
  
  const handleSave = async () => {
    setIsSaving(true)
    try {
      await onSave(scores)
    } finally {
      setIsSaving(false)
    }
  }
  
  const updateScore = (ability: string, value: string) => {
    const numValue = parseInt(value) || 0
    // Clamp between 1 and 30 (D&D 5e typical range)
    const clampedValue = Math.max(1, Math.min(30, numValue))
    setScores({ ...scores, [ability]: clampedValue })
  }
  
  return (
    <div className="space-y-6">
      {/* Ability Scores Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {ABILITIES.map((ability) => {
          const score = scores[ability.key] || 10
          const modifier = calculateModifier(score)
          
          return (
            <div
              key={ability.key}
              className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-4 border-2 border-purple-200"
            >
              <div className="flex items-center justify-between mb-2">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{ability.label}</h3>
                  <p className="text-xs text-gray-600">{ability.description}</p>
                </div>
                <span className="text-2xl font-bold text-purple-600">{ability.abbr}</span>
              </div>
              
              <div className="flex items-center gap-4 mt-3">
                {/* Score Input */}
                <div className="flex-1">
                  <label className="block text-xs font-medium text-gray-700 mb-1">Score</label>
                  <input
                    type="number"
                    min="1"
                    max="30"
                    value={score}
                    onChange={(e) => updateScore(ability.key, e.target.value)}
                    className="w-full px-3 py-2 text-center text-2xl font-bold border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
                
                {/* Modifier Display */}
                <div className="flex-1">
                  <label className="block text-xs font-medium text-gray-700 mb-1">Modifier</label>
                  <div className={`px-3 py-2 text-center text-2xl font-bold rounded-lg ${
                    modifier >= 0 
                      ? 'bg-green-100 text-green-700 border-2 border-green-300' 
                      : 'bg-red-100 text-red-700 border-2 border-red-300'
                  }`}>
                    {formatModifier(modifier)}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
      
      {/* Stats Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <span className="text-blue-600 text-xl">📊</span>
          <div className="text-sm text-blue-800">
            <p className="font-bold mb-1">Ability Score Summary</p>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-2">
              <div>
                <span className="font-medium">Total:</span>{' '}
                {ABILITIES.reduce((sum, a) => sum + (scores[a.key] || 0), 0)}
              </div>
              <div>
                <span className="font-medium">Average:</span>{' '}
                {(ABILITIES.reduce((sum, a) => sum + (scores[a.key] || 0), 0) / 6).toFixed(1)}
              </div>
              <div>
                <span className="font-medium">Total Modifiers:</span>{' '}
                {formatModifier(ABILITIES.reduce((sum, a) => sum + calculateModifier(scores[a.key] || 0), 0))}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Info Box */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <span className="text-purple-600 text-xl">💡</span>
          <div className="text-sm text-purple-800">
            <p className="font-bold mb-1">D&D 5e Ability Score Guidelines</p>
            <ul className="list-disc list-inside space-y-1">
              <li><strong>10-11:</strong> Average human ability</li>
              <li><strong>14-15:</strong> Naturally gifted</li>
              <li><strong>18:</strong> Exceptional (typical maximum at character creation)</li>
              <li><strong>20:</strong> Legendary (maximum for most characters)</li>
              <li><strong>30:</strong> Godlike (ancient dragons, deities)</li>
            </ul>
          </div>
        </div>
      </div>
      
      {/* Save Button */}
      <div className="flex justify-end pt-4">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed font-medium transition-all transform hover:scale-105 active:scale-95 disabled:transform-none"
        >
          {isSaving ? 'Saving...' : 'Save Ability Scores'}
        </button>
      </div>
    </div>
  )
}
