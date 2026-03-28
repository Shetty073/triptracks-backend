from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from typing import Dict, List, Optional
import json
from app.core.database import db
from app.api.auth import get_current_user
from app.models.user import UserDB
from datetime import datetime
import uuid

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        # Dictionary mapping trip_id to a list of active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, trip_id: str):
        await websocket.accept()
        if trip_id not in self.active_connections:
            self.active_connections[trip_id] = []
        self.active_connections[trip_id].append(websocket)

    def disconnect(self, websocket: WebSocket, trip_id: str):
        self.active_connections[trip_id].remove(websocket)
        if not self.active_connections[trip_id]:
            del self.active_connections[trip_id]

    async def broadcast_to_trip(self, message: str, trip_id: str):
        if trip_id not in self.active_connections:
            return
        dead = []
        for connection in list(self.active_connections[trip_id]):
            try:
                await connection.send_text(message)
            except Exception:
                dead.append(connection)
        for c in dead:
            try:
                self.active_connections[trip_id].remove(c)
            except ValueError:
                pass
        if not self.active_connections.get(trip_id):
            self.active_connections.pop(trip_id, None)

manager = ConnectionManager()

# In an actual prod environment, you would use JWT token extraction from Query parameters 
# since WebSockets don't easily support headers natively in all JS clients without subprotocols.
@router.websocket("/{trip_id}")
async def websocket_endpoint(websocket: WebSocket, trip_id: str, user_id: str = Query(...), username: str = Query(...)):
    await manager.connect(websocket, trip_id)
    
    # Notify others that this user joined
    join_msg = {
        "type": "system",
        "message": f"{username} joined the trip live view",
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast_to_trip(json.dumps(join_msg), trip_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Message could be a chat or a location update
            msg_type = message_data.get("type", "chat")
            
            broadcast_data = {
                "id": str(uuid.uuid4()),
                "type": msg_type,
                "user_id": user_id,
                "username": username,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if msg_type == "chat":
                broadcast_data["text"] = message_data.get("text", "")
                # Optional: Save chat history to DB
                await db.db["trip_chats"].insert_one({
                    **broadcast_data,
                    "trip_id": trip_id
                })
            elif msg_type == "location":
                broadcast_data["lat"] = message_data.get("lat")
                broadcast_data["lng"] = message_data.get("lng")
                # Location updates are usually ephemeral, but could be saved to track route history
                
            await manager.broadcast_to_trip(json.dumps(broadcast_data), trip_id)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, trip_id)
        leave_msg = {
            "type": "system",
            "message": f"{username} left the trip live view",
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.broadcast_to_trip(json.dumps(leave_msg), trip_id)

@router.get("/{trip_id}/history")
async def get_chat_history(
    trip_id: str,
    limit: int = 10,
    before_id: Optional[str] = None,
    current_user: UserDB = Depends(get_current_user),
):
    """Returns paginated chat messages for a trip, newest first, skipping system messages."""
    query: dict = {"trip_id": trip_id, "type": "chat"}

    if before_id:
        # Find the timestamp of the anchor message, then fetch older ones
        anchor = await db.db["trip_chats"].find_one({"id": before_id})
        if anchor:
            query["timestamp"] = {"$lt": anchor["timestamp"]}

    cursor = (
        db.db["trip_chats"]
        .find(query, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
    )
    messages = await cursor.to_list(length=limit)
    # Return in oldest-first order so the UI can prepend them naturally
    messages.reverse()
    return messages
