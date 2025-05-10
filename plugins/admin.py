import asyncio
import os
import random
import sys
import time
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction, ChatMemberStatus, ChatType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatMemberUpdated, ChatPermissions
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, InviteHashEmpty, ChatAdminRequired, PeerIdInvalid, UserIsBlocked, InputUserDeactivated
from bot import Bot
from config import *
from helper_func import *
from database.database import *



# Commands for adding admins by owner
@Bot.on_message(filters.command(['add_admin', 'addadmin']) & filters.user(OWNER_ID))
async def add_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    check = 0
    admin_ids = await db.get_all_admins()
    admins = []
    
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    # Case 1: Command with replied message
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        admins.append(str(user_id))
    
    # Case 2: Command with username or user_id
    elif len(message.command) > 1:
        # Get all arguments after command
        args = message.command[1:]
        for arg in args:
            # Handle username case
            if arg.startswith('@'):
                try:
                    user = await client.get_users(arg)
                    if user.is_deleted:
                        continue
                    if user.is_bot or user.is_verified or user.is_fake:
                        continue
                    admins.append(str(user.id))
                except Exception as e:
                    await pro.edit(f"<b>❌ Error: Failed to find user {arg}</b>\n\n<b>Error:</b> {str(e)}", reply_markup=reply_markup)
                    return
            # Handle user_id case
            else:
                admins.append(arg)
    
    # Show usage if no valid input
    if not admins:
        return await pro.edit(
            "<b>You need to provide a user to add as admin.</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/addadmin [reply to user]</code> — Add by replying to message\n"
            "<code>/addadmin @username</code> — Add by username\n"
            "<code>/addadmin [user_id]</code> — Add by user ID\n\n"
            "<b>Example:</b>\n"
            "<code>/addadmin 1234567890</code> or <code>/addadmin @username</code>",
            reply_markup=reply_markup
        )

    admin_list = ""
    for id_or_username in admins:
        try:
            # Try to convert to integer for validation
            try:
                user_id = int(id_or_username)
                # Try to validate if this is a user (not a channel or group)
                try:
                    user = await client.get_users(user_id)
                    # Skip if deleted, bot, verified, or fake
                    if user.is_deleted or user.is_bot or user.is_verified or user.is_fake:
                        admin_list += f"<blockquote><b>Invalid user: <code>{id_or_username}</code> (not a regular user)</b></blockquote>\n"
                        continue
                except (PeerIdInvalid, UserIsBlocked, InputUserDeactivated) as e:
                    # If we can't fetch the user details but have a numeric ID, we'll still try to add it
                    # This handles cases where the bot can't fetch user info but the ID is valid
                    pass
                except Exception as e:
                    # For unexpected errors, log and continue with adding the user
                    admin_list += f"<blockquote><b>Warning for ID <code>{user_id}</code>: {str(e)}</b></blockquote>\n"
            except ValueError:
                # Not an integer, skip this validation
                user_id = id_or_username
            
            # Check if user is already an admin
            if isinstance(user_id, int) and user_id in admin_ids:
                admin_list += f"<blockquote><b>ID <code>{user_id}</code> already exists as admin.</b></blockquote>\n"
                continue
            
            # For string IDs, convert to integer for storage
            if isinstance(user_id, str) and user_id.isdigit():
                user_id = int(user_id)
                if user_id in admin_ids:
                    admin_list += f"<blockquote><b>ID <code>{user_id}</code> already exists as admin.</b></blockquote>\n"
                    continue
                
                # Add user as admin
                admin_list += f"<b><blockquote>(ID: <code>{user_id}</code>) added.</blockquote></b>\n"
                await db.add_admin(user_id)
                check += 1
            elif isinstance(user_id, int):
                # Process integer user_id
                if user_id in admin_ids:
                    admin_list += f"<blockquote><b>ID <code>{user_id}</code> already exists as admin.</b></blockquote>\n"
                    continue
                
                # Add user as admin
                admin_list += f"<b><blockquote>(ID: <code>{user_id}</code>) added.</blockquote></b>\n"
                await db.add_admin(user_id)
                check += 1
            else:
                admin_list += f"<blockquote><b>Invalid ID: <code>{id_or_username}</code></b></blockquote>\n"
        except Exception as e:
            admin_list += f"<blockquote><b>Error with <code>{id_or_username}</code>: {str(e)}</b></blockquote>\n"

    if check > 0:
        await pro.edit(f"<b>✅ Admin(s) added successfully:</b>\n\n{admin_list}", reply_markup=reply_markup)
    else:
        await pro.edit(
            f"<b>❌ Failed to add admins:</b>\n\n{admin_list.strip()}\n\n"
            "<b><i>Please check and try again.</i></b>",
            reply_markup=reply_markup
        )


