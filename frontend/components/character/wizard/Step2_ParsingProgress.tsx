/**
 * Step 2: Parsing Progress
 * 
 * Displays real-time progress of all 6 character parsers with progress bars
 */

'use client'

import type { ParserProgress } from '@/lib/hooks/useCharacterCreation'
import type { ParserName, CharacterSummary } from '@/lib/types/character'

interface Step2_ParsingProgressProps {
  parsers: Record<ParserName, ParserProgress>
  isCreating: boolean
  error: string | null
  completedCount: number
  totalCount: number
  characterSummary: CharacterSummary | null
  onNext: () => void
}

const PARSER_LABELS: Record<ParserName, string> = {
  core: 'Core Stats & Abilities',
  inventory: 'Inventory & Equipment',
  spells: 'Spells & Spellcasting',
  features: 'Features & Traits',
  background: 'Backstory & Personality',
  actions: 'Actions & Attacks',
}

const PARSER_ICONS: Record<ParserName, string> = {
  core: '⚡',
  inventory: '🎒',
  spells: '✨',
  features: '🎖️',
  background: '📜',
  actions: '⚔️',
}

export function Step2_ParsingProgress({
  parsers,
  isCreating,
  error,
  completedCount,
  totalCount,
  characterSummary,
  onNext,
}: Step2_ParsingProgressProps) {
  const progressPercentage = Math.round((completedCount / totalCount) * 100)
  const allComplete = completedCount === totalCount && !isCreating
  
  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-foreground mb-2">
            {allComplete ? 'Parsing Complete!' : 'Parsing Character Data'}
          </h2>
          <p className="text-muted-foreground">
            {allComplete
              ? 'Your character has been successfully parsed and is ready for review'
              : 'Please wait while we parse your character data...'}
          </p>
        </div>
        
        {/* Overall Progress */}
        <div className="mb-8 bg-gradient-to-br from-primary/5 to-accent/5 rounded-lg p-6 border border-border">
          <div className="flex items-center justify-between mb-3">
            <span className="text-lg font-bold text-foreground">Overall Progress</span>
            <span className="text-2xl font-bold text-primary">{progressPercentage}%</span>
          </div>
          <div className="w-full bg-muted rounded-full h-4 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-500"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
          <div className="mt-2 text-sm text-muted-foreground text-center">
            {completedCount} of {totalCount} parsers complete
          </div>
        </div>
        
        {/* Error Display */}
        {error && (
          <div className="mb-6 bg-destructive/10 border border-destructive/50 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <span className="text-destructive text-xl">⚠️</span>
              <div>
                <h3 className="font-bold text-destructive">Parsing Error</h3>
                <p className="text-destructive/90">{error}</p>
              </div>
            </div>
          </div>
        )}
        
        {/* Individual Parser Progress */}
        <div className="space-y-4 mb-8">
          {(Object.keys(PARSER_LABELS) as ParserName[]).map((parserName) => {
            const parser = parsers[parserName]
            return (
              <div
                key={parserName}
                className="bg-card border border-border rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{PARSER_ICONS[parserName]}</span>
                    <div>
                      <div className="font-bold text-foreground">
                        {PARSER_LABELS[parserName]}
                      </div>
                      <div className={`text-sm capitalize ${
                        parser.status === 'complete' ? 'text-primary' :
                        parser.status === 'in_progress' || parser.status === 'started' ? 'text-secondary' :
                        parser.status === 'error' ? 'text-destructive' :
                        'text-muted-foreground'
                      }`}>
                        {parser.status === 'in_progress' ? 'In Progress' : parser.status}
                      </div>
                    </div>
                  </div>
                  {parser.execution_time_ms && (
                    <span className="text-sm text-muted-foreground font-mono">
                      {parser.execution_time_ms.toFixed(0)}ms
                    </span>
                  )}
                </div>
                
                {/* Progress Bar */}
                <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-300 ${
                      parser.status === 'complete' ? 'bg-primary' :
                      parser.status === 'in_progress' || parser.status === 'started' ? 'bg-secondary' :
                      parser.status === 'error' ? 'bg-destructive' :
                      'bg-muted'
                    }`}
                    style={{
                      width:
                        parser.status === 'complete'
                          ? '100%'
                          : parser.status === 'started' || parser.status === 'in_progress'
                          ? '50%'
                          : '0%',
                    }}
                  />
                </div>
                
                {parser.message && (
                  <p className="mt-2 text-sm text-muted-foreground">{parser.message}</p>
                )}
              </div>
            )
          })}
        </div>
        
        {/* Character Summary (when complete) */}
        {allComplete && characterSummary && (
          <div className="bg-primary/5 border border-primary/20 rounded-lg p-6 mb-6">
            <div className="flex items-start gap-3 mb-4">
              <span className="text-3xl">🎉</span>
              <div>
                <h3 className="text-xl font-bold text-foreground mb-1">
                  Character Loaded Successfully!
                </h3>
                <p className="text-muted-foreground">Ready to review and customize</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 bg-card rounded-lg p-4 border border-border">
              <div>
                <span className="text-sm text-muted-foreground">Name</span>
                <p className="font-bold text-lg text-foreground">{characterSummary.name}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Race</span>
                <p className="font-bold text-lg text-foreground">{characterSummary.race}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Class</span>
                <p className="font-bold text-lg text-foreground">{characterSummary.character_class}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Level</span>
                <p className="font-bold text-lg text-foreground">{characterSummary.level}</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Hit Points</span>
                <p className="font-bold text-lg text-foreground">{characterSummary.hp} HP</p>
              </div>
              <div>
                <span className="text-sm text-muted-foreground">Armor Class</span>
                <p className="font-bold text-lg text-foreground">{characterSummary.ac} AC</p>
              </div>
            </div>
          </div>
        )}
        
        {/* Continue Button (only when complete) */}
        {allComplete && (
          <button
            onClick={onNext}
            className="w-full px-6 py-4 bg-gradient-to-r from-primary to-accent text-primary-foreground rounded-lg hover:opacity-90 font-bold text-lg transition-all transform hover:scale-105 active:scale-95 shadow-md"
          >
            Continue to Review & Edit →
          </button>
        )}
      </div>
    </div>
  )
}
