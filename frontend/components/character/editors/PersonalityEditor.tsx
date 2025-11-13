/**
 * Personality Editor
 * 
 * Text area editor for character personality traits
 */

'use client'

import { useState } from 'react'

interface PersonalityData {
  personality_traits?: string[] | string
  ideals?: string[] | string
  bonds?: string[] | string
  flaws?: string[] | string
  [key: string]: any
}

interface PersonalityEditorProps {
  data: PersonalityData | null
  onSave: (data: PersonalityData) => void
}

export function PersonalityEditor({ data, onSave }: PersonalityEditorProps) {
  const [personality, setPersonality] = useState<PersonalityData>(() => {
    // Normalize data - backend sends arrays, display as newline-separated text
    const normalizeField = (field: string[] | string | undefined) => {
      if (!field) return ''
      if (Array.isArray(field)) return field.join('\n')
      return field
    }
    
    return {
      personality_traits: normalizeField(data?.personality_traits),
      ideals: normalizeField(data?.ideals),
      bonds: normalizeField(data?.bonds),
      flaws: normalizeField(data?.flaws),
    }
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
      {/* Info Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p className="text-sm text-blue-800">
          ℹ️ <strong>Personality Data:</strong> These fields were parsed from D&D Beyond. Each line represents a separate trait/ideal/bond/flaw.
        </p>
      </div>
      
      {/* Personality Traits */}
      <div>
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Personality Traits
        </label>
        <textarea
          value={(personality.personality_traits as string) || ''}
          onChange={(e) => updateField('personality_traits', e.target.value)}
          placeholder="What are your character's defining personality traits? (e.g., 'Always has a plan', 'Optimistic to a fault')\nOne per line"
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none font-mono text-sm"
        />
        <p className="text-xs text-gray-600 mt-1">
          {((personality.personality_traits as string) || '').split('\n').filter(t => t.trim()).length} traits
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
          value={(personality.ideals as string) || ''}
          onChange={(e) => updateField('ideals', e.target.value)}
          placeholder="What principles or beliefs drive your character? (e.g., 'Justice above all', 'Knowledge is power')\nOne per line"
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none font-mono text-sm"
        />
        <p className="text-xs text-gray-600 mt-1">
          {((personality.ideals as string) || '').split('\n').filter(t => t.trim()).length} ideals
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
          value={(personality.bonds as string) || ''}
          onChange={(e) => updateField('bonds', e.target.value)}
          placeholder="What people, places, or things is your character most connected to? (e.g., 'My sword was my father's', 'I'll protect my village')\nOne per line"
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none font-mono text-sm"
        />
        <p className="text-xs text-gray-600 mt-1">
          {((personality.bonds as string) || '').split('\n').filter(t => t.trim()).length} bonds
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
          value={(personality.flaws as string) || ''}
          onChange={(e) => updateField('flaws', e.target.value)}
          placeholder="What weaknesses, vices, or negative traits does your character have? (e.g., 'I can't resist a pretty face', 'Overconfident in combat')\nOne per line"
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none font-mono text-sm"
        />
        <p className="text-xs text-gray-600 mt-1">
          {((personality.flaws as string) || '').split('\n').filter(t => t.trim()).length} flaws
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
