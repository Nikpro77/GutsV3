# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#

import asyncio
import os
import random
import sys
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatInviteLink, ChatPrivileges
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import *
from helper_func import *
from database.database import *


#=====================================================================================##

REPLY_ERROR = "<code>Use this command as a reply to any telegram message without any spaces.</code>"

#=====================================================================================##


@Bot.on_message(filters.private & filters.command('pbroadcast') & admin)
async def send_pin_text(client: Bot, message: Message):
    if message.reply_to_message:
        # Dictionary to track active broadcasts
        if not hasattr(client, "active_broadcasts"):
            client.active_broadcasts = {}
            
        # Create a unique ID for this broadcast
        broadcast_id = str(int(time.time()))
        client.active_broadcasts[broadcast_id] = True
        
        query = await db.full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        # Create cancel button
        cancel_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel Broadcast", callback_data=f"cancel_broadcast_{broadcast_id}")]
        ])
        
        pls_wait = await message.reply("<i>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘʀᴏᴄᴇꜱꜱɪɴɢ....</i>", reply_markup=cancel_button)
        
        for chat_id in query:
            # Check if broadcast has been cancelled
            if not client.active_broadcasts.get(broadcast_id, False):
                await pls_wait.edit("<b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")
                break
                
            try:
                # Send and pin the message
                sent_msg = await broadcast_msg.copy(chat_id)
                await client.pin_chat_message(chat_id=chat_id, message_id=sent_msg.id, both_sides=True)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                sent_msg = await broadcast_msg.copy(chat_id)
                await client.pin_chat_message(chat_id=chat_id, message_id=sent_msg.id, both_sides=True)
                successful += 1
            except UserIsBlocked:
                await db.del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await db.del_user(chat_id)
                deleted += 1
            except Exception as e:
                print(f"Failed to send or pin message to {chat_id}: {e}")
                unsuccessful += 1
                
            total += 1
            
            # Update status every 25 users
            if total % 25 == 0:
                status = f"""<b><u>ᴘɪɴ ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ...</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
                await pls_wait.edit(status, reply_markup=cancel_button)

        # Remove broadcast from active broadcasts
        if broadcast_id in client.active_broadcasts:
            del client.active_broadcasts[broadcast_id]

        status = f"""<b><u>ᴘɪɴ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</u></b>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code>"""

        return await pls_wait.edit(status)

    else:
        msg = await message.reply("<code>Reply to a message to broadcast and pin it.</code>")
        await asyncio.sleep(8)
        await msg.delete()

#=====================================================================================##


@Bot.on_message(filters.private & filters.command('broadcast') & admin)
async def send_text(client: Bot, message: Message):
    if message.reply_to_message:
        # Dictionary to track active broadcasts
        if not hasattr(client, "active_broadcasts"):
            client.active_broadcasts = {}
            
        # Create a unique ID for this broadcast
        broadcast_id = str(int(time.time()))
        client.active_broadcasts[broadcast_id] = True
        
        query = await db.full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        # Create cancel button
        cancel_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel Broadcast", callback_data=f"cancel_broadcast_{broadcast_id}")]
        ])
        
        pls_wait = await message.reply("<i>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘʀᴏᴄᴇꜱꜱɪɴɢ....</i>", reply_markup=cancel_button)
        
        for chat_id in query:
            # Check if broadcast has been cancelled
            if not client.active_broadcasts.get(broadcast_id, False):
                await pls_wait.edit("<b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")
                break
                
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await db.del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await db.del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
                
            total += 1
            
            # Update status every 25 users
            if total % 25 == 0:
                status = f"""<b><u>ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ...</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
                await pls_wait.edit(status, reply_markup=cancel_button)

        # Remove broadcast from active broadcasts
        if broadcast_id in client.active_broadcasts:
            del client.active_broadcasts[broadcast_id]

        status = f"""<b><u>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</u></b>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code>"""

        return await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()

#=====================================================================================##


