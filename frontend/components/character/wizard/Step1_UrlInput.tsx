/**
 * Step 1: URL Input
 * 
 * User enters D&D Beyond character URL to fetch character data
 */

'use client'

import { useState } from 'react'

interface Step1_UrlInputProps {
  onFetch: (url: string) => Promise<void>
  onNext: () => void
}

export function Step1_UrlInput({ onFetch, onNext }: Step1_UrlInputProps) {
  const [url, setUrl] = useState('https://www.dndbeyond.com/characters/152248393')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const handleFetch = async () => {
    if (!url.trim()) {
      setError('Please enter a D&D Beyond URL')
      return
    }
    
    // Basic URL validation
    if (!url.includes('dndbeyond.com/characters/')) {
      setError('Invalid D&D Beyond URL. Expected format: https://dndbeyond.com/characters/{id}')
      return
    }
    
    setLoading(true)
    setError(null)
    
    try {
      await onFetch(url)
      // Note: onNext is called automatically by parent component after successful fetch
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch character')
    } finally {
      setLoading(false)
    }
  }
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) {
      handleFetch()
    }
  }
  
  return (
    <div className="p-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-foreground mb-2">
            Import from D&D Beyond
          </h2>
          <p className="text-muted-foreground">
            Enter your D&D Beyond character URL to get started
          </p>
        </div>
        
        {/* URL Input */}
        <div className="space-y-4">
          <div>
            <label htmlFor="dndbeyond-url" className="block text-sm font-medium text-foreground mb-2">
              D&D Beyond Character URL
            </label>
            <input
              id="dndbeyond-url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="https://dndbeyond.com/characters/152248393"
              className="w-full px-4 py-3 bg-input border border-border rounded-lg focus:ring-2 focus:ring-ring focus:border-transparent text-lg text-foreground placeholder:text-muted-foreground"
              disabled={loading}
            />
            <p className="mt-2 text-sm text-muted-foreground">
              You can find this URL in your D&D Beyond character page
            </p>
          </div>
          
          {/* Error Display */}
          {error && (
            <div className="bg-destructive/10 border border-destructive/50 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <span className="text-destructive text-xl">⚠️</span>
                <div>
                  <h3 className="font-bold text-destructive">Error</h3>
                  <p className="text-destructive/90">{error}</p>
                </div>
              </div>
            </div>
          )}
          
          {/* Action Button */}
          <button
            onClick={handleFetch}
            disabled={loading || !url.trim()}
            className="w-full px-6 py-4 bg-gradient-to-r from-primary to-accent text-primary-foreground rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed font-bold text-lg transition-all transform hover:scale-105 active:scale-95 shadow-md"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                Fetching Character...
              </span>
            ) : (
              'Fetch Character'
            )}
          </button>
        </div>
        
        {/* Help Section */}
        <div className="mt-8 p-4 bg-muted rounded-lg border border-border">
          <h3 className="font-bold text-foreground mb-2">How to find your character URL:</h3>
          <ol className="list-decimal list-inside space-y-1 text-sm text-muted-foreground">
            <li>Go to D&D Beyond and open your character sheet</li>
            <li>Copy the URL from your browser's address bar</li>
            <li>Paste it above and click "Fetch Character"</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
