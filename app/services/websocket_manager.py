from typing import Dict, Set
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for users"""
    
    def __init__(self):
        # user_id -> set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str, already_accepted: bool = False):
        """Connect a user's websocket"""
        if not already_accepted:
            await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        logger.info(f"User {user_id} connected to WebSocket. Total connections: {len(self.active_connections[user_id])}")
        
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Disconnect a user's websocket"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            logger.info(f"User {user_id} disconnected from WebSocket. Remaining connections: {len(self.active_connections[user_id])}")
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                logger.info(f"User {user_id} has no active connections")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user"""
        if user_id in self.active_connections:
            disconnected = set()
            sent_count = 0
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                    sent_count += 1
                except Exception as e:
                    logger.warning(f"Failed to send message to user {user_id}: {str(e)}")
                    disconnected.add(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            
            logger.info(f"Sent wallet status update to user {user_id}: {sent_count} connection(s)")
        else:
            logger.warning(f"User {user_id} has no active WebSocket connections. Message not sent.")
    
    async def broadcast_to_all_users(self, message: dict):
        """Broadcast message to all connected users"""
        disconnected_users = []
        total_sent = 0
        for user_id, connections in self.active_connections.items():
            disconnected = set()
            for connection in connections:
                try:
                    await connection.send_json(message)
                    total_sent += 1
                except Exception as e:
                    logger.warning(f"Failed to broadcast to user {user_id}: {str(e)}")
                    disconnected.add(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                connections.discard(conn)
            if not connections:
                disconnected_users.append(user_id)
        
        # Clean up empty user connections
        for user_id in disconnected_users:
            del self.active_connections[user_id]
        
        logger.info(f"Broadcast message sent to {total_sent} connection(s)")

# Global instance
manager = ConnectionManager()

