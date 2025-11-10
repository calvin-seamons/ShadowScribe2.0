/**
 * Character Creation Page
 * 
 * Main route for the character creation wizard.
 * Import characters from D&D Beyond and customize every detail.
 */

'use client'

import { CharacterCreationWizard } from '@/components/character/CharacterCreationWizard'
import { LogoText } from '@/components/Logo'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

export default function CharacterCreatePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card shadow-sm">
        <div className="container mx-auto flex items-center justify-between p-4">
          <LogoText />
          <Link
            href="/"
            className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border hover:bg-muted transition-colors text-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
        </div>
      </header>
      
      {/* Wizard */}
      <CharacterCreationWizard />
    </div>
  )
}