@Bot.on_message(filters.private & filters.command('dbroadcast') & admin)
async def delete_broadcast(client: Bot, message: Message):
    if message.reply_to_message:
        try:
            duration = int(message.command[1])  # Get the duration in seconds
        except (IndexError, ValueError):
            await message.reply("<b>Pʟᴇᴀsᴇ ᴜsᴇ ᴀ ᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ ɪɴ sᴇᴄᴏɴᴅs.</b> Usᴀɢᴇ: /dbroadcast {duration}")
            return

        # Dictionary to track active broadcasts
        if not hasattr(client, "active_broadcasts"):
            client.active_broadcasts = {}
            
        # Create a unique ID for this broadcast
        broadcast_id = str(int(time.time()))
        client.active_broadcasts[broadcast_id] = True
        
        query = await db.full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        # Create cancel button
        cancel_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel Broadcast", callback_data=f"cancel_broadcast_{broadcast_id}")]
        ])
        
        pls_wait = await message.reply("<i>Broadcast with auto-delete processing....</i>", reply_markup=cancel_button)
        
        for chat_id in query:
            # Check if broadcast has been cancelled
            if not client.active_broadcasts.get(broadcast_id, False):
                await pls_wait.edit("<b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")
                break
                
            try:
                sent_msg = await broadcast_msg.copy(chat_id)
                # Create a task for deletion so we don't block the broadcast loop
                asyncio.create_task(delete_after_duration(sent_msg, duration))
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                sent_msg = await broadcast_msg.copy(chat_id)
                asyncio.create_task(delete_after_duration(sent_msg, duration))
                successful += 1
            except UserIsBlocked:
                await db.del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await db.del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
                
            total += 1
            
            # Update status every 25 users
            if total % 25 == 0:
                status = f"""<b><u>ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ...</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
                await pls_wait.edit(status, reply_markup=cancel_button)

        # Remove broadcast from active broadcasts
        if broadcast_id in client.active_broadcasts:
            del client.active_broadcasts[broadcast_id]

        status = f"""<b><u>ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</u></b>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code>"""

        return await pls_wait.edit(status)

    else:
        msg = await message.reply("<code>Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ ɪᴛ ᴡɪᴛʜ Aᴜᴛᴏ-Dᴇʟᴇᴛᴇ.</code>")
        await asyncio.sleep(8)
        await msg.delete()

#=====================================================================================##


@Bot.on_message(filters.private & filters.command('fbroadcast') & admin)
async def forward_broadcast(client: Bot, message: Message):
    if message.reply_to_message:
        # Dictionary to track active broadcasts
        if not hasattr(client, "active_broadcasts"):
            client.active_broadcasts = {}
            
        # Create a unique ID for this broadcast
        broadcast_id = str(int(time.time()))
        client.active_broadcasts[broadcast_id] = True
        
        query = await db.full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        # Create cancel button
        cancel_button = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel Broadcast", callback_data=f"cancel_broadcast_{broadcast_id}")]
        ])
        
        pls_wait = await message.reply("<i>ғᴏʀᴡᴀʀᴅ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘʀᴏᴄᴇꜱꜱɪɴɢ....</i>", reply_markup=cancel_button)
        
        for chat_id in query:
            # Check if broadcast has been cancelled
            if not client.active_broadcasts.get(broadcast_id, False):
                await pls_wait.edit("<b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")
                break
                
            try:
                # Forward the message instead of copying it
                await broadcast_msg.forward(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.forward(chat_id)
                successful += 1
            except UserIsBlocked:
                await db.del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await db.del_user(chat_id)
                deleted += 1
            except Exception as e:
                print(f"Failed to forward message to {chat_id}: {e}")
                unsuccessful += 1
            
            total += 1
            
            # Update status every 25 users
            if total % 25 == 0:
                status = f"""<b><u>ғᴏʀᴡᴀʀᴅ ʙʀᴏᴀᴅᴄᴀꜱᴛ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ...</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""
                await pls_wait.edit(status, reply_markup=cancel_button)

        # Remove broadcast from active broadcasts
        if broadcast_id in client.active_broadcasts:
            del client.active_broadcasts[broadcast_id]
            
        final_status = f"""<b><u>ғᴏʀᴡᴀʀᴅ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</u></b>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code>"""

        return await pls_wait.edit(final_status)

    else:
        msg = await message.reply("<code>Reply to a message to forward broadcast it to all users.</code>")
        await asyncio.sleep(8)
        await msg.delete()

#=====================================================================================##


# Helper function for auto-delete broadcast
async def delete_after_duration(message, duration):
    await asyncio.sleep(duration)
    try:
        await message.delete()
    except Exception as e:
        print(f"Failed to delete message: {e}")

#=====================================================================================##


# Handle cancel broadcast callback
@Bot.on_callback_query(filters.regex(r"^cancel_broadcast_(.+)"))
async def cancel_broadcast_callback(client: Bot, callback: CallbackQuery):
    # Extract broadcast ID from callback data
    broadcast_id = callback.data.split("_")[-1]
    
    
    
    # Initialize active_broadcasts if not exists
    if not hasattr(client, "active_broadcasts"):
        client.active_broadcasts = {}
    
    # Cancel the broadcast
    if broadcast_id in client.active_broadcasts:
        client.active_broadcasts[broadcast_id] = False
        await callback.answer("Broadcast will be cancelled shortly.", show_alert=True)
    else:
        await callback.answer("This broadcast is no longer active.", show_alert=True)

#=====================================================================================##

# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport
#
# Copyright (C) 2025 by Codeflix-Bots@Github, < https://github.com/Codeflix-Bots >.
#
# This file is part of < https://github.com/Codeflix-Bots/FileStore > project,
# and is released under the MIT License.
# Please see < https://github.com/Codeflix-Bots/FileStore/blob/master/LICENSE >
#
# All rights reserved.
#
