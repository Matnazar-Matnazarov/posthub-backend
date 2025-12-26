"""WebSocket manager for real-time notifications."""

from typing import Dict, Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections for real-time notifications."""

    def __init__(self):
        # user_id -> set of websocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # All connections for broadcast
        self.all_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, user_id: int = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.all_connections.add(websocket)
        
        if user_id:
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()
            self.active_connections[user_id].add(websocket)
            logger.info(f"User {user_id} connected via WebSocket")

    def disconnect(self, websocket: WebSocket, user_id: int = None):
        """Remove a WebSocket connection."""
        self.all_connections.discard(websocket)
        
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user."""
        if user_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to user {user_id}: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, user_id)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        disconnected = set()
        for connection in self.all_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.add(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.all_connections.discard(conn)


# Global connection manager
manager = ConnectionManager()


async def notify_new_post(post_id: int, title: str, author_name: str):
    """Notify all users about a new post."""
    await manager.broadcast({
        "type": "new_post",
        "data": {
            "post_id": post_id,
            "title": title,
            "author": author_name,
            "message": f"Yangi post: {title}"
        }
    })


async def notify_new_comment(
    post_owner_id: int, 
    post_id: int, 
    post_title: str,
    commenter_name: str,
    comment_preview: str
):
    """Notify post owner about a new comment."""
    await manager.send_personal_message({
        "type": "new_comment",
        "data": {
            "post_id": post_id,
            "post_title": post_title,
            "commenter": commenter_name,
            "preview": comment_preview[:100],
            "message": f"{commenter_name} sizning postingizga izoh qoldirdi"
        }
    }, post_owner_id)


async def notify_new_like(
    post_owner_id: int,
    post_id: int,
    post_title: str,
    liker_name: str
):
    """Notify post owner about a new like."""
    await manager.send_personal_message({
        "type": "new_like",
        "data": {
            "post_id": post_id,
            "post_title": post_title,
            "liker": liker_name,
            "message": f"{liker_name} sizning postingizni yoqtirdi"
        }
    }, post_owner_id)

