/**
 * Combat Stats Editor
 * 
 * Editor for core combat statistics: HP, AC, Initiative, Speed, Hit Dice
 */

'use client'

import { useState } from 'react'

interface CombatStatsData {
  max_hp?: number
  armor_class?: number
  initiative_bonus?: number
  speed?: number
  hit_dice?: Record<string, string>
  [key: string]: any
}

interface CombatStatsEditorProps {
  data: CombatStatsData | null
  onSave: (data: CombatStatsData) => void
}

export function CombatStatsEditor({ data, onSave }: CombatStatsEditorProps) {
  const [stats, setStats] = useState<CombatStatsData>(() => {
    return data || {
      max_hp: 0,
      armor_class: 10,
      initiative_bonus: 0,
      speed: 30,
      hit_dice: {},
    }
  })
  const [isSaving, setIsSaving] = useState(false)
  
  const handleSave = async () => {
    setIsSaving(true)
    try {
      await onSave(stats)
    } finally {
      setIsSaving(false)
    }
  }
  
  const updateStat = (field: string, value: number) => {
    setStats({ ...stats, [field]: value })
  }
  
  const formatInitiative = (bonus: number) => {
    return bonus >= 0 ? `+${bonus}` : `${bonus}`
  }
  
  return (
    <div className="space-y-6">
      {/* Info Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p className="text-sm text-blue-800">
          ℹ️ <strong>Combat Statistics:</strong> Core stats for combat encounters. Values are calculated from D&D Beyond but can be adjusted here.
        </p>
      </div>
      
      {/* Primary Stats Grid */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Hit Points */}
        <div className="bg-gradient-to-br from-red-50 to-pink-50 rounded-lg p-6 border-2 border-red-300">
          <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
            <span className="text-2xl">❤️</span>
            <span>Hit Points (HP)</span>
          </label>
          <input
            type="number"
            min="1"
            value={stats.max_hp || 0}
            onChange={(e) => updateStat('max_hp', parseInt(e.target.value) || 0)}
            className="w-full px-4 py-3 text-3xl font-bold text-center border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-600 mt-2 text-center">Maximum Hit Points</p>
        </div>
        
        {/* Armor Class */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border-2 border-blue-300">
          <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
            <span className="text-2xl">🛡️</span>
            <span>Armor Class (AC)</span>
          </label>
          <input
            type="number"
            min="1"
            value={stats.armor_class || 10}
            onChange={(e) => updateStat('armor_class', parseInt(e.target.value) || 10)}
            className="w-full px-4 py-3 text-3xl font-bold text-center border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-600 mt-2 text-center">Defense Rating</p>
        </div>
      </div>
      
      {/* Secondary Stats Grid */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Initiative */}
        <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg p-6 border-2 border-yellow-300">
          <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
            <span className="text-2xl">⚡</span>
            <span>Initiative Bonus</span>
          </label>
          <input
            type="number"
            value={stats.initiative_bonus || 0}
            onChange={(e) => updateStat('initiative_bonus', parseInt(e.target.value) || 0)}
            className="w-full px-4 py-3 text-3xl font-bold text-center border border-gray-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-600 mt-2 text-center">
            Roll: d20 {formatInitiative(stats.initiative_bonus || 0)}
          </p>
        </div>
        
        {/* Speed */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-6 border-2 border-green-300">
          <label className="block text-sm font-bold text-gray-700 mb-2 flex items-center gap-2">
            <span className="text-2xl">👟</span>
            <span>Speed</span>
          </label>
          <div className="relative w-full">
            <input
              type="number"
              min="0"
              step="5"
              value={stats.speed || 30}
              onChange={(e) => updateStat('speed', parseInt(e.target.value) || 30)}
              className="w-full px-4 py-3 pr-12 text-3xl font-bold text-center border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
            <span className="absolute right-4 top-1/2 -translate-y-1/2 text-xl font-bold text-gray-600 pointer-events-none">ft</span>
          </div>
          <p className="text-xs text-gray-600 mt-2 text-center">Walking Speed per Turn</p>
        </div>
      </div>
      
      {/* Hit Dice Section */}
      {stats.hit_dice && Object.keys(stats.hit_dice).length > 0 && (
        <div className="bg-white border-2 border-gray-300 rounded-lg p-4">
          <h4 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
            <span className="text-xl">🎲</span>
            <span>Hit Dice</span>
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {Object.entries(stats.hit_dice).map(([className, dice]) => (
              <div key={className} className="bg-gray-50 rounded p-3 text-center">
                <div className="text-xs font-medium text-gray-600 mb-1">{className}</div>
                <div className="text-lg font-bold text-gray-900">{dice}</div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Save Button */}
      <div className="flex justify-end pt-4 border-t border-gray-200">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
        >
          {isSaving ? 'Saving...' : 'Save Combat Stats'}
        </button>
      </div>
    </div>
  )
}
