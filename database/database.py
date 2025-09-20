# Merged DB Handler
# Credits: Codeflix_Botz + Yato

import motor.motor_asyncio
import pymongo
from config import DB_URI, DB_NAME
from datetime import datetime
from typing import List, Optional, Dict, Any
import base64
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DBHandler:
    def __init__(self, db_uri: str, db_name: str):
        """Initialize database handler with proper connection management."""
        try:
            # Async client for async operations
            self.async_client = motor.motor_asyncio.AsyncIOMotorClient(
                db_uri,
                maxPoolSize=50,  # Optimize connection pool
                minPoolSize=10,
                maxIdleTimeMS=30000,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000
            )
            
            # Sync client for initialization checks only
            self.sync_client = pymongo.MongoClient(
                db_uri,
                serverSelectionTimeoutMS=5000
            )
            
            self.database = self.async_client[db_name]
            
            # Collections
            self.user_data = self.database["users"]
            self.admins_data = self.database["admins"]
            self.banned_user_data = self.database["banned_user"]
            self.autho_user_data = self.database["autho_user"]
            self.del_timer_data = self.database["del_timer"]
            self.channels_data = self.database["channels"]
            self.fsub_data = self.database["fsub"]
            self.rqst_fsub_data = self.database["request_forcesub"]
            self.rqst_fsub_channel_data = self.database["request_forcesub_channel"]
            
            logger.info("Database handler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database handler: {e}")
            raise

    async def close_connections(self):
        """Properly close database connections."""
        try:
            if hasattr(self, 'async_client'):
                self.async_client.close()
            if hasattr(self, 'sync_client'):
                self.sync_client.close()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")

    # ---------------- CONNECTION HEALTH ----------------
    async def ping_database(self) -> bool:
        """Check if database connection is healthy."""
        try:
            await self.database.command("ping")
            return True
        except Exception as e:
            logger.error(f"Database ping failed: {e}")
            return False

    # ---------------- USER DATA ----------------
    async def present_user(self, user_id: int) -> bool:
        """Check if user exists in database."""
        try:
            result = await self.user_data.find_one({"_id": user_id})
            return result is not None
        except Exception as e:
            logger.error(f"Error checking user presence {user_id}: {e}")
            return False

    async def add_user(self, user_id: int) -> bool:
        """Add new user to database."""
        try:
            if not await self.present_user(user_id):
                await self.user_data.insert_one({
                    "_id": user_id, 
                    "created_at": datetime.utcnow()
                })
                logger.info(f"Added new user: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False

    async def full_userbase(self) -> List[int]:
        """Get all user IDs from database."""
        try:
            cursor = self.user_data.find({}, {"_id": 1})
            users = await cursor.to_list(length=None)
            return [doc["_id"] for doc in users]
        except Exception as e:
            logger.error(f"Error fetching userbase: {e}")
            return []

    async def del_user(self, user_id: int) -> bool:
        """Delete user from database."""
        try:
            result = await self.user_data.delete_one({"_id": user_id})
            if result.deleted_count > 0:
                logger.info(f"Deleted user: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False

    async def get_users_count(self) -> int:
        """Get total user count."""
        try:
            return await self.user_data.count_documents({})
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0

    # ---------------- ADMIN DATA ----------------
    async def is_admin(self, admin_id: int) -> bool:
        """Check if user is admin."""
        try:
            result = await self.admins_data.find_one({"_id": admin_id})
            return result is not None
        except Exception as e:
            logger.error(f"Error checking admin status {admin_id}: {e}")
            return False

    async def add_admin(self, admin_id: int) -> bool:
        """Add admin to database."""
        try:
            await self.admins_data.update_one(
                {"_id": admin_id}, 
                {"$set": {"_id": admin_id, "added_at": datetime.utcnow()}}, 
                upsert=True
            )
            logger.info(f"Added admin: {admin_id}")
            return True
        except Exception as e:
            logger.error(f"Error adding admin {admin_id}: {e}")
            return False

    async def del_admin(self, admin_id: int) -> bool:
        """Remove admin from database."""
        try:
            result = await self.admins_data.delete_one({"_id": admin_id})
            if result.deleted_count > 0:
                logger.info(f"Removed admin: {admin_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing admin {admin_id}: {e}")
            return False

    async def get_all_admins(self) -> List[int]:
        """Get all admin IDs."""
        try:
            cursor = self.admins_data.find({}, {"_id": 1})
            admins = await cursor.to_list(length=None)
            return [doc["_id"] for doc in admins]
        except Exception as e:
            logger.error(f"Error fetching admins: {e}")
            return []

    # ---------------- BANNED USERS ----------------
    async def ban_user_exist(self, user_id: int) -> bool:
        """Check if user is banned."""
        try:
            result = await self.banned_user_data.find_one({"_id": user_id})
            return result is not None
        except Exception as e:
            logger.error(f"Error checking ban status {user_id}: {e}")
            return False

    async def add_ban_user(self, user_id: int, reason: str = None) -> bool:
        """Ban user with optional reason."""
        try:
            if not await self.ban_user_exist(user_id):
                ban_data = {
                    "_id": user_id,
                    "banned_at": datetime.utcnow()
                }
                if reason:
                    ban_data["reason"] = reason
                
                await self.banned_user_data.insert_one(ban_data)
                logger.info(f"Banned user: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error banning user {user_id}: {e}")
            return False

    async def del_ban_user(self, user_id: int) -> bool:
        """Unban user."""
        try:
            result = await self.banned_user_data.delete_one({"_id": user_id})
            if result.deleted_count > 0:
                logger.info(f"Unbanned user: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error unbanning user {user_id}: {e}")
            return False

    async def get_ban_users(self) -> List[int]:
        """Get all banned user IDs."""
        try:
            cursor = self.banned_user_data.find({}, {"_id": 1})
            users = await cursor.to_list(length=None)
            return [doc["_id"] for doc in users]
        except Exception as e:
            logger.error(f"Error fetching banned users: {e}")
            return []

    # ---------------- DELETE TIMER ----------------
    async def set_del_timer(self, value: int) -> bool:
        """Set auto-delete timer value."""
        try:
            await self.del_timer_data.update_one(
                {}, 
                {"$set": {"value": value, "updated_at": datetime.utcnow()}}, 
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error setting delete timer: {e}")
            return False

    async def get_del_timer(self) -> int:
        """Get auto-delete timer value."""
        try:
            data = await self.del_timer_data.find_one({})
            return data.get("value", 600) if data else 600
        except Exception as e:
            logger.error(f"Error getting delete timer: {e}")
            return 600

    # ---------------- CHANNEL MANAGEMENT ----------------
    async def save_channel(self, channel_id: int, title: str = None) -> bool:
        """Save channel to database."""
        try:
            channel_data = {
                "channel_id": channel_id,
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            if title:
                channel_data["title"] = title

            await self.channels_data.update_one(
                {"channel_id": channel_id},
                {"$set": channel_data},
                upsert=True
            )
            logger.info(f"Saved channel: {channel_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving channel {channel_id}: {e}")
            return False

    async def get_channels(self) -> List[int]:
        """Get all active channel IDs."""
        try:
            cursor = self.channels_data.find(
                {"status": "active"}, 
                {"channel_id": 1}
            )
            channels = await cursor.to_list(length=None)
            return [c["channel_id"] for c in channels if "channel_id" in c]
        except Exception as e:
            logger.error(f"Error fetching channels: {e}")
            return []

    async def delete_channel(self, channel_id: int) -> bool:
        """Delete channel from database."""
        try:
            result = await self.channels_data.delete_one({"channel_id": channel_id})
            if result.deleted_count > 0:
                logger.info(f"Deleted channel: {channel_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting channel {channel_id}: {e}")
            return False

    # ---------------- CHANNEL EXTRA FEATURES ----------------
    async def save_encoded_link(self, channel_id: int) -> Optional[str]:
        """Generate and save encoded link for channel."""
        try:
            encoded = base64.urlsafe_b64encode(str(channel_id).encode()).decode()
            await self.channels_data.update_one(
                {"channel_id": channel_id},
                {
                    "$set": {
                        "encoded_link": encoded, 
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            return encoded
        except Exception as e:
            logger.error(f"Error saving encoded link for {channel_id}: {e}")
            return None

    async def get_channel_by_encoded_link(self, encoded: str) -> Optional[int]:
        """Get channel ID by encoded link."""
        try:
            ch = await self.channels_data.find_one({
                "encoded_link": encoded, 
                "status": "active"
            })
            return ch["channel_id"] if ch else None
        except Exception as e:
            logger.error(f"Error getting channel by encoded link: {e}")
            return None

    async def save_invite_link(self, channel_id: int, invite_link: str, is_request: bool = False) -> bool:
        """Save invite link for channel."""
        try:
            await self.channels_data.update_one(
                {"channel_id": channel_id},
                {
                    "$set": {
                        "current_invite_link": invite_link,
                        "is_request_link": is_request,
                        "invite_link_created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error saving invite link for {channel_id}: {e}")
            return False

    async def get_current_invite_link(self, channel_id: int) -> Optional[Dict[str, Any]]:
        """Get current invite link for channel."""
        try:
            ch = await self.channels_data.find_one({
                "channel_id": channel_id, 
                "status": "active"
            })
            if ch and "current_invite_link" in ch:
                return {
                    "invite_link": ch["current_invite_link"], 
                    "is_request": ch.get("is_request_link", False)
                }
            return None
        except Exception as e:
            logger.error(f"Error getting invite link for {channel_id}: {e}")
            return None

    async def get_original_link(self, channel_id: int) -> Optional[str]:
        """Get original link for channel."""
        try:
            ch = await self.channels_data.find_one({
                "channel_id": channel_id, 
                "status": "active"
            })
            return ch.get("original_link") if ch else None
        except Exception as e:
            logger.error(f"Error getting original link for {channel_id}: {e}")
            return None

    async def set_approval_off(self, channel_id: int, off: bool = True) -> bool:
        """Set approval status for channel."""
        try:
            await self.channels_data.update_one(
                {"channel_id": channel_id}, 
                {
                    "$set": {
                        "approval_off": off,
                        "updated_at": datetime.utcnow()
                    }
                }, 
                upsert=True
            )
            logger.info(f"Set approval_off={off} for channel {channel_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting approval for {channel_id}: {e}")
            return False

    async def is_approval_off(self, channel_id: int) -> bool:
        """Check if approval is off for channel."""
        try:
            ch = await self.channels_data.find_one({"channel_id": channel_id})
            return bool(ch and ch.get("approval_off", False))
        except Exception as e:
            logger.error(f"Error checking approval status for {channel_id}: {e}")
            return False

    # ---------------- F-SUB ----------------
    async def add_fsub_channel(self, channel_id: int) -> bool:
        """Add force subscribe channel."""
        try:
            existing = await self.fsub_data.find_one({"_id": channel_id})
            if not existing:
                await self.fsub_data.insert_one({
                    "_id": channel_id, 
                    "status": "active",
                    "added_at": datetime.utcnow()
                })
                logger.info(f"Added fsub channel: {channel_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding fsub channel {channel_id}: {e}")
            return False

    async def remove_fsub_channel(self, channel_id: int) -> bool:
        """Remove force subscribe channel."""
        try:
            result = await self.fsub_data.delete_one({"_id": channel_id})
            if result.deleted_count > 0:
                logger.info(f"Removed fsub channel: {channel_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing fsub channel {channel_id}: {e}")
            return False

    async def get_fsub_channels(self) -> List[int]:
        """Get all force subscribe channels."""
        try:
            cursor = self.fsub_data.find({"status": "active"}, {"_id": 1})
            channels = await cursor.to_list(length=None)
            return [c["_id"] for c in channels]
        except Exception as e:
            logger.error(f"Error fetching fsub channels: {e}")
            return []

    async def get_channel_mode(self, channel_id: int) -> str:
        """Get channel mode."""
        try:
            data = await self.fsub_data.find_one({"_id": channel_id})
            return data.get("mode", "off") if data else "off"
        except Exception as e:
            logger.error(f"Error getting channel mode for {channel_id}: {e}")
            return "off"

    async def set_channel_mode(self, channel_id: int, mode: str) -> bool:
        """Set channel mode."""
        try:
            await self.fsub_data.update_one(
                {"_id": channel_id}, 
                {
                    "$set": {
                        "mode": mode,
                        "updated_at": datetime.utcnow()
                    }
                }, 
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error setting channel mode for {channel_id}: {e}")
            return False

    # ---------------- REQUEST FORCE-SUB ----------------
    async def req_user(self, channel_id: int, user_id: int) -> bool:
        """Add user to channel request list."""
        try:
            await self.rqst_fsub_channel_data.update_one(
                {"_id": int(channel_id)},
                {
                    "$addToSet": {"user_ids": int(user_id)},
                    "$set": {"updated_at": datetime.utcnow()}
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error adding request user {user_id} to {channel_id}: {e}")
            return False

    async def del_req_user(self, channel_id: int, user_id: int) -> bool:
        """Remove user from channel request list."""
        try:
            result = await self.rqst_fsub_channel_data.update_one(
                {"_id": channel_id}, 
                {
                    "$pull": {"user_ids": user_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error removing request user {user_id} from {channel_id}: {e}")
            return False

    async def req_user_exist(self, channel_id: int, user_id: int) -> bool:
        """Check if user exists in channel request list."""
        try:
            found = await self.rqst_fsub_channel_data.find_one({
                "_id": int(channel_id), 
                "user_ids": int(user_id)
            })
            return bool(found)
        except Exception as e:
            logger.error(f"Error checking request user {user_id} in {channel_id}: {e}")
            return False

    async def clear_channel_requests(self, channel_id: int) -> int:
        """Clear all requests for a channel."""
        try:
            doc = await self.rqst_fsub_channel_data.find_one({"_id": int(channel_id)})
            count = len(doc.get("user_ids", [])) if doc else 0
            
            await self.rqst_fsub_channel_data.update_one(
                {"_id": int(channel_id)}, 
                {
                    "$set": {
                        "user_ids": [],
                        "cleared_at": datetime.utcnow()
                    }
                }, 
                upsert=True
            )
            logger.info(f"Cleared {count} requests for channel {channel_id}")
            return count
        except Exception as e:
            logger.error(f"Error clearing requests for {channel_id}: {e}")
            return 0

    async def get_request_count(self, channel_id: int) -> int:
        """Get pending request count for channel."""
        try:
            doc = await self.rqst_fsub_channel_data.find_one({"_id": int(channel_id)})
            return len(doc.get("user_ids", [])) if doc else 0
        except Exception as e:
            logger.error(f"Error getting request count for {channel_id}: {e}")
            return 0


# Create global DB object with proper error handling
try:
    db = DBHandler(DB_URI, DB_NAME)
    logger.info("Global database handler created successfully")
except Exception as e:
    logger.critical(f"Failed to create global database handler: {e}")
    raise


# Utility function for graceful shutdown
async def cleanup_database():
    """Cleanup database connections on shutdown."""
    try:
        await db.close_connections()
    except Exception as e:
        logger.error(f"Error during database cleanup: {e}")
