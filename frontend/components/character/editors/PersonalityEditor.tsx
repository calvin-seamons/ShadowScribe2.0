/**
 * Personality Editor
 * 
 * Text area editor for character personality traits
 */

'use client'

import { useState } from 'react'

interface PersonalityData {
  traits?: string
  ideals?: string
  bonds?: string
  flaws?: string
  [key: string]: any
}

interface PersonalityEditorProps {
  data: PersonalityData | null
  onSave: (data: PersonalityData) => void
}

export function PersonalityEditor({ data, onSave }: PersonalityEditorProps) {
  const [personality, setPersonality] = useState<PersonalityData>(data || {
    traits: '',
    ideals: '',
    bonds: '',
    flaws: '',
  })
  const [isSaving, setIsSaving] = useState(false)
  
  const handleSave = async () => {
    setIsSaving(true)
    try {
      await onSave(personality)
    } finally {
      setIsSaving(false)
    }
  }
  
  const updateField = (field: string, value: string) => {
    setPersonality({ ...personality, [field]: value })
  }
  
  return (
    <div className="space-y-6">
      {/* Personality Traits */}
      <div>
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Personality Traits
        </label>
        <textarea
          value={personality.traits || ''}
          onChange={(e) => updateField('traits', e.target.value)}
          placeholder="What are your character's defining personality traits? (e.g., 'Always has a plan', 'Optimistic to a fault')"
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
        />
        <p className="text-xs text-gray-600 mt-1">
          {personality.traits?.length || 0} characters
        </p>
        <p className="text-xs text-gray-500 mt-1">
          💡 Tip: D&D characters typically have 2-3 personality traits that guide their behavior
        </p>
      </div>
      
      {/* Ideals */}
      <div>
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Ideals
        </label>
        <textarea
          value={personality.ideals || ''}
          onChange={(e) => updateField('ideals', e.target.value)}
          placeholder="What principles or beliefs drive your character? (e.g., 'Justice above all', 'Knowledge is power')"
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
        />
        <p className="text-xs text-gray-600 mt-1">
          {personality.ideals?.length || 0} characters
        </p>
        <p className="text-xs text-gray-500 mt-1">
          💡 Tip: Ideals represent what matters most to your character and guide major decisions
        </p>
      </div>
      
      {/* Bonds */}
      <div>
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Bonds
        </label>
        <textarea
          value={personality.bonds || ''}
          onChange={(e) => updateField('bonds', e.target.value)}
          placeholder="What people, places, or things is your character most connected to? (e.g., 'My sword was my father's', 'I'll protect my village')"
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
        />
        <p className="text-xs text-gray-600 mt-1">
          {personality.bonds?.length || 0} characters
        </p>
        <p className="text-xs text-gray-500 mt-1">
          💡 Tip: Bonds tie your character to the world and give them reasons to adventure
        </p>
      </div>
      
      {/* Flaws */}
      <div>
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Flaws
        </label>
        <textarea
          value={personality.flaws || ''}
          onChange={(e) => updateField('flaws', e.target.value)}
          placeholder="What weaknesses, vices, or negative traits does your character have? (e.g., 'I can't resist a pretty face', 'Overconfident in combat')"
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
        />
        <p className="text-xs text-gray-600 mt-1">
          {personality.flaws?.length || 0} characters
        </p>
        <p className="text-xs text-gray-500 mt-1">
          💡 Tip: Flaws make characters interesting and create opportunities for roleplaying
        </p>
      </div>
      
      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <span className="text-blue-600 text-xl">ℹ️</span>
          <div className="text-sm text-blue-800">
            <p className="font-bold mb-1">D&D 5e Personality Framework</p>
            <p>
              These four aspects create a well-rounded character. Think about how they interact:
              Do your traits align with your ideals? Do your bonds conflict with your flaws?
              These tensions create memorable roleplay moments.
            </p>
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
          {isSaving ? 'Saving...' : 'Save Personality'}
        </button>
      </div>
    </div>
  )
}
