import { NextRequest, NextResponse } from 'next/server'

/**
 * Proxy endpoint for D&D Beyond character fetching
 * Forwards requests to backend API at localhost:8000
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Server-side API URL (use Docker service name in container, localhost for local dev)
    // API_URL is server-side only, NEXT_PUBLIC_API_URL is client-side
    const apiUrl = process.env.API_URL || 'http://localhost:8000'
    
    console.log(`[API Route] Forwarding to: ${apiUrl}/api/characters/fetch`)
    
    const response = await fetch(`${apiUrl}/api/characters/fetch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      return NextResponse.json(
        { error: errorData.detail || 'Failed to fetch character' },
        { status: response.status }
      )
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error proxying character fetch:', error)
    return NextResponse.json(
      { error: 'Failed to connect to backend API' },
      { status: 500 }
    )
  }
}
