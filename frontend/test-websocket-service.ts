/**
 * Test script for WebSocket character creation service
 * 
 * This is a Node.js test script to verify the WebSocketService
 * can properly handle character creation events.
 * 
 * Run with: npx tsx frontend/test-websocket-service.ts
 */

import { WebSocket } from 'ws'

// Mock WebSocket for Node.js environment
(global as any).WebSocket = WebSocket

const WS_URL = 'ws://localhost:8000'
const TEST_CHARACTER_URL = 'https://www.dndbeyond.com/characters/152248393'

interface CharacterCreationEvent {
  type: string
  [key: string]: any
}

async function testCharacterCreation() {
  console.log('🧪 Testing WebSocket Character Creation Service')
  console.log('=' .repeat(60))
  
  return new Promise<void>((resolve, reject) => {
    const ws = new WebSocket(`${WS_URL}/ws/character/create`)
    const events: CharacterCreationEvent[] = []
    let startTime = Date.now()
    
    ws.onopen = () => {
      console.log('✅ WebSocket connected')
      console.log(`📤 Sending create_character message with URL: ${TEST_CHARACTER_URL}`)
      
      ws.send(JSON.stringify({
        type: 'create_character',
        url: TEST_CHARACTER_URL
      }))
      
      startTime = Date.now()
    }
    
    ws.onmessage = (event: any) => {
      try {
        const data = JSON.parse(event.data.toString()) as CharacterCreationEvent
        events.push(data)
        
        const elapsed = Date.now() - startTime
        
        switch (data.type) {
          case 'fetch_started':
            console.log(`\n📥 [${elapsed}ms] Fetching character from D&D Beyond...`)
            break
          
          case 'fetch_complete':
            console.log(`✅ [${elapsed}ms] Fetch complete: ${data.character_name}`)
            break
          
          case 'parser_started':
            console.log(`▶️  [${elapsed}ms] Parser started: ${data.parser} (${data.completed}/${data.total})`)
            break
          
          case 'parser_complete':
            console.log(`✅ [${elapsed}ms] Parser complete: ${data.parser} (${data.execution_time_ms}ms) (${data.completed}/${data.total})`)
            break
          
          case 'assembly_started':
            console.log(`\n🔧 [${elapsed}ms] Assembling character...`)
            break
          
          case 'creation_complete':
            console.log(`\n🎉 [${elapsed}ms] Character creation complete!`)
            console.log('\nCharacter Summary:')
            console.log(`  Name: ${data.character_summary.name}`)
            console.log(`  Race: ${data.character_summary.race}`)
            console.log(`  Class: ${data.character_summary.character_class}`)
            console.log(`  Level: ${data.character_summary.level}`)
            console.log(`  HP: ${data.character_summary.hp}`)
            console.log(`  AC: ${data.character_summary.ac}`)
            
            console.log('\n📊 Event Summary:')
            console.log(`  Total events: ${events.length}`)
            console.log(`  Total time: ${elapsed}ms`)
            
            ws.close()
            resolve()
            break
          
          case 'creation_error':
            console.error(`\n❌ Error: ${data.error}`)
            if (data.parser) {
              console.error(`  Failed parser: ${data.parser}`)
            }
            ws.close()
            reject(new Error(data.error))
            break
        }
      } catch (error) {
        console.error('❌ Error parsing message:', error)
        reject(error)
      }
    }
    
    ws.onerror = (error: any) => {
      console.error('❌ WebSocket error:', error.message)
      reject(error)
    }
    
    ws.onclose = () => {
      console.log('\n🔌 WebSocket closed')
      console.log('=' .repeat(60))
    }
    
    // Timeout after 30 seconds
    setTimeout(() => {
      ws.close()
      reject(new Error('Test timeout after 30 seconds'))
    }, 30000)
  })
}

// Run the test
testCharacterCreation()
  .then(() => {
    console.log('\n✅ TEST PASSED')
    process.exit(0)
  })
  .catch((error) => {
    console.error('\n❌ TEST FAILED:', error.message)
    process.exit(1)
  })
