# Merged DB Handler
# Credits: Codeflix_Botz + Yato

import motor.motor_asyncio
import pymongo
from config import DB_URI, DB_NAME
from datetime import datetime
from typing import List, Optional
import base64
import logging

logging.basicConfig(level=logging.INFO)


class DBHandler:
    def __init__(self, DB_URI, DB_NAME):
        # Mongo clients
        self.sync_client = pymongo.MongoClient(DB_URI)
        self.async_client = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        self.database = self.async_client[DB_NAME]

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

    # ---------------- USER DATA ----------------
    async def present_user(self, user_id: int) -> bool:
        return bool(await self.user_data.find_one({"_id": user_id}))

    async def add_user(self, user_id: int) -> bool:
        if not await self.present_user(user_id):
            await self.user_data.insert_one({"_id": user_id, "created_at": datetime.utcnow()})
            return True
        return False

    async def full_userbase(self) -> List[int]:
        users = await self.user_data.find().to_list(length=None)
        return [doc["_id"] for doc in users]

    async def del_user(self, user_id: int) -> bool:
        result = await self.user_data.delete_one({"_id": user_id})
        return result.deleted_count > 0

    # ---------------- ADMIN DATA ----------------
    async def is_admin(self, admin_id: int) -> bool:
        return bool(await self.admins_data.find_one({"_id": admin_id}))

    async def add_admin(self, admin_id: int) -> bool:
        await self.admins_data.update_one(
            {"_id": admin_id}, {"$set": {"_id": admin_id}}, upsert=True
        )
        return True

    async def del_admin(self, admin_id: int) -> bool:
        result = await self.admins_data.delete_one({"_id": admin_id})
        return result.deleted_count > 0

    async def get_all_admins(self) -> List[int]:
        admins = await self.admins_data.find().to_list(length=None)
        return [doc["_id"] for doc in admins]

    # ---------------- BANNED USERS ----------------
    async def ban_user_exist(self, user_id: int) -> bool:
        return bool(await self.banned_user_data.find_one({"_id": user_id}))

    async def add_ban_user(self, user_id: int) -> bool:
        if not await self.ban_user_exist(user_id):
            await self.banned_user_data.insert_one({"_id": user_id})
            return True
        return False

    async def del_ban_user(self, user_id: int) -> bool:
        result = await self.banned_user_data.delete_one({"_id": user_id})
        return result.deleted_count > 0

    async def get_ban_users(self) -> List[int]:
        users = await self.banned_user_data.find().to_list(length=None)
        return [doc["_id"] for doc in users]

    # ---------------- DELETE TIMER ----------------
    async def set_del_timer(self, value: int):
        await self.del_timer_data.update_one({}, {"$set": {"value": value}}, upsert=True)

    async def get_del_timer(self) -> int:
        data = await self.del_timer_data.find_one({})
        return data.get("value", 600) if data else 600

    # ---------------- CHANNEL MANAGEMENT ----------------
    async def save_channel(self, channel_id: int) -> bool:
        await self.channels_data.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "channel_id": channel_id,
                    "invite_link_expiry": None,
                    "created_at": datetime.utcnow(),
                    "status": "active",
                }
            },
            upsert=True,
        )
        return True

    async def get_channels(self) -> List[int]:
        channels = await self.channels_data.find({"status": "active"}).to_list(None)
        return [c["channel_id"] for c in channels if "channel_id" in c]

    async def delete_channel(self, channel_id: int) -> bool:
        result = await self.channels_data.delete_one({"channel_id": channel_id})
        return result.deleted_count > 0

    # ---------------- CHANNEL EXTRA FEATURES ----------------
    async def save_encoded_link(self, channel_id: int) -> Optional[str]:
        encoded = base64.urlsafe_b64encode(str(channel_id).encode()).decode()
        await self.channels_data.update_one(
            {"channel_id": channel_id},
            {"$set": {"encoded_link": encoded, "updated_at": datetime.utcnow()}},
            upsert=True,
        )
        return encoded

    async def get_channel_by_encoded_link(self, encoded: str) -> Optional[int]:
        ch = await self.channels_data.find_one({"encoded_link": encoded, "status": "active"})
        return ch["channel_id"] if ch else None

    async def save_invite_link(self, channel_id: int, invite_link: str, is_request: bool) -> bool:
        await self.channels_data.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "current_invite_link": invite_link,
                    "is_request_link": is_request,
                    "invite_link_created_at": datetime.utcnow(),
                }
            },
            upsert=True,
        )
        return True

    async def get_current_invite_link(self, channel_id: int) -> Optional[dict]:
        ch = await self.channels_data.find_one({"channel_id": channel_id, "status": "active"})
        if ch and "current_invite_link" in ch:
            return {"invite_link": ch["current_invite_link"], "is_request": ch.get("is_request_link", False)}
        return None

    async def get_original_link(self, channel_id: int) -> Optional[str]:
        ch = await self.channels_data.find_one({"channel_id": channel_id, "status": "active"})
        return ch.get("original_link") if ch else None

    async def set_approval_off(self, channel_id: int, off: bool = True) -> bool:
        await self.channels_data.update_one(
            {"channel_id": channel_id}, {"$set": {"approval_off": off}}, upsert=True
        )
        return True

    async def is_approval_off(self, channel_id: int) -> bool:
        ch = await self.channels_data.find_one({"channel_id": channel_id})
        return bool(ch and ch.get("approval_off", False))

    # ---------------- F-SUB ----------------
    async def add_fsub_channel(self, channel_id: int) -> bool:
        if not await self.fsub_data.find_one({"_id": channel_id}):
            await self.fsub_data.insert_one({"_id": channel_id, "status": "active"})
            return True
        return False

    async def remove_fsub_channel(self, channel_id: int) -> bool:
        result = await self.fsub_data.delete_one({"_id": channel_id})
        return result.deleted_count > 0

    async def get_fsub_channels(self) -> List[int]:
        channels = await self.fsub_data.find({"status": "active"}).to_list(None)
        return [c["_id"] for c in channels]

    async def get_channel_mode(self, channel_id: int) -> str:
        data = await self.fsub_data.find_one({"_id": channel_id})
        return data.get("mode", "off") if data else "off"

    async def set_channel_mode(self, channel_id: int, mode: str):
        await self.fsub_data.update_one(
            {"_id": channel_id}, {"$set": {"mode": mode}}, upsert=True
        )

    # ---------------- REQUEST FORCE-SUB ----------------
    async def req_user(self, channel_id: int, user_id: int):
        await self.rqst_fsub_channel_data.update_one(
            {"_id": int(channel_id)},
            {"$addToSet": {"user_ids": int(user_id)}},
            upsert=True,
        )

    async def del_req_user(self, channel_id: int, user_id: int):
        await self.rqst_fsub_channel_data.update_one(
            {"_id": channel_id}, {"$pull": {"user_ids": user_id}}
        )

    async def req_user_exist(self, channel_id: int, user_id: int) -> bool:
        found = await self.rqst_fsub_channel_data.find_one(
            {"_id": int(channel_id), "user_ids": int(user_id)}
        )
        return bool(found)

    async def clear_channel_requests(self, channel_id: int) -> int:
        doc = await self.rqst_fsub_channel_data.find_one({"_id": int(channel_id)})
        count = len(doc.get("user_ids", [])) if doc else 0
        await self.rqst_fsub_channel_data.update_one(
            {"_id": int(channel_id)}, {"$set": {"user_ids": []}}, upsert=True
        )
        return count


# Create global DB object
db = DBHandler(DB_URI, DB_NAME)
