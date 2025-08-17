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

BAN_SUPPORT = f"{BAN_SUPPORT}"

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    # Check if user is banned
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        return await message.reply_text(
            "<b>⛔️ You are Bᴀɴɴᴇᴅ from using this bot.</b>\n\n"
            "<i>Contact support if you think this is a mistake.</i>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Contact Support", url=BAN_SUPPORT)]]
            )
        )

    m = await message.reply_text("♻️")
    await asyncio.sleep(0.5)
    await m.edit_text("<code>Checking.</code>")
    await asyncio.sleep(0.4)
    await m.edit_text("<code>Checking..</code>")
    await asyncio.sleep(0.4)
    await m.edit_text("<code>Checking...</code>")
    await asyncio.sleep(0.6)
    await m.delete()
    
    # ✅ Check Force Subscription
    if not await is_subscribed(client, user_id):
        #await temp.delete()
        return await not_joined(client, message)

    # File auto-delete time in seconds (Set your desired time in seconds here)
    FILE_AUTO_DELETE = await db.get_del_timer()  # Example: 3600 seconds (1 hour)

    # Add user if not already present
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
        except:
            pass

    # Handle normal message flow
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except IndexError:
            return

        string = await decode(base64_string)
        argument = string.split("-")

        ids = []
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
            except Exception as e:
                print(f"Error decoding IDs: {e}")
                return

        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except Exception as e:
                print(f"Error decoding ID: {e}")
                return

        temp_msg = await message.reply("<b>Please wait...</b>")
        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await message.reply_text("Something went wrong!")
            print(f"Error getting messages: {e}")
            return
        finally:
            await temp_msg.delete()

        codeflix_msgs = []
        for msg in messages:
            caption = (CUSTOM_CAPTION.format(previouscaption="" if not msg.caption else msg.caption.html, 
                                             filename=msg.document.file_name) if bool(CUSTOM_CAPTION) and bool(msg.document)
                       else ("" if not msg.caption else msg.caption.html))

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, 
                                            reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                codeflix_msgs.append(copied_msg)
            except FloodWait as e:
                await asyncio.sleep(e.x)
                copied_msg = await msg.copy(chat_id=message.from_user.id, caption=caption, parse_mode=ParseMode.HTML, 
                                            reply_markup=reply_markup, protect_content=PROTECT_CONTENT)
                codeflix_msgs.append(copied_msg)
            except Exception as e:
                print(f"Failed to send message: {e}")
                pass

        if FILE_AUTO_DELETE > 0:
            notification_msg = await message.reply(
                f"<b>Tʜɪs Fɪʟᴇ ᴡɪʟʟ ʙᴇ Dᴇʟᴇᴛᴇᴅ ɪɴ  {get_exp_time(FILE_AUTO_DELETE)}. Pʟᴇᴀsᴇ sᴀᴠᴇ ᴏʀ ғᴏʀᴡᴀʀᴅ ɪᴛ ᴛᴏ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ʙᴇғᴏʀᴇ ɪᴛ ɢᴇᴛs Dᴇʟᴇᴛᴇᴅ.</b>"
            )

            await asyncio.sleep(FILE_AUTO_DELETE)

            for snt_msg in codeflix_msgs:    
                if snt_msg:
                    try:    
                        await snt_msg.delete()  
                    except Exception as e:
                        print(f"Error deleting message {snt_msg.id}: {e}")

            try:
                reload_url = (
                    f"https://t.me/{client.username}?start={message.command[1]}"
                    if message.command and len(message.command) > 1
                    else None
                )
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=reload_url)]]
                ) if reload_url else None

                await notification_msg.edit(
                    "<b>ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ ɪꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ !!\n\nᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ᴅᴇʟᴇᴛᴇᴅ ᴠɪᴅᴇᴏ / ꜰɪʟᴇ 👇</b>",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"Error updating notification with 'Get File Again' button: {e}")
    else:
        # 🚀 ENHANCED UI WITH MORE BUTTONS
        reply_markup = InlineKeyboardMarkup(
            [
                # Row 1: Main Network Button (Full Width)
                [InlineKeyboardButton("🌐 ᴀs ɴᴇᴛᴡᴏʀᴋs", url="https://t.me/as_networks")],
                
                # Row 2: Content Channels (2 buttons)
                [
                    InlineKeyboardButton("🎭 ᴀɴɪᴍᴇ sᴛᴀᴛɪᴏɴ", url="https://t.me/+fD0wqOhZnqNmZmQ9"),
                    InlineKeyboardButton("🎬 ᴍᴏᴠɪᴇs sᴛᴀᴛɪᴏɴ", url="https://t.me/+x9G79j7Cc2QyYjc1")
                ],
                
                # Row 3: Additional Channels (2 buttons)
                [
                    InlineKeyboardButton("🔞 ᴀᴅᴜʟᴛs sᴛᴀᴛɪᴏɴ", url="https://t.me/Adults_Station"),
                    InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇs", url="https://t.me/Animes_station")
                ],
                
                # Row 4: Bot Information (2 buttons)
                [
                    InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about"),
                    InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="help")
                ],
                
                # Row 5: Additional Features (2 buttons)
                [
                    InlineKeyboardButton("📊 ʙᴏᴛ sᴛᴀᴛᴜs", callback_data="stats"),
                    InlineKeyboardButton("👤 ᴍʏ ɪɴғᴏ", callback_data="my_info")
                ],
                
                # Row 6: Support and Contact (2 buttons)
                [
                    InlineKeyboardButton("🛠️ sᴜᴘᴘᴏʀᴛ", url="https://t.me/CodeflixSupport"),
                    InlineKeyboardButton("💬 ɢʀᴏᴜᴘ ᴄʜᴀᴛ", callback_data="group_chat")
                ]
            ]
        )
        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            message_effect_id=5104841245755180586)  # 🔥
        
        return


