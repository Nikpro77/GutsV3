#Codeflix_Botz
#rohit_1888 on Tg

import motor, asyncio
import motor.motor_asyncio
import time
import pymongo, os
from config import DB_URI, DB_NAME
from bot import Bot
import logging
from datetime import datetime, timedelta

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

logging.basicConfig(level=logging.INFO)


class Rohit:

    def __init__(self, DB_URI, DB_NAME):
        self.dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        self.database = self.dbclient[DB_NAME]

        self.channel_data = self.database['channels']
        self.admins_data = self.database['admins']
        self.user_data = self.database['users']
        self.banned_user_data = self.database['banned_user']
        self.autho_user_data = self.database['autho_user']
        self.del_timer_data = self.database['del_timer']
        self.fsub_data = self.database['fsub']   
        self.rqst_fsub_data = self.database['request_forcesub']
        self.rqst_fsub_Channel_data = self.database['request_forcesub_channel']
        


    # USER DATA
    async def present_user(self, user_id: int):
        found = await self.user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_user(self, user_id: int):
        await self.user_data.insert_one({'_id': user_id})
        return

    async def full_userbase(self):
        user_docs = await self.user_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in user_docs]
        return user_ids

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})
        return


    # ADMIN DATA
    async def admin_exist(self, admin_id: int):
        found = await self.admins_data.find_one({'_id': admin_id})
        return bool(found)

    async def add_admin(self, admin_id: int):
        if not await self.admin_exist(admin_id):
            await self.admins_data.insert_one({'_id': admin_id})
            return

    async def del_admin(self, admin_id: int):
        if await self.admin_exist(admin_id):
            await self.admins_data.delete_one({'_id': admin_id})
            return

    async def get_all_admins(self):
        users_docs = await self.admins_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in users_docs]
        return user_ids


    # BAN USER DATA
    async def ban_user_exist(self, user_id: int):
        found = await self.banned_user_data.find_one({'_id': user_id})
        return bool(found)

    async def add_ban_user(self, user_id: int):
        if not await self.ban_user_exist(user_id):
            await self.banned_user_data.insert_one({'_id': user_id})
            return

    async def del_ban_user(self, user_id: int):
        if await self.ban_user_exist(user_id):
            await self.banned_user_data.delete_one({'_id': user_id})
            return

    async def get_ban_users(self):
        users_docs = await self.banned_user_data.find().to_list(length=None)
        user_ids = [doc['_id'] for doc in users_docs]
        return user_ids



    # AUTO DELETE TIMER SETTINGS
    async def set_del_timer(self, value: int):        
        existing = await self.del_timer_data.find_one({})
        if existing:
            await self.del_timer_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.del_timer_data.insert_one({'value': value})

    async def get_del_timer(self):
        data = await self.del_timer_data.find_one({})
        if data:
            return data.get('value', 600)
        return 0


    # CHANNEL MANAGEMENT
    async def channel_exist(self, channel_id: int):
        found = await self.fsub_data.find_one({'_id': channel_id})
        return bool(found)

    async def add_channel(self, channel_id: int):
        if not await self.channel_exist(channel_id):
            await self.fsub_data.insert_one({'_id': channel_id})
            return

    async def rem_channel(self, channel_id: int):
        if await self.channel_exist(channel_id):
            await self.fsub_data.delete_one({'_id': channel_id})
            return

    async def show_channels(self):
        channel_docs = await self.fsub_data.find().to_list(length=None)
        channel_ids = [doc['_id'] for doc in channel_docs]
        return channel_ids

    