@Bot.on_message(filters.command(['deladmin', 'del_admin']) & filters.user(OWNER_ID))
async def delete_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    admin_ids = await db.get_all_admins()
    admins_to_remove = []
    
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])

    # Case 1: Command with replied message
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        admins_to_remove.append(str(user_id))
    
    # Case 2: Command with parameters (username, user_id, or "all")
    elif len(message.command) > 1:
        args = message.command[1:]
        
        # Check if "all" is provided
        if len(args) == 1 and args[0].lower() == "all":
            if admin_ids:
                ids = "\n".join(f"<blockquote><code>{admin}</code> ✅</blockquote>" for admin in admin_ids)
                for id in admin_ids:
                    await db.del_admin(id)
                return await pro.edit(f"<b>⛔️ All admin IDs have been removed:</b>\n{ids}", reply_markup=reply_markup)
            else:
                return await pro.edit("<b><blockquote>No admin IDs to remove.</blockquote></b>", reply_markup=reply_markup)
        
        # Process usernames and user_ids
        for arg in args:
            # Handle username case
            if arg.startswith('@'):
                try:
                    user = await client.get_users(arg)
                    admins_to_remove.append(str(user.id))
                except Exception as e:
                    await pro.edit(f"<b>❌ Error: Failed to find user {arg}</b>\n\n<b>Error:</b> {str(e)}", reply_markup=reply_markup)
                    return
            # Handle user_id case
            else:
                admins_to_remove.append(arg)
    
    # Show usage if no valid input
    if not admins_to_remove:
        return await pro.edit(
            "<b>Please provide a valid admin to remove.</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/deladmin [reply to user]</code> — Remove by replying to message\n"
            "<code>/deladmin @username</code> — Remove by username\n"
            "<code>/deladmin [user_id]</code> — Remove by user ID\n"
            "<code>/deladmin all</code> — Remove all admins",
            reply_markup=reply_markup
        )

    if admin_ids:
        removal_results = ''
        for id_or_username in admins_to_remove:
            try:
                # Try to convert to integer
                try:
                    user_id = int(id_or_username)
                except ValueError:
                    # If not an integer, try to get user info
                    try:
                        user = await client.get_users(id_or_username)
                        user_id = user.id
                    except Exception as e:
                        removal_results += f"<blockquote><b>Invalid user: <code>{id_or_username}</code> ({str(e)})</b></blockquote>\n"
                        continue
                
                # Check if user is in admin list
                if user_id in admin_ids:
                    await db.del_admin(user_id)
                    removal_results += f"<blockquote><code>{user_id}</code> ✅ Removed from admins</blockquote>\n"
                else:
                    removal_results += f"<blockquote><b>ID <code>{user_id}</code> not found in admin list.</b></blockquote>\n"
            except Exception as e:
                removal_results += f"<blockquote><b>Error with <code>{id_or_username}</code>: {str(e)}</b></blockquote>\n"

        await pro.edit(f"<b>⛔️ Admin removal result:</b>\n\n{removal_results}", reply_markup=reply_markup)
    else:
        await pro.edit("<b><blockquote>No admin IDs available to delete.</blockquote></b>", reply_markup=reply_markup)


@Bot.on_message(filters.command('admins') & admin)
async def get_admins(client: Client, message: Message):
    pro = await message.reply("<b><i>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ..</i></b>", quote=True)
    admin_ids = await db.get_all_admins()

    if not admin_ids:
        admin_list = "<b><blockquote>❌ No admins found.</blockquote></b>"
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])
        return await pro.edit(f"<b>⚡ Current Admin List:</b>\n\n{admin_list}", reply_markup=reply_markup)
    
    # Fetch admin information with names
    admin_list = "<b>📊 Current Admins:</b>\n\n"
    counter = 1
    
    for admin_id in admin_ids:
        try:
            # Try to get user information
            user = await client.get_users(admin_id)
            
            # Extract name information
            if user.first_name:
                name = user.first_name
                if user.last_name:
                    name += f" {user.last_name}"
            else:
                name = "Unknown"
                
            # Add username if available
            username = f"@{user.username}" if user.username else "No username"
            
            # Create a mention of the user
            mention = f"<a href='tg://user?id={admin_id}'>{name}</a>"
            
            admin_list += f"<b>{counter}.</b> {mention} : <code>{admin_id}</code>\n"
            if user.username:
                admin_list += f"   └ Username: {username}\n"
                
        except Exception as e:
            # If we can't get user info, just show the ID
            admin_list += f"<b>{counter}.</b> <code>{admin_id}</code> (User info unavailable)\n"
        
        counter += 1

    # Add close button
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close")]])
    
    await pro.edit(admin_list, reply_markup=reply_markup)