# 📝 CALLBACK HANDLERS FOR NEW BUTTONS
@Bot.on_callback_query(filters.regex(r'^stats$'))
async def bot_stats_callback(client: Client, callback_query: CallbackQuery):
    """Handle bot stats callback"""
    try:
        # Get total users count
        total_users = len(await db.full_userbase())
        
        # Get bot uptime (you might need to track this globally)
        uptime = "Bot is running smoothly! 🚀"
        
        stats_text = f"""
📊 <b>Bot Statistics</b>

👥 <b>Total Users:</b> <code>{total_users}</code>
⏰ <b>Status:</b> <code>{uptime}</code>
🤖 <b>Bot Version:</b> <code>v2.0</code>
🔥 <b>Server:</b> <code>Online</code>
        """
        
        back_button = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")
        ]])
        
        await callback_query.message.edit_caption(
            caption=stats_text,
            reply_markup=back_button
        )
    except Exception as e:
        await callback_query.answer("❌ Error loading stats!", show_alert=True)

@Bot.on_callback_query(filters.regex(r'^my_info$'))
async def my_info_callback(client: Client, callback_query: CallbackQuery):
    """Handle user info callback"""
    try:
        user = callback_query.from_user
        user_info = f"""
👤 <b>Your Information</b>

🆔 <b>User ID:</b> <code>{user.id}</code>
👨‍💻 <b>Name:</b> {user.first_name} {user.last_name or ''}
🔗 <b>Username:</b> @{user.username if user.username else 'Not set'}
🌟 <b>Status:</b> Premium User ⭐
📅 <b>Joined:</b> Member since start!
        """
        
        back_button = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")
        ]])
        
        await callback_query.message.edit_caption(
            caption=user_info,
            reply_markup=back_button
        )
    except Exception as e:
        await callback_query.answer("❌ Error loading your info!", show_alert=True)

@Bot.on_callback_query(filters.regex(r'^group_chat$'))
async def group_chat_callback(client: Client, callback_query: CallbackQuery):
    """Handle group chat callback"""
    group_chat_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Join Group Chat", url="https://t.me/CodeflixSupport")],
        [InlineKeyboardButton("📢 Join Updates Channel", url="https://t.me/Animes_station")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_start")]
    ])
    
    group_text = """
💬 <b>Join Our Community</b>

Connect with other users and get latest updates!

🔹 <b>Group Chat:</b> Ask questions, share feedback
🔹 <b>Updates Channel:</b> Get latest news and features
🔹 <b>Support:</b> Get help from our team

<i>Click the buttons below to join!</i>
    """
    
    await callback_query.message.edit_caption(
        caption=group_text,
        reply_markup=group_chat_buttons
    )

