/**
 * Multi-Step Character Creation Wizard
 * 
 * A comprehensive 4-step wizard for importing and creating D&D characters:
 * 1. URL Input - Fetch character from D&D Beyond
 * 2. Parsing Progress - Real-time parser status with progress bars
 * 3. Section Review - Edit character sections (ability scores, inventory, etc.)
 * 4. Preview & Save - Final character preview and database save
 */

'use client'

import { useState, useEffect } from 'react'
import { useCharacterCreation } from '@/lib/hooks/useCharacterCreation'
import type { CharacterSummary } from '@/lib/types/character'

// Step components
import {
  Step1_UrlInput,
  Step2_ParsingProgress,
  Step3_SectionReview,
  Step4_PreviewAndSave,
  WizardProgress
} from './wizard'

const TOTAL_STEPS = 4

export function CharacterCreationWizard() {
  const [currentStep, setCurrentStep] = useState(1)
  const [dndbeyondUrl, setDndbeyondUrl] = useState('')
  const [characterJsonData, setCharacterJsonData] = useState<any>(null) // Raw D&D Beyond JSON
  const [savedCharacterId, setSavedCharacterId] = useState<string | null>(null)
  
  const {
    createCharacter,
    parsers,
    isCreating,
    error,
    characterId,
    characterSummary,
    characterData, // Parsed character with all sections
    progressEvents,
    resetProgress,
    completedCount,
    totalCount,
  } = useCharacterCreation()
  
  // Auto-advance to step 3 when parsing completes
  useEffect(() => {
    if (currentStep === 2 && completedCount === totalCount && !isCreating && characterSummary) {
      // Small delay to show completion state
      setTimeout(() => {
        setCurrentStep(3)
      }, 1000)
    }
  }, [currentStep, completedCount, totalCount, isCreating, characterSummary])
  
  const handleNextStep = () => {
    if (currentStep < TOTAL_STEPS) {
      setCurrentStep(currentStep + 1)
    }
  }
  
  const handlePrevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }
  
  const handleFetchCharacter = async (url: string) => {
    setDndbeyondUrl(url)
    
    try {
      // Fetch from D&D Beyond API
      const response = await fetch('/api/characters/fetch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || errorData.detail || 'Failed to fetch character')
      }
      
      const data = await response.json()
      setCharacterJsonData(data.json_data)
      
      // Move to step 2 (parsing)
      setCurrentStep(2)
      
      // Start character creation via WebSocket
      await createCharacter(data.json_data)
      
    } catch (err) {
      console.error('Error fetching character:', err)
      // Error will be displayed by Step1 component
    }
  }
  
  const handleSectionSave = async (section: string, data: any) => {
    if (!savedCharacterId) {
      console.error('No character ID available for section update')
      return
    }
    
    try {
      const response = await fetch(`/api/characters/${savedCharacterId}/${section}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data })
      })
      
      if (!response.ok) {
        throw new Error('Failed to save section')
      }
      
      console.log(`Section ${section} saved successfully`)
    } catch (err) {
      console.error(`Error saving section ${section}:`, err)
      throw err
    }
  }
  
  const handleFinalSave = async () => {
    if (!characterData) {
      console.error('No character data available to save')
      return
    }
    
    try {
      // Save complete character to database using parsed data
      const response = await fetch('/api/characters', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ character: characterData })
      })
      
      if (!response.ok) {
        throw new Error('Failed to save character')
      }
      
      const data = await response.json()
      setSavedCharacterId(data.id)
      
      console.log('Character saved successfully:', data.id)
      return data.id
    } catch (err) {
      console.error('Error saving character:', err)
      throw err
    }
  }
  
  const handleReset = () => {
    setCurrentStep(1)
    setDndbeyondUrl('')
    setCharacterJsonData(null)
    setSavedCharacterId(null)
    resetProgress()
  }
  
  return (
    <div className="min-h-screen bg-background py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent mb-2">
            Character Creation Wizard
          </h1>
          <p className="text-muted-foreground">
            Import your D&D Beyond character and customize every detail
          </p>
        </div>
        
        {/* Progress Indicator */}
        <WizardProgress currentStep={currentStep} totalSteps={TOTAL_STEPS} />
        
        {/* Main Content */}
        <div className="bg-card border border-border rounded-lg shadow-lg overflow-hidden">
          {currentStep === 1 && (
            <Step1_UrlInput
              onFetch={handleFetchCharacter}
              onNext={handleNextStep}
            />
          )}
          
          {currentStep === 2 && (
            <Step2_ParsingProgress
              parsers={parsers}
              isCreating={isCreating}
              error={error}
              completedCount={completedCount}
              totalCount={totalCount}
              characterSummary={characterSummary}
              onNext={handleNextStep}
            />
          )}
          
          {currentStep === 3 && (
            <Step3_SectionReview
              characterData={characterData || {}}
              onSectionSave={handleSectionSave}
              onNext={handleNextStep}
            />
          )}
          
          {currentStep === 4 && (
            <Step4_PreviewAndSave
              characterData={characterData || {}}
              savedCharacterId={savedCharacterId ? Number(savedCharacterId) : null}
              onSave={handleFinalSave}
              onReset={handleReset}
            />
          )}
        </div>
        
        {/* Debug Info (development only) */}
        {process.env.NODE_ENV === 'development' && (
          <details className="mt-4 bg-card border border-border rounded-lg p-4">
            <summary className="cursor-pointer font-medium text-foreground">Debug Info</summary>
            <div className="mt-2 space-y-2 text-sm font-mono text-muted-foreground">
              <div>Current Step: {currentStep}</div>
              <div>Character ID: {characterId || 'N/A'}</div>
              <div>Saved ID: {savedCharacterId || 'N/A'}</div>
              <div>Is Creating: {isCreating.toString()}</div>
              <div>Completed: {completedCount}/{totalCount}</div>
              <div>Has Character Data: {!!characterData ? 'Yes' : 'No'}</div>
              <div>Has Raw JSON: {!!characterJsonData ? 'Yes' : 'No'}</div>
              <div>Has Summary: {!!characterSummary ? 'Yes' : 'No'}</div>
              <div>Progress Events: {progressEvents.length}</div>
            </div>
          </details>
        )}
      </div>
    </div>
  )
}
