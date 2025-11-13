/**
 * Features and Traits Editor
 * 
 * Display and editing for racial traits, class features, feats, and modifiers
 */

'use client'

import { useState } from 'react'

interface RacialTrait {
  name: string
  description?: string
  featureType?: string
  creatureRules?: any[]
}

interface ClassFeature {
  name: string
  description?: string
}

interface Feat {
  name: string
  description?: string
  isRepeatable?: boolean
}

interface FeatureModifier {
  type?: string
  subType?: string
  friendlyTypeName?: string
  friendlySubtypeName?: string
  value?: number
  restriction?: string
}

interface FeaturesAndTraitsData {
  racial_traits?: RacialTrait[]
  class_features?: Record<string, Record<number, ClassFeature[]>>
  feats?: Feat[]
  modifiers?: Record<string, FeatureModifier[]>
  [key: string]: any
}

interface FeaturesAndTraitsEditorProps {
  data: FeaturesAndTraitsData | null
  onSave: (data: FeaturesAndTraitsData) => void
}

type SectionType = 'racial' | 'class' | 'feats' | 'modifiers' | null

export function FeaturesAndTraitsEditor({ data, onSave }: FeaturesAndTraitsEditorProps) {
  const [features, setFeatures] = useState<FeaturesAndTraitsData>(data || {
    racial_traits: [],
    class_features: {},
    feats: [],
    modifiers: {},
  })
  const [isSaving, setIsSaving] = useState(false)
  const [expandedSection, setExpandedSection] = useState<SectionType>(null)
  
  const handleSave = async () => {
    setIsSaving(true)
    try {
      await onSave(features)
    } finally {
      setIsSaving(false)
    }
  }
  
  const stripHtml = (html: string | undefined) => {
    if (!html) return ''
    // Basic HTML tag removal - can be enhanced
    return html.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim()
  }
  
  return (
    <div className="space-y-6">
      {/* Info Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <p className="text-sm text-blue-800">
          ℹ️ <strong>Features & Traits:</strong> Character abilities from race, class, feats, and items. Data is imported from D&D Beyond.
        </p>
      </div>
      
      {/* Racial Traits Section */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <button
          onClick={() => setExpandedSection(expandedSection === 'racial' ? null : 'racial')}
          className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">🧬</span>
            <div className="text-left">
              <h3 className="font-bold text-gray-900">Racial Traits</h3>
              <p className="text-xs text-gray-600">
                {features.racial_traits?.length || 0} traits
              </p>
            </div>
          </div>
          <span className={`text-xl transition-transform ${expandedSection === 'racial' ? 'rotate-180' : ''}`}>
            ▼
          </span>
        </button>
        
        {expandedSection === 'racial' && (
          <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
            {!features.racial_traits || features.racial_traits.length === 0 ? (
              <p className="text-center text-gray-500 py-4">No racial traits found</p>
            ) : (
              <div className="space-y-3">
                {features.racial_traits.map((trait, index) => (
                  <div key={index} className="bg-white rounded-lg p-4 border border-gray-300">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-bold text-gray-900">{trait.name}</h4>
                      {trait.featureType && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                          {trait.featureType}
                        </span>
                      )}
                    </div>
                    {trait.description && (
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">
                        {stripHtml(trait.description)}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Class Features Section */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <button
          onClick={() => setExpandedSection(expandedSection === 'class' ? null : 'class')}
          className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">🎖️</span>
            <div className="text-left">
              <h3 className="font-bold text-gray-900">Class Features</h3>
              <p className="text-xs text-gray-600">
                {Object.keys(features.class_features || {}).length} classes
              </p>
            </div>
          </div>
          <span className={`text-xl transition-transform ${expandedSection === 'class' ? 'rotate-180' : ''}`}>
            ▼
          </span>
        </button>
        
        {expandedSection === 'class' && (
          <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
            {!features.class_features || Object.keys(features.class_features).length === 0 ? (
              <p className="text-center text-gray-500 py-4">No class features found</p>
            ) : (
              <div className="space-y-4">
                {Object.entries(features.class_features).map(([className, levelFeatures]) => (
                  <div key={className} className="bg-white rounded-lg p-4 border-2 border-purple-200">
                    <h4 className="font-bold text-lg text-purple-800 mb-3">{className}</h4>
                    <div className="space-y-3">
                      {Object.entries(levelFeatures).map(([level, featuresList]) => (
                        <div key={level} className="border-l-4 border-purple-300 pl-3">
                          <div className="text-xs font-bold text-purple-600 mb-2">
                            Level {level}
                          </div>
                          <div className="space-y-2">
                            {(featuresList as ClassFeature[]).map((feature, idx) => (
                              <div key={idx} className="bg-gray-50 rounded p-2">
                                <div className="font-bold text-sm text-gray-900 mb-1">
                                  {feature.name}
                                </div>
                                {feature.description && (
                                  <p className="text-xs text-gray-700 whitespace-pre-wrap">
                                    {stripHtml(feature.description)}
                                  </p>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Feats Section */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <button
          onClick={() => setExpandedSection(expandedSection === 'feats' ? null : 'feats')}
          className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">⭐</span>
            <div className="text-left">
              <h3 className="font-bold text-gray-900">Feats</h3>
              <p className="text-xs text-gray-600">
                {features.feats?.length || 0} feats
              </p>
            </div>
          </div>
          <span className={`text-xl transition-transform ${expandedSection === 'feats' ? 'rotate-180' : ''}`}>
            ▼
          </span>
        </button>
        
        {expandedSection === 'feats' && (
          <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
            {!features.feats || features.feats.length === 0 ? (
              <p className="text-center text-gray-500 py-4">No feats found</p>
            ) : (
              <div className="space-y-3">
                {features.feats.map((feat, index) => (
                  <div key={index} className="bg-white rounded-lg p-4 border border-gray-300">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-bold text-gray-900">{feat.name}</h4>
                      {feat.isRepeatable && (
                        <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs font-medium">
                          Repeatable
                        </span>
                      )}
                    </div>
                    {feat.description && (
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">
                        {stripHtml(feat.description)}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Modifiers Section */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <button
          onClick={() => setExpandedSection(expandedSection === 'modifiers' ? null : 'modifiers')}
          className="w-full px-4 py-3 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚙️</span>
            <div className="text-left">
              <h3 className="font-bold text-gray-900">Modifiers</h3>
              <p className="text-xs text-gray-600">
                {Object.keys(features.modifiers || {}).length} categories
              </p>
            </div>
          </div>
          <span className={`text-xl transition-transform ${expandedSection === 'modifiers' ? 'rotate-180' : ''}`}>
            ▼
          </span>
        </button>
        
        {expandedSection === 'modifiers' && (
          <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
            {!features.modifiers || Object.keys(features.modifiers).length === 0 ? (
              <p className="text-center text-gray-500 py-4">No modifiers found</p>
            ) : (
              <div className="space-y-4">
                {Object.entries(features.modifiers).map(([category, modifiersList]) => (
                  <div key={category} className="bg-white rounded-lg p-4 border border-gray-300">
                    <h4 className="font-bold text-gray-900 mb-3 capitalize">
                      {category} Modifiers
                    </h4>
                    <div className="space-y-2">
                      {(modifiersList as FeatureModifier[]).map((modifier, idx) => (
                        <div key={idx} className="bg-gray-50 rounded p-3 text-sm">
                          <div className="grid grid-cols-2 gap-2">
                            {modifier.friendlyTypeName && (
                              <div>
                                <span className="font-medium text-gray-700">Type: </span>
                                <span className="text-gray-900">{modifier.friendlyTypeName}</span>
                              </div>
                            )}
                            {modifier.friendlySubtypeName && (
                              <div>
                                <span className="font-medium text-gray-700">Subtype: </span>
                                <span className="text-gray-900">{modifier.friendlySubtypeName}</span>
                              </div>
                            )}
                            {modifier.value !== undefined && (
                              <div>
                                <span className="font-medium text-gray-700">Value: </span>
                                <span className="text-gray-900">
                                  {modifier.value >= 0 ? '+' : ''}{modifier.value}
                                </span>
                              </div>
                            )}
                            {modifier.restriction && (
                              <div className="col-span-2">
                                <span className="font-medium text-gray-700">Restriction: </span>
                                <span className="text-gray-900 text-xs">{modifier.restriction}</span>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Summary */}
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 border-2 border-purple-300 rounded-lg p-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-purple-600">
              {features.racial_traits?.length || 0}
            </div>
            <div className="text-xs text-gray-700">Racial Traits</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-600">
              {Object.values(features.class_features || {}).reduce((total, levelFeatures) => 
                total + Object.values(levelFeatures).reduce((sum, features) => sum + features.length, 0), 0
              )}
            </div>
            <div className="text-xs text-gray-700">Class Features</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-600">
              {features.feats?.length || 0}
            </div>
            <div className="text-xs text-gray-700">Feats</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-purple-600">
              {Object.values(features.modifiers || {}).reduce((total, mods) => total + mods.length, 0)}
            </div>
            <div className="text-xs text-gray-700">Modifiers</div>
          </div>
        </div>
      </div>
      
      {/* Save Button */}
      <div className="flex justify-end pt-4 border-t border-gray-200">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
        >
          {isSaving ? 'Saving...' : 'Save Features & Traits'}
        </button>
      </div>
    </div>
  )
}
