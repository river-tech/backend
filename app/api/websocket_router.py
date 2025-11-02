from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from uuid import UUID
import logging

from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()

async def get_current_user_from_ws_token(token: str, db: Session):
    """Get current user from JWT token in WebSocket"""
    try:
        from app.services.auth import decode_access_token
        from app.models.user import User
        
        if not token or len(token) < 10:  # Basic validation
            logger.warning("Invalid token format")
            return None
        
        payload = decode_access_token(token)
        if not payload:
            logger.warning("Failed to decode token")
            return None
            
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("No user_id in token payload")
            return None
        
        user = db.query(User).filter(User.id == UUID(user_id)).first()
        if not user:
            logger.warning(f"User not found: {user_id}")
        return user
    except Exception as e:
        logger.error(f"Error authenticating WebSocket token: {str(e)}")
        return None

@router.websocket("/ws/wallet/{token}")
async def wallet_status_websocket(websocket: WebSocket, token: str):
    """WebSocket endpoint for wallet status updates (user connects)"""
    from app.db.database import SessionLocal
    db = SessionLocal()
    user = None
    
    try:
        # Accept connection first (required for WebSocket handshake)
        await websocket.accept()
        
        # Authenticate user from token after accepting
        user = await get_current_user_from_ws_token(token, db)
        if not user:
            await websocket.close(code=1008, reason="Unauthorized")
            return
        
        # Connect to manager (connection already accepted)
        await manager.connect(websocket, str(user.id), already_accepted=True)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to wallet status updates",
            "user_id": str(user.id)
        })
        
        # Keep connection alive and listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                # Echo back for ping/pong
                await websocket.send_json({
                    "type": "pong",
                    "data": data
                })
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    finally:
        if user:
            manager.disconnect(websocket, str(user.id))
        db.close()

@router.websocket("/ws/notifications/{token}")
async def notifications_websocket(websocket: WebSocket, token: str):
    """WebSocket endpoint for notifications (user or admin connects)"""
    from app.db.database import SessionLocal
    db = SessionLocal()
    user = None
    
    try:
        # Accept connection first (required for WebSocket handshake)
        await websocket.accept()
        
        # Authenticate user from token
        user = await get_current_user_from_ws_token(token, db)
        if not user:
            await websocket.close(code=1008, reason="Unauthorized")
            return
        
        # Connect to manager (connection already accepted)
        await manager.connect(websocket, str(user.id), already_accepted=True)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to notifications",
            "user_id": str(user.id),
            "role": user.role
        })
        
        # Keep connection alive and listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                # Echo back for ping/pong
                await websocket.send_json({
                    "type": "pong",
                    "data": data
                })
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    finally:
        if user:
            manager.disconnect(websocket, str(user.id))
        db.close()

@router.websocket("/ws/admin/deposits/{token}")
async def admin_deposits_websocket(websocket: WebSocket, token: str):
    """WebSocket endpoint for admin to receive new deposit requests"""
    from app.db.database import SessionLocal
    db = SessionLocal()
    user = None
    
    try:
        # Accept connection first (required for WebSocket handshake)
        await websocket.accept()
        
        # Authenticate user from token
        user = await get_current_user_from_ws_token(token, db)
        if not user:
            await websocket.close(code=1008, reason="Unauthorized")
            return
        
        # Check if user is admin
        if user.role != "ADMIN":
            await websocket.close(code=1008, reason="Admin access required")
            return
        
        # Connect to manager (connection already accepted)
        await manager.connect(websocket, str(user.id), already_accepted=True)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to admin deposit requests",
            "user_id": str(user.id),
            "role": user.role
        })
        
        # Keep connection alive and listen for messages
        while True:
            try:
                data = await websocket.receive_text()
                # Echo back for ping/pong
                await websocket.send_json({
                    "type": "pong",
                    "data": data
                })
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    finally:
        if user:
            manager.disconnect(websocket, str(user.id))
        db.close()

