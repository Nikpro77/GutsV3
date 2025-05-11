#Codeflix_Botz
#rohit_1888 on Tg

import motor, asyncio
import motor.motor_asyncio
import time
import pymongo, os
from config import DB_URI, DB_NAME
import logging
from datetime import datetime, timedelta

dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

logging.basicConfig(level=logging.INFO)

default_verify = {
    'is_verified': False,
    'verified_time': 0,
    'verify_token': "",
    'link': ""
}

def new_user(id):
    return {
        '_id': id,
        'verify_status': default_verify.copy()
    }

class Rohit:

    def __init__(self, DB_URI, DB_NAME):
        self.dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
        self.database = self.dbclient[DB_NAME]

        self.channel_data = self.database['channels']
        self.admins_data = self.database['admins']
        self.user_data = self.database['users']
        self.sex_data = self.database['sex']
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
        await self.user_data.insert_one(new_user(user_id))

    async def full_userbase(self):
        user_docs = await self.user_data.find().to_list(length=None)
        return [doc['_id'] for doc in user_docs]

    async def del_user(self, user_id: int):
        await self.user_data.delete_one({'_id': user_id})


    # ADMIN DATA
    async def admin_exist(self, admin_id: int):
        return bool(await self.admins_data.find_one({'_id': admin_id}))

    async def add_admin(self, admin_id: int):
        if not await self.admin_exist(admin_id):
            await self.admins_data.insert_one({'_id': admin_id})

    async def del_admin(self, admin_id: int):
        if await self.admin_exist(admin_id):
            await self.admins_data.delete_one({'_id': admin_id})

    async def get_all_admins(self):
        docs = await self.admins_data.find().to_list(length=None)
        return [doc['_id'] for doc in docs]


    # BAN USER DATA
    async def ban_user_exist(self, user_id: int):
        return bool(await self.banned_user_data.find_one({'_id': user_id}))

    async def add_ban_user(self, user_id: int):
        if not await self.ban_user_exist(user_id):
            await self.banned_user_data.insert_one({'_id': user_id})

    async def del_ban_user(self, user_id: int):
        if await self.ban_user_exist(user_id):
            await self.banned_user_data.delete_one({'_id': user_id})

    async def get_ban_users(self):
        docs = await self.banned_user_data.find().to_list(length=None)
        return [doc['_id'] for doc in docs]


    # AUTO DELETE TIMER
    async def set_del_timer(self, value: int):        
        existing = await self.del_timer_data.find_one({})
        if existing:
            await self.del_timer_data.update_one({}, {'$set': {'value': value}})
        else:
            await self.del_timer_data.insert_one({'value': value})

    async def get_del_timer(self):
        data = await self.del_timer_data.find_one({})
        return data.get('value', 600) if data else 0


    # FORCE SUB CHANNEL MANAGEMENT
    async def channel_exist(self, channel_id: int):
        return bool(await self.fsub_data.find_one({'_id': channel_id}))

    async def add_channel(self, channel_id: int):
        if not await self.channel_exist(channel_id):
            await self.fsub_data.insert_one({'_id': channel_id})

    async def rem_channel(self, channel_id: int):
        if await self.channel_exist(channel_id):
            await self.fsub_data.delete_one({'_id': channel_id})

    async def show_channels(self):
        docs = await self.fsub_data.find().to_list(length=None)
        return [doc['_id'] for doc in docs]

    async def get_channel_mode(self, channel_id: int):
        data = await self.fsub_data.find_one({'_id': channel_id})
        return data.get("mode", "off") if data else "off"

    async def set_channel_mode(self, channel_id: int, mode: str):
        await self.fsub_data.update_one({'_id': channel_id}, {'$set': {'mode': mode}}, upsert=True)


    # REQUEST FORCE SUB MANAGEMENT
    async def req_user(self, channel_id: int, user_id: int):
        try:
            await self.rqst_fsub_Channel_data.update_one(
                {'_id': channel_id},
                {'$addToSet': {'user_ids': user_id}},
                upsert=True
            )
        except Exception as e:
            print(f"[DB ERROR] Add req_user: {e}")

    async def del_req_user(self, channel_id: int, user_id: int):
        await self.rqst_fsub_Channel_data.update_one(
            {'_id': channel_id},
            {'$pull': {'user_ids': user_id}}
        )

    async def req_user_exist(self, channel_id: int, user_id: int):
        try:
            found = await self.rqst_fsub_Channel_data.find_one({
                '_id': channel_id,
                'user_ids': user_id
            })
            return bool(found)
        except Exception as e:
            print(f"[DB ERROR] Check req_user_exist: {e}")
            return False

    async def reqChannel_exist(self, channel_id: int):
        return channel_id in await self.show_channels()

    async def clear_channel_requests(self, channel_id: int):
        try:
            doc = await self.rqst_fsub_Channel_data.find_one({'_id': channel_id})
            count = len(doc.get('user_ids', [])) if doc else 0
            await self.rqst_fsub_Channel_data.update_one(
                {'_id': channel_id},
                {'$set': {'user_ids': []}},
                upsert=True
            )
            return count
        except Exception as e:
            print(f"[DB ERROR] Clear channel requests: {e}")
            return 0


    # VERIFICATION SYSTEM
    async def db_verify_status(self, user_id: int):
        user = await self.user_data.find_one({'_id': user_id})
        return user.get('verify_status', default_verify) if user else default_verify

    async def db_update_verify_status(self, user_id: int, verify: dict):
        await self.user_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}}, upsert=True)

    async def get_verify_status(self, user_id: int):
        return await self.db_verify_status(user_id)

    async def update_verify_status(self, user_id: int, verify_token="", is_verified=False, verified_time=0, link=""):
        current = await self.db_verify_status(user_id)
        current.update({
            'verify_token': verify_token,
            'is_verified': is_verified,
            'verified_time': verified_time,
            'link': link
        })
        await self.db_update_verify_status(user_id, current)

    async def set_verify_count(self, user_id: int, count: int):
        await self.sex_data.update_one({'_id': user_id}, {'$set': {'verify_count': count}}, upsert=True)

    async def get_verify_count(self, user_id: int):
        doc = await self.sex_data.find_one({'_id': user_id})
        return doc.get('verify_count', 0) if doc else 0

    async def reset_all_verify_counts(self):
        await self.sex_data.update_many({}, {'$set': {'verify_count': 0}})

    async def get_total_verify_count(self):
        pipeline = [{"$group": {"_id": None, "total": {"$sum": "$verify_count"}}}]
        result = await self.sex_data.aggregate(pipeline).to_list(length=1)
        return result[0]['total'] if result else 0


db = Rohit(DB_URI, DB_NAME)
