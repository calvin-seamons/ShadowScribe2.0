import { NextRequest, NextResponse } from 'next/server'

/**
 * Proxy endpoint for individual character operations
 * Forwards requests to backend API at localhost:8000
 */

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const characterId = params.id
    
    console.log(`[API Route] Forwarding GET to: ${apiUrl}/api/characters/${characterId}`)
    
    const response = await fetch(`${apiUrl}/api/characters/${characterId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
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

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json()
    const apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const characterId = params.id
    
    console.log(`[API Route] Forwarding PUT to: ${apiUrl}/api/characters/${characterId}`)
    
    const response = await fetch(`${apiUrl}/api/characters/${characterId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      return NextResponse.json(
        { error: errorData.detail || 'Failed to update character' },
        { status: response.status }
      )
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error proxying character update:', error)
    return NextResponse.json(
      { error: 'Failed to connect to backend API' },
      { status: 500 }
    )
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const characterId = params.id
    
    console.log(`[API Route] Forwarding DELETE to: ${apiUrl}/api/characters/${characterId}`)
    
    const response = await fetch(`${apiUrl}/api/characters/${characterId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }))
      return NextResponse.json(
        { error: errorData.detail || 'Failed to delete character' },
        { status: response.status }
      )
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error proxying character delete:', error)
    return NextResponse.json(
      { error: 'Failed to connect to backend API' },
      { status: 500 }
    )
  }
}
