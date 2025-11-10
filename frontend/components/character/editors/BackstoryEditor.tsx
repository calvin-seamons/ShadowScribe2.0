/**
 * Backstory Editor
 * 
 * Text area editor for character backstory sections
 */

'use client'

import { useState } from 'react'

interface BackstoryData {
  title?: string
  family?: string
  early_life?: string
  defining_moment?: string
  current_situation?: string
  goals_and_aspirations?: string
  secrets_and_mysteries?: string
  [key: string]: any
}

interface BackstoryEditorProps {
  data: BackstoryData | null
  onSave: (data: BackstoryData) => void
}

export function BackstoryEditor({ data, onSave }: BackstoryEditorProps) {
  const [backstory, setBackstory] = useState<BackstoryData>(data || {
    title: '',
    family: '',
    early_life: '',
    defining_moment: '',
    current_situation: '',
    goals_and_aspirations: '',
    secrets_and_mysteries: '',
  })
  const [isSaving, setIsSaving] = useState(false)
  
  const handleSave = async () => {
    setIsSaving(true)
    try {
      await onSave(backstory)
    } finally {
      setIsSaving(false)
    }
  }
  
  const updateField = (field: string, value: string) => {
    setBackstory({ ...backstory, [field]: value })
  }
  
  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Title
        </label>
        <input
          type="text"
          value={backstory.title || ''}
          onChange={(e) => updateField('title', e.target.value)}
          placeholder="e.g., 'The Shadow's Apprentice'"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
        />
      </div>
      
      {/* Family History */}
      <div>
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Family History
        </label>
        <textarea
          value={backstory.family || ''}
          onChange={(e) => updateField('family', e.target.value)}
          placeholder="Describe your character's family background, heritage, and upbringing..."
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
        />
        <p className="text-xs text-gray-600 mt-1">
          {backstory.family?.length || 0} characters
        </p>
      </div>
      
      {/* Early Life */}
      <div>
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Early Life
        </label>
        <textarea
          value={backstory.early_life || ''}
          onChange={(e) => updateField('early_life', e.target.value)}
          placeholder="What was your character's childhood and formative years like?"
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
        />
        <p className="text-xs text-gray-600 mt-1">
          {backstory.early_life?.length || 0} characters
        </p>
      </div>
      
      {/* Defining Moment */}
      <div>
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Defining Moment
        </label>
        <textarea
          value={backstory.defining_moment || ''}
          onChange={(e) => updateField('defining_moment', e.target.value)}
          placeholder="What pivotal event shaped your character into who they are today?"
          rows={4}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
        />
        <p className="text-xs text-gray-600 mt-1">
          {backstory.defining_moment?.length || 0} characters
        </p>
      </div>
      
      {/* Current Situation */}
      <div>
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Current Situation
        </label>
        <textarea
          value={backstory.current_situation || ''}
          onChange={(e) => updateField('current_situation', e.target.value)}
          placeholder="Where is your character now? What are they currently dealing with?"
          rows={3}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
        />
        <p className="text-xs text-gray-600 mt-1">
          {backstory.current_situation?.length || 0} characters
        </p>
      </div>
      
      {/* Goals and Aspirations */}
      <div>
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Goals and Aspirations
        </label>
        <textarea
          value={backstory.goals_and_aspirations || ''}
          onChange={(e) => updateField('goals_and_aspirations', e.target.value)}
          placeholder="What does your character hope to achieve? What are their dreams?"
          rows={3}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
        />
        <p className="text-xs text-gray-600 mt-1">
          {backstory.goals_and_aspirations?.length || 0} characters
        </p>
      </div>
      
      {/* Secrets and Mysteries */}
      <div>
        <label className="block text-sm font-bold text-gray-900 mb-2">
          Secrets and Mysteries
        </label>
        <textarea
          value={backstory.secrets_and_mysteries || ''}
          onChange={(e) => updateField('secrets_and_mysteries', e.target.value)}
          placeholder="What secrets does your character keep? What mysteries surround them?"
          rows={3}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
        />
        <p className="text-xs text-gray-600 mt-1">
          {backstory.secrets_and_mysteries?.length || 0} characters
        </p>
      </div>
      
      {/* Save Button */}
      <div className="flex justify-end pt-4">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed font-medium transition-all transform hover:scale-105 active:scale-95 disabled:transform-none"
        >
          {isSaving ? 'Saving...' : 'Save Backstory'}
        </button>
      </div>
    </div>
  )
}