# Get current mode of a channel
    async def get_channel_mode(self, channel_id: int):
        data = await self.fsub_data.find_one({'_id': channel_id})
        return data.get("mode", "off") if data else "off"

    # Set mode of a channel
    async def set_channel_mode(self, channel_id: int, mode: str):
        await self.fsub_data.update_one(
            {'_id': channel_id},
            {'$set': {'mode': mode}},
            upsert=True
        )

    # REQUEST FORCE-SUB MANAGEMENT

    # Add the user to the set of users for a   specific channel
    async def req_user(self, channel_id: int, user_id: int):
        try:
            await self.rqst_fsub_Channel_data.update_one(
                {'_id': int(channel_id)},
                {'$addToSet': {'user_ids': int(user_id)}},
                upsert=True
            )
        except Exception as e:
            print(f"[DB ERROR] Failed to add user to request list: {e}")


    # Method 2: Remove a user from the channel set
    async def del_req_user(self, channel_id: int, user_id: int):
        # Remove the user from the set of users for the channel
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id}, 
            {'$pull': {'user_ids': user_id}}
        )

    # Check if the user exists in the set of the channel's users
    async def req_user_exist(self, channel_id: int, user_id: int):
        try:
            found = await self.rqst_fsub_Channel_data.find_one({
                '_id': int(channel_id),
                'user_ids': int(user_id)
            })
            return bool(found)
        except Exception as e:
            print(f"[DB ERROR] Failed to check request list: {e}")
            return False  


    # Method to check if a channel exists using show_channels
    async def reqChannel_exist(self, channel_id: int):
    # Get the list of all channel IDs from the database
        channel_ids = await self.show_channels()
        #print(f"All channel IDs in the database: {channel_ids}")

    # Check if the given channel_id is in the list of channel IDs
        if channel_id in channel_ids:
            #print(f"Channel {channel_id} found in the database.")
            return True
        else:
            #print(f"Channel {channel_id} NOT found in the database.")
            return False

    # Method to clear all requests for a specific channel
    async def clear_channel_requests(self, channel_id: int):
        """
        Clears all user requests for a specific channel
        Returns the number of users removed
        """
        try:
            # Get the current document to count users
            channel_data = await self.rqst_fsub_Channel_data.find_one({'_id': int(channel_id)})
            user_count = len(channel_data.get('user_ids', [])) if channel_data else 0
            
            # Delete all user IDs for this channel by setting an empty array
            result = await self.rqst_fsub_Channel_data.update_one(
                {'_id': int(channel_id)},
                {'$set': {'user_ids': []}},
                upsert=True
            )
            
            return user_count
        except Exception as e:
            print(f"[DB ERROR] Failed to clear request list: {e}")
            return 0


db = Rohit(DB_URI, DB_NAME)

# +++ Modified By Yato [telegram username: @i_killed_my_clan & @ProYato] +++ # aNDI BANDI SANDI JISNE BHI CREDIT HATAYA USKI BANDI RAndi 
import motor.motor_asyncio
import base64
from config import DB_URI, DB_NAME
from datetime import datetime, timedelta
from typing import List, Optional

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]

# collections
user_data = database['users']
channels_collection = database['channels']
fsub_channels_collection = database['fsub_channels']

async def add_user(user_id: int) -> bool:
    """Add a user to the database if they don't exist."""
    if not isinstance(user_id, int) or user_id <= 0:
        print(f"Invalid user_id: {user_id}")
        return False
    
    try:
        existing_user = await user_data.find_one({'_id': user_id})
        if existing_user:
            return False
        
        await user_data.insert_one({'_id': user_id, 'created_at': datetime.utcnow()})
        return True
    except Exception as e:
        print(f"Error adding user {user_id}: {e}")
        return False

async def present_user(user_id: int) -> bool:
    """Check if a user exists in the database."""
    if not isinstance(user_id, int):
        return False
    return bool(await user_data.find_one({'_id': user_id}))

async def full_userbase() -> List[int]:
    """Get all user IDs from the database."""
    try:
        user_docs = user_data.find()
        return [doc['_id'] async for doc in user_docs]
    except Exception as e:
        print(f"Error fetching userbase: {e}")
        return []