@Bot.on_callback_query(filters.regex(r'^back_to_start$'))
async def back_to_start_callback(client: Client, callback_query: CallbackQuery):
    """Handle back to start menu callback"""
    try:
        # Recreate the original start menu
        reply_markup = InlineKeyboardMarkup(
            [
                # Row 1: Main Network Button (Full Width)
                [InlineKeyboardButton("🌐 ᴀs ɴᴇᴛᴡᴏʀᴋs", url="https://t.me/as_networks")],
                
                # Row 2: Content Channels (2 buttons)
                [
                    InlineKeyboardButton("🎭 ᴀɴɪᴍᴇ sᴛᴀᴛɪᴏɴ", url="https://t.me/+fD0wqOhZnqNmZmQ9"),
                    InlineKeyboardButton("🎬 ᴍᴏᴠɪᴇs sᴛᴀᴛɪᴏɴ", url="https://t.me/+x9G79j7Cc2QyYjc1")
                ],
                
                # Row 3: Additional Channels (2 buttons)
                [
                    InlineKeyboardButton("🔞 ᴀᴅᴜʟᴛs sᴛᴀᴛɪᴏɴ", url="https://t.me/Adults_Station"),
                    InlineKeyboardButton("📢 ᴜᴘᴅᴀᴛᴇs", url="https://t.me/Animes_station")
                ],
                
                # Row 4: Bot Information (2 buttons)
                [
                    InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about"),
                    InlineKeyboardButton("❓ ʜᴇʟᴘ", callback_data="help")
                ],
                
                # Row 5: Additional Features (2 buttons)
                [
                    InlineKeyboardButton("📊 ʙᴏᴛ sᴛᴀᴛᴜs", callback_data="stats"),
                    InlineKeyboardButton("👤 ᴍʏ ɪɴғᴏ", callback_data="my_info")
                ],
                
                # Row 6: Support and Contact (2 buttons)
                [
                    InlineKeyboardButton("🛠️ sᴜᴘᴘᴏʀᴛ", url="https://t.me/CodeflixSupport"),
                    InlineKeyboardButton("💬 ɢʀᴏᴜᴘ ᴄʜᴀᴛ", callback_data="group_chat")
                ]
            ]
        )
        
        await callback_query.message.edit_caption(
            caption=START_MSG.format(
                first=callback_query.from_user.first_name,
                last=callback_query.from_user.last_name,
                username=None if not callback_query.from_user.username else '@' + callback_query.from_user.username,
                mention=callback_query.from_user.mention,
                id=callback_query.from_user.id
            ),
            reply_markup=reply_markup
        )
    except Exception as e:
        await callback_query.answer("❌ Error loading menu!", show_alert=True)


#=====================================================================================##
# Don't Remove Credit @CodeFlix_Bots, @rohit_1888
# Ask Doubt on telegram @CodeflixSupport



# Create a global dictionary to store chat data
chat_data_cache = {}

async def not_joined(client: Client, message: Message):
    temp = await message.reply("<b><i>ᴡᴀɪᴛ ᴀ sᴇᴄ..</i></b>")

    user_id = message.from_user.id
    buttons = []
    count = 0

    try:
        all_channels = await db.show_channels()  # Should return list of (chat_id, mode) tuples
        for total, chat_id in enumerate(all_channels, start=1):
            mode = await db.get_channel_mode(chat_id)  # fetch mode 

            await message.reply_chat_action(ChatAction.TYPING)

            if not await is_sub(client, user_id, chat_id):
                try:
                    # Cache chat info
                    if chat_id in chat_data_cache:
                        data = chat_data_cache[chat_id]
                    else:
                        data = await client.get_chat(chat_id)
                        chat_data_cache[chat_id] = data

                    name = data.title

                    # Simplified check - just use the username as indicator for public/private
                    is_public = bool(data.username)
                    
                    # Generate appropriate invite link
                    try:
                        if not is_public and mode == "on":
                            # Private channel with join request mode
                            invite = await client.create_chat_invite_link(
                                chat_id=chat_id,
                                creates_join_request=True,
                                expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY) if FSUB_LINK_EXPIRY else None
                            )
                        else:
                            # Public channel or private channel without join request
                            invite = await client.create_chat_invite_link(
                                chat_id=chat_id,
                                expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY) if FSUB_LINK_EXPIRY else None
                            )
                        link = invite.invite_link
                    except Exception as e:
                        print(f"Failed to create invite link: {e}")
                        # Fallback to username link only if generating invite link fails
                        if data.username:
                            link = f"https://t.me/{data.username}"
                        else:
                            raise  # Re-raise the exception if no fallback available

                    buttons.append([InlineKeyboardButton(text=name, url=link)])
                    count += 1
                    await temp.edit(f"<b>{'! ' * count}</b>")

                except Exception as e:
                    print(f"Error with chat {chat_id}: {e}")
                    return await temp.edit(
                        f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @rohit_1888</i></b>\n"
                        f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
                    )

        # Retry Button
        try:
            buttons.append([
                InlineKeyboardButton(
                    text='♻️ Tʀʏ Aɢᴀɪɴ',
                    url=f"https://t.me/{client.username}?start={message.command[1]}"
                )
            ])
        except IndexError:
            pass

        await message.reply_photo(
            photo=FORCE_PIC,
            caption=FORCE_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    except Exception as e:
        print(f"Final Error: {e}")
        await temp.edit(
            f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @rohit_1888</i></b>\n"
            f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
        )
        await temp.delete
#=====================================================================================##

@Bot.on_message(filters.command('commands') & filters.private & admin)
async def bcmd(bot: Bot, message: Message):        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data = "close")]])
    await message.reply(text=CMD_TXT, reply_markup = reply_markup, quote= True)
