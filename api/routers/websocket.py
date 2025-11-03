"""WebSocket router for real-time chat."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import json
import uuid
from typing import Dict

from api.database.connection import get_db
from api.services.chat_service import ChatService

router = APIRouter()

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    
    connection_id = str(uuid.uuid4())
    active_connections[connection_id] = websocket
    
    # Initialize chat service
    chat_service = ChatService()
    
    async def emit_metadata(event_type: str, data: dict):
        """Callback to emit metadata events to the client."""
        await websocket.send_json({
            'type': event_type,
            'data': data
        })
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Extract message details
            message_type = message_data.get('type')
            
            if message_type == 'ping':
                await websocket.send_json({'type': 'pong'})
                continue
            
            if message_type == 'clear_history':
                character_name = message_data.get('character_name')
                if character_name:
                    chat_service.clear_conversation_history(character_name)
                    await websocket.send_json({'type': 'history_cleared'})
                continue
            
            user_message = message_data.get('message')
            character_name = message_data.get('character_name')
            
            # Validate input
            if not user_message or not character_name:
                await websocket.send_json({
                    'type': 'error',
                    'error': 'Missing required fields: message, character_name'
                })
                continue
            
            # Send acknowledgment
            await websocket.send_json({'type': 'message_received'})
            
            # Stream response from CentralEngine
            try:
                async for chunk in chat_service.process_query_stream(
                    user_message, 
                    character_name,
                    metadata_callback=emit_metadata
                ):
                    await websocket.send_json({
                        'type': 'response_chunk',
                        'content': chunk
                    })
                
                # Send completion signal
                await websocket.send_json({'type': 'response_complete'})
                
            except Exception as e:
                await websocket.send_json({
                    'type': 'error',
                    'error': f'Error processing query: {str(e)}'
                })
    
    except WebSocketDisconnect:
        print(f"Client disconnected: {connection_id}")
    except Exception as e:
        print(f"Error in WebSocket connection: {str(e)}")
        try:
            await websocket.send_json({
                'type': 'error',
                'error': str(e)
            })
        except:
            pass
    finally:
        # Clean up connection
        if connection_id in active_connections:
            del active_connections[connection_id]
        try:
            await websocket.close()
        except:
            pass
