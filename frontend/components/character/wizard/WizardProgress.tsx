/**
 * Wizard Progress Indicator
 * 
 * Shows current step in the wizard with visual progress bar
 */

'use client'

interface WizardProgressProps {
  currentStep: number
  totalSteps: number
}

const STEP_LABELS = [
  'Import Character',
  'Parsing Data',
  'Review & Edit',
  'Save Character'
]

export function WizardProgress({ currentStep, totalSteps }: WizardProgressProps) {
  return (
    <div className="mb-8">
      {/* Step Labels */}
      <div className="flex justify-between mb-4">
        {Array.from({ length: totalSteps }, (_, i) => i + 1).map((step) => (
          <div
            key={step}
            className={`flex-1 text-center ${
              step === currentStep
                ? 'text-foreground font-bold'
                : step < currentStep
                ? 'text-primary'
                : 'text-muted-foreground'
            }`}
          >
            <div className="flex items-center justify-center mb-2">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold ${
                  step === currentStep
                    ? 'bg-primary text-primary-foreground ring-4 ring-primary/20'
                    : step < currentStep
                    ? 'bg-primary/80 text-primary-foreground'
                    : 'bg-muted text-muted-foreground'
                }`}
              >
                {step < currentStep ? '✓' : step}
              </div>
            </div>
            <div className="text-sm hidden sm:block">{STEP_LABELS[step - 1]}</div>
          </div>
        ))}
      </div>
      
      {/* Progress Bar */}
      <div className="relative">
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary to-accent transition-all duration-500"
            style={{ width: `${((currentStep - 1) / (totalSteps - 1)) * 100}%` }}
          />
        </div>
      </div>
      
      {/* Mobile Step Label */}
      <div className="text-center mt-4 sm:hidden">
        <span className="text-foreground font-medium">
          {STEP_LABELS[currentStep - 1]}
        </span>
      </div>
    </div>
  )
}
