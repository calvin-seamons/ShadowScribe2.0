/**
 * Spell List Editor
 * 
 * Editor for spells organized by class and level with spell slot management
 */

'use client'

import { useState } from 'react'

interface Spell {
  name: string
  level: number
  school?: string
  casting_time?: string
  range?: string
  duration?: string
  description?: string
  [key: string]: any
}

interface SpellListData {
  spells?: Spell[]
  spellcasting?: Record<string, {
    spell_slots?: Record<number, number>
    spellcasting_ability?: string
    spell_save_dc?: number
    spell_attack_bonus?: number
  }>
  [key: string]: any
}

interface SpellListEditorProps {
  data: SpellListData | null
  onSave: (data: SpellListData) => void
}

const SPELL_LEVELS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

export function SpellListEditor({ data, onSave }: SpellListEditorProps) {
  const [spellList, setSpellList] = useState<SpellListData>(data || {
    spells: [],
    spellcasting: {},
  })
  const [isSaving, setIsSaving] = useState(false)
  const [selectedLevel, setSelectedLevel] = useState<number | null>(null)
  
  const handleSave = async () => {
    setIsSaving(true)
    try {
      await onSave(spellList)
    } finally {
      setIsSaving(false)
    }
  }
  
  const addSpell = (level: number) => {
    const newSpell: Spell = {
      name: 'New Spell',
      level,
      school: 'Evocation',
      casting_time: '1 action',
      range: '60 feet',
      duration: 'Instantaneous',
      description: '',
    }
    
    // Convert to flat array for editing
    const currentSpells = Array.isArray(spellList.spells) 
      ? spellList.spells 
      : []
    
    setSpellList({
      ...spellList,
      spells: [...currentSpells, newSpell]
    })
  }
  
  const removeSpell = (index: number) => {
    setSpellList({
      ...spellList,
      spells: spellList.spells?.filter((_, i) => i !== index) || []
    })
  }
  
  const updateSpell = (index: number, field: string, value: any) => {
    const updated = [...(spellList.spells || [])]
    updated[index] = { ...updated[index], [field]: value }
    setSpellList({ ...spellList, spells: updated })
  }
  
  const getSpellsByLevel = (level: number) => {
    // Handle nested dict structure: Dict[class, Dict[level, List[Spell]]]
    if (!spellList.spells) return []
    
    // If spells is already a flat array (backward compatibility)
    if (Array.isArray(spellList.spells)) {
      return spellList.spells.filter(spell => spell.level === level)
    }
    
    // If spells is a nested dict by class and level
    const allSpells: Spell[] = []
    Object.values(spellList.spells).forEach((classSpells: any) => {
      if (typeof classSpells === 'object') {
        Object.entries(classSpells).forEach(([levelKey, spells]: [string, any]) => {
          if (Array.isArray(spells)) {
            allSpells.push(...spells.filter((s: Spell) => s.level === level))
          }
        })
      }
    })
    return allSpells
  }
  
  const getLevelName = (level: number) => {
    if (level === 0) return 'Cantrips'
    if (level === 1) return '1st Level'
    if (level === 2) return '2nd Level'
    if (level === 3) return '3rd Level'
    return `${level}th Level`
  }
  
  return (
    <div className="space-y-6">
      {/* Info Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p className="text-sm text-blue-800">
          ℹ️ <strong>Read-Only View:</strong> Spell data is imported from D&D Beyond and cannot be edited here. Use D&D Beyond to modify your spell list.
        </p>
      </div>
      
      {/* Spellcasting Stats */}
      <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-4 border-2 border-blue-300">
        <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
          <span>✨</span> Spellcasting Stats
        </h3>
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Spellcasting Ability
            </label>
            <select
              value={spellList.spellcasting?.['default']?.spellcasting_ability || 'INT'}
              onChange={(e) => setSpellList({
                ...spellList,
                spellcasting: {
                  ...spellList.spellcasting,
                  'default': {
                    ...spellList.spellcasting?.['default'],
                    spellcasting_ability: e.target.value
                  }
                }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            >
              <option value="INT">Intelligence</option>
              <option value="WIS">Wisdom</option>
              <option value="CHA">Charisma</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Spell Save DC
            </label>
            <input
              type="number"
              value={spellList.spellcasting?.['default']?.spell_save_dc || 13}
              onChange={(e) => setSpellList({
                ...spellList,
                spellcasting: {
                  ...spellList.spellcasting,
                  'default': {
                    ...spellList.spellcasting?.['default'],
                    spell_save_dc: parseInt(e.target.value) || 13
                  }
                }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Spell Attack Bonus
            </label>
            <input
              type="number"
              value={spellList.spellcasting?.['default']?.spell_attack_bonus || 5}
              onChange={(e) => setSpellList({
                ...spellList,
                spellcasting: {
                  ...spellList.spellcasting,
                  'default': {
                    ...spellList.spellcasting?.['default'],
                    spell_attack_bonus: parseInt(e.target.value) || 5
                  }
                }
              })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
          </div>
        </div>
      </div>
      
      {/* Spell Levels */}
      <div>
        <h3 className="text-lg font-bold text-gray-900 mb-3">Spells by Level</h3>
        <div className="space-y-4">
          {SPELL_LEVELS.map((level) => {
            const spells = getSpellsByLevel(level)
            const isExpanded = selectedLevel === level
            
            return (
              <div key={level} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                {/* Level Header */}
                <button
                  onClick={() => setSelectedLevel(isExpanded ? null : level)}
                  className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{level === 0 ? '🔮' : '✨'}</span>
                    <div className="text-left">
                      <h4 className="font-bold text-gray-900">{getLevelName(level)}</h4>
                      <p className="text-xs text-gray-600">{spells.length} spells</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xl transition-transform ${isExpanded ? 'rotate-180' : ''}`}>
                      ▼
                    </span>
                  </div>
                </button>
                
                {/* Expanded Spell List */}
                {isExpanded && (
                  <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
                    {spells.length === 0 ? (
                      <p className="text-center text-gray-500 py-4">No spells at this level</p>
                    ) : (
                      <div className="space-y-3">
                        {spells.map((spell, spellIndex) => {
                          // Use level and spellIndex as unique identifier since spells is a nested dict
                          return (
                            <div key={`${level}-${spellIndex}`} className="bg-white rounded-lg p-3 border border-gray-300">
                              <div className="grid md:grid-cols-2 gap-3 mb-2">
                                <div>
                                  <label className="block text-xs font-medium text-gray-700 mb-1">
                                    Spell Name
                                  </label>
                                  <input
                                    type="text"
                                    value={spell.name || ''}
                                    readOnly
                                    className="w-full px-2 py-1 border border-gray-200 rounded bg-gray-50"
                                    title="Spell data is read-only"
                                  />
                                </div>
                                <div>
                                  <label className="block text-xs font-medium text-gray-700 mb-1">
                                    School
                                  </label>
                                  <input
                                    type="text"
                                    value={spell.school || ''}
                                    readOnly
                                    className="w-full px-2 py-1 border border-gray-200 rounded bg-gray-50"
                                  />
                                  {/* <select
                                    value={spell.school || 'Evocation'}
                                    disabled
                                    className="w-full px-2 py-1 border border-gray-300 rounded"
                                  >
                                    <option value="Abjuration">Abjuration</option>
                                    <option value="Conjuration">Conjuration</option>
                                    <option value="Divination">Divination</option>
                                    <option value="Enchantment">Enchantment</option>
                                    <option value="Evocation">Evocation</option>
                                    <option value="Illusion">Illusion</option>
                                    <option value="Necromancy">Necromancy</option>
                                    <option value="Transmutation">Transmutation</option>
                                  </select> */}
                                </div>
                                <div>
                                  <label className="block text-xs font-medium text-gray-700 mb-1">
                                    Casting Time
                                  </label>
                                  <input
                                    type="text"
                                    value={spell.casting_time || ''}
                                    readOnly
                                    className="w-full px-2 py-1 border border-gray-200 rounded bg-gray-50"
                                  />
                                </div>
                                <div>
                                  <label className="block text-xs font-medium text-gray-700 mb-1">
                                    Range
                                  </label>
                                  <input
                                    type="text"
                                    value={spell.range || ''}
                                    readOnly
                                    className="w-full px-2 py-1 border border-gray-200 rounded bg-gray-50"
                                  />
                                </div>
                              </div>
                              <div className="mb-2">
                                <label className="block text-xs font-medium text-gray-700 mb-1">
                                  Description
                                </label>
                                <textarea
                                  value={spell.description || ''}
                                  readOnly
                                  rows={3}
                                  className="w-full px-2 py-1 border border-gray-200 rounded text-sm bg-gray-50"
                                />
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
      
      {/* Spell Summary */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <span className="font-bold text-purple-800">Total Spells Known:</span>
          <span className="text-2xl font-bold text-purple-600">
            {SPELL_LEVELS.reduce((count, level) => count + getSpellsByLevel(level).length, 0)}
          </span>
        </div>
      </div>
    </div>
  )
}
