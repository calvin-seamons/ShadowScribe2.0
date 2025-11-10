/**
 * Step 3: Section Review & Edit
 * 
 * Accordion UI for reviewing and editing character sections
 */

'use client'

import { useState } from 'react'
import type { CharacterData } from '@/lib/types/character'
import {
  AbilityScoresEditor,
  BackstoryEditor,
  PersonalityEditor,
  InventoryEditor,
  SpellListEditor,
  ActionsEditor,
} from '../editors'

interface Step3_SectionReviewProps {
  characterData: CharacterData | null
  onSectionSave: (sectionName: string, sectionData: any) => Promise<void>
  onNext: () => void
}

type SectionName = 'ability_scores' | 'combat_stats' | 'inventory' | 'spell_list' | 'action_economy' | 'features_and_traits' | 'backstory' | 'personality'

interface SectionConfig {
  name: SectionName
  label: string
  icon: string
  description: string
  hasEditor: boolean
}

const SECTIONS: SectionConfig[] = [
  {
    name: 'ability_scores',
    label: 'Ability Scores',
    icon: '💪',
    description: 'Strength, Dexterity, Constitution, Intelligence, Wisdom, Charisma',
    hasEditor: true,
  },
  {
    name: 'combat_stats',
    label: 'Combat Stats',
    icon: '⚔️',
    description: 'Hit Points, Armor Class, Initiative, Speed',
    hasEditor: false,
  },
  {
    name: 'inventory',
    label: 'Inventory & Equipment',
    icon: '🎒',
    description: 'Weapons, armor, items, and currency',
    hasEditor: true,
  },
  {
    name: 'spell_list',
    label: 'Spells',
    icon: '✨',
    description: 'Known spells, spell slots, and spellcasting abilities',
    hasEditor: true,
  },
  {
    name: 'action_economy',
    label: 'Actions & Attacks',
    icon: '🎯',
    description: 'Available actions, attacks, and bonus actions',
    hasEditor: true,
  },
  {
    name: 'features_and_traits',
    label: 'Features & Traits',
    icon: '🎖️',
    description: 'Class features, racial traits, and special abilities',
    hasEditor: false,
  },
  {
    name: 'backstory',
    label: 'Backstory',
    icon: '📜',
    description: 'Character history, family, and defining moments',
    hasEditor: true,
  },
  {
    name: 'personality',
    label: 'Personality',
    icon: '🎭',
    description: 'Traits, ideals, bonds, and flaws',
    hasEditor: true,
  },
]

export function Step3_SectionReview({
  characterData,
  onSectionSave,
  onNext,
}: Step3_SectionReviewProps) {
  const [expandedSection, setExpandedSection] = useState<SectionName | null>(null)
  const [savingSection, setSavingSection] = useState<SectionName | null>(null)
  
  const toggleSection = (sectionName: SectionName) => {
    setExpandedSection(expandedSection === sectionName ? null : sectionName)
  }
  
  const handleSectionSave = async (sectionName: SectionName) => {
    if (!characterData || !characterData[sectionName]) return
    
    setSavingSection(sectionName)
    try {
      await onSectionSave(sectionName, characterData[sectionName])
    } finally {
      setSavingSection(null)
    }
  }
  
  if (!characterData) {
    return (
      <div className="p-8 text-center">
        <p className="text-gray-600">No character data available</p>
      </div>
    )
  }
  
  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Review & Edit Sections</h2>
          <p className="text-gray-600">
            Review each section and make any necessary changes before saving
          </p>
        </div>
        
        {/* Section Accordion */}
        <div className="space-y-3 mb-8">
          {SECTIONS.map((section) => {
            const isExpanded = expandedSection === section.name
            const isSaving = savingSection === section.name
            const hasData = !!characterData[section.name]
            
            return (
              <div
                key={section.name}
                className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-all"
              >
                {/* Section Header */}
                <button
                  onClick={() => toggleSection(section.name)}
                  className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <span className="text-3xl">{section.icon}</span>
                    <div className="text-left">
                      <h3 className="font-bold text-lg text-gray-900">{section.label}</h3>
                      <p className="text-sm text-gray-600">{section.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {hasData && (
                      <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                        ✓ Loaded
                      </span>
                    )}
                    <span className={`text-2xl transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
                      ▼
                    </span>
                  </div>
                </button>
                
                {/* Section Content (expanded) */}
                {isExpanded && (
                  <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
                    {hasData ? (
                      <div>
                        {/* Render appropriate editor based on section */}
                        {section.hasEditor ? (
                          <>
                            {section.name === 'ability_scores' && (
                              <AbilityScoresEditor
                                data={characterData[section.name]}
                                onSave={async (data) => handleSectionSave(section.name)}
                              />
                            )}
                            {section.name === 'inventory' && (
                              <InventoryEditor
                                data={characterData[section.name]}
                                onSave={async (data) => handleSectionSave(section.name)}
                              />
                            )}
                            {section.name === 'spell_list' && (
                              <SpellListEditor
                                data={characterData[section.name]}
                                onSave={async (data) => handleSectionSave(section.name)}
                              />
                            )}
                            {section.name === 'action_economy' && (
                              <ActionsEditor
                                data={characterData[section.name]}
                                onSave={async (data) => handleSectionSave(section.name)}
                              />
                            )}
                            {section.name === 'backstory' && (
                              <BackstoryEditor
                                data={characterData[section.name]}
                                onSave={async (data) => handleSectionSave(section.name)}
                              />
                            )}
                            {section.name === 'personality' && (
                              <PersonalityEditor
                                data={characterData[section.name]}
                                onSave={async (data) => handleSectionSave(section.name)}
                              />
                            )}
                          </>
                        ) : (
                          <>
                            {/* JSON Preview for sections without editors yet */}
                            <div className="bg-white border border-gray-300 rounded-lg p-4 mb-4">
                              <div className="text-xs text-gray-600 mb-2">Section Data Preview:</div>
                              <pre className="text-xs text-gray-800 overflow-x-auto max-h-60 overflow-y-auto">
                                {JSON.stringify(characterData[section.name], null, 2)}
                              </pre>
                            </div>
                            
                            <div className="flex items-center justify-between">
                              <p className="text-sm text-gray-600">
                                <span className="font-bold">Note:</span> Full editing UI for this section coming soon.
                                For now, you can save this section as-is or edit after saving the character.
                              </p>
                              <button
                                onClick={() => handleSectionSave(section.name)}
                                disabled={isSaving}
                                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
                              >
                                {isSaving ? 'Saving...' : 'Save Section'}
                              </button>
                            </div>
                          </>
                        )}
                      </div>
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        <p>No data available for this section</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
        
        {/* Navigation Buttons */}
        <div className="flex gap-4">
          <button
            onClick={onNext}
            className="flex-1 px-6 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 font-bold text-lg transition-all transform hover:scale-105 active:scale-95"
          >
            Continue to Preview & Save →
          </button>
        </div>
        
        {/* Info Box */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <span className="text-blue-600 text-xl">ℹ️</span>
            <div className="text-sm text-blue-800">
              <p className="font-bold mb-1">Section Editing</p>
              <p>
                You can save individual sections now or skip to the final step to save the entire character at once.
                After saving, you'll be able to edit any section from the character detail page.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
