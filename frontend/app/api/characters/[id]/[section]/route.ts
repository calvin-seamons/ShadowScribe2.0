import { NextRequest, NextResponse } from 'next/server'

/**
 * Proxy endpoint for character section updates
 * Forwards PATCH requests to backend API at localhost:8000
 */

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string; section: string } }
) {
  try {
    const body = await request.json()
    const apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const { id: characterId, section } = params
    
    console.log(`[API Route] Forwarding PATCH to: ${apiUrl}/api/characters/${characterId}/${section}`)
    
    const response = await fetch(`${apiUrl}/api/characters/${characterId}/${section}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      console.error('[API Route] Backend error:', errorData)
      return NextResponse.json(
        { error: errorData.detail || 'Failed to update section' },
        { status: response.status }
      )
    }
    
    const data = await response.json()
    console.log(`[API Route] Section ${section} updated successfully`)
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error proxying section update:', error)
    return NextResponse.json(
      { error: 'Failed to connect to backend API' },
      { status: 500 }
    )
  }
}