async def del_user(user_id: int) -> bool:
    """Delete a user from the database."""
    try:
        result = await user_data.delete_one({'_id': user_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting user {user_id}: {e}")
        return False

async def is_admin(user_id: int) -> bool:
    """Check if a user is an admin."""
    admins_collection = database['admins']
    try:
        user_id = int(user_id)  # Ensure always int
        return bool(await admins_collection.find_one({'_id': user_id}))
    except Exception as e:
        print(f"Error checking admin status for {user_id}: {e}")
        return False

async def add_admin(user_id: int) -> bool:
    """Add a user as admin."""
    admins_collection = database['admins']
    try:
        user_id = int(user_id)  # Ensure always int
        await admins_collection.update_one({'_id': user_id}, {'$set': {'_id': user_id}}, upsert=True)
        return True
    except Exception as e:
        print(f"Error adding admin {user_id}: {e}")
        return False

async def remove_admin(user_id: int) -> bool:
    """Remove a user from admins."""
    admins_collection = database['admins']
    try:
        result = await admins_collection.delete_one({'_id': user_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error removing admin {user_id}: {e}")
        return False

async def list_admins() -> list:
    """List all admin user IDs."""
    admins_collection = database['admins']
    try:
        admins = await admins_collection.find().to_list(None)
        return [admin['_id'] for admin in admins]
    except Exception as e:
        print(f"Error listing admins: {e}")
        return []

async def save_channel(channel_id: int) -> bool:
    """Save a channel to the database with invite link expiration."""
    if not isinstance(channel_id, int):
        print(f"Invalid channel_id: {channel_id}")
        return False
    
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "channel_id": channel_id,
                    "invite_link_expiry": None,
                    "created_at": datetime.utcnow(),
                    "status": "active"
                }
            },
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error saving channel {channel_id}: {e}")
        return False

async def get_channels() -> List[int]:
    """Get all active channel IDs from the database."""
    try:
        channels = await channels_collection.find({"status": "active"}).to_list(None)
        valid_channels = []
        for channel in channels:
            if isinstance(channel, dict) and "channel_id" in channel:
                valid_channels.append(channel["channel_id"])
            else:
                print(f"Invalid channel document: {channel}")
        if not valid_channels:
            print(f"No valid channels found in database. Total documents checked: {len(channels)}")
        return valid_channels
    except Exception as e:
        print(f"Error fetching channels: {e}")
        return []

async def delete_channel(channel_id: int) -> bool:
    """Delete a channel from the database."""
    try:
        result = await channels_collection.delete_one({"channel_id": channel_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting channel {channel_id}: {e}")
        return False

async def save_encoded_link(channel_id: int) -> Optional[str]:
    """Save an encoded link for a channel and return it."""
    if not isinstance(channel_id, int):
        print(f"Invalid channel_id: {channel_id}")
        return None
    
    try:
        encoded_link = base64.urlsafe_b64encode(str(channel_id).encode()).decode()
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "encoded_link": encoded_link,
                    "status": "active",
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        return encoded_link
    except Exception as e:
        print(f"Error saving encoded link for channel {channel_id}: {e}")
        return None

async def get_channel_by_encoded_link(encoded_link: str) -> Optional[int]:
    """Get a channel ID by its encoded link."""
    if not isinstance(encoded_link, str):
        return None
    
    try:
        channel = await channels_collection.find_one({"encoded_link": encoded_link, "status": "active"})
        return channel["channel_id"] if channel and "channel_id" in channel else None
    except Exception as e:
        print(f"Error fetching channel by encoded link {encoded_link}: {e}")
        return None

async def save_encoded_link2(channel_id: int, encoded_link: str) -> Optional[str]:
    """Save a secondary encoded link for a channel."""
    if not isinstance(channel_id, int) or not isinstance(encoded_link, str):
        print(f"Invalid input: channel_id={channel_id}, encoded_link={encoded_link}")
        return None
    
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "req_encoded_link": encoded_link,
                    "status": "active",
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        return encoded_link
    except Exception as e:
        print(f"Error saving secondary encoded link for channel {channel_id}: {e}")
        return None

async def get_channel_by_encoded_link2(encoded_link: str) -> Optional[int]:
    """Get a channel ID by its secondary encoded link."""
    if not isinstance(encoded_link, str):
        return None
    
    try:
        channel = await channels_collection.find_one({"req_encoded_link": encoded_link, "status": "active"})
        return channel["channel_id"] if channel and "channel_id" in channel else None
    except Exception as e:
        print(f"Error fetching channel by secondary encoded link {encoded_link}: {e}")
        return None

async def save_invite_link(channel_id: int, invite_link: str, is_request: bool) -> bool:
    """Save the current invite link for a channel and its type."""
    if not isinstance(channel_id, int) or not isinstance(invite_link, str):
        print(f"Invalid input: channel_id={channel_id}, invite_link={invite_link}")
        return False
    
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {
                "$set": {
                    "current_invite_link": invite_link,
                    "is_request_link": is_request,
                    "invite_link_created_at": datetime.utcnow(),
                    "status": "active"
                }
            },
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error saving invite link for channel {channel_id}: {e}")
        return False

async def get_current_invite_link(channel_id: int) -> Optional[dict]:
    """Get the current invite link and its type for a channel."""
    if not isinstance(channel_id, int):
        return None
    
    try:
        channel = await channels_collection.find_one({"channel_id": channel_id, "status": "active"})
        if channel and "current_invite_link" in channel:
            return {
                "invite_link": channel["current_invite_link"],
                "is_request": channel.get("is_request_link", False)
            }
        return None
    except Exception as e:
        print(f"Error fetching current invite link for channel {channel_id}: {e}")
        return None

async def add_fsub_channel(channel_id: int) -> bool:
    """Add a channel to the FSub list."""
    if not isinstance(channel_id, int):
        print(f"Invalid channel_id: {channel_id}")
        return False
    
    try:
        existing_channel = await fsub_channels_collection.find_one({'channel_id': channel_id})
        if existing_channel:
            return False
        
        await fsub_channels_collection.insert_one({
            'channel_id': channel_id,
            'created_at': datetime.utcnow(),
            'status': 'active'
        })
        return True
    except Exception as e:
        print(f"Error adding FSub channel {channel_id}: {e}")
        return False

async def remove_fsub_channel(channel_id: int) -> bool:
    """Remove a channel from the FSub list."""
    try:
        result = await fsub_channels_collection.delete_one({'channel_id': channel_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error removing FSub channel {channel_id}: {e}")
        return False

async def get_fsub_channels() -> List[int]:
    """Get all active FSub channel IDs."""
    try:
        channels = await fsub_channels_collection.find({'status': 'active'}).to_list(None)
        return [channel['channel_id'] for channel in channels]
    except Exception as e:
        print(f"Error fetching FSub channels: {e}")
        return []

async def get_original_link(channel_id: int) -> Optional[str]:
    """Get the original link stored for a channel (used by /genlink)."""
    if not isinstance(channel_id, int):
        return None
    try:
        channel = await channels_collection.find_one({"channel_id": channel_id, "status": "active"})
        return channel.get("original_link") if channel and "original_link" in channel else None
    except Exception as e:
        print(f"Error fetching original link for channel {channel_id}: {e}")
        return None

async def set_approval_off(channel_id: int, off: bool = True) -> bool:
    """Set approval_off flag for a channel."""
    if not isinstance(channel_id, int):
        print(f"Invalid channel_id: {channel_id}")
        return False
    try:
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {"$set": {"approval_off": off}},
            upsert=True
        )
        return True
    except Exception as e:
        print(f"Error setting approval_off for channel {channel_id}: {e}")
        return False

async def is_approval_off(channel_id: int) -> bool:
    """Check if approval_off flag is set for a channel."""
    if not isinstance(channel_id, int):
        return False
    try:
        channel = await channels_collection.find_one({"channel_id": channel_id})
        return bool(channel and channel.get("approval_off", False))
    except Exception as e:
        print(f"Error checking approval_off for channel {channel_id}: {e}")
        return False
