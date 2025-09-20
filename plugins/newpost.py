'''# +++ Modified By Yato [telegram username: @i_killed_my_clan & @ProYato] +++ # aNDI BANDI SANDI JISNE BHI CREDIT HATAYA USKI BANDI RAndi 
import asyncio
import base64
from bot import Bot
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant, FloodWait, ChatAdminRequired, RPCError
from pyrogram.errors import InviteHashExpired, InviteRequestSent
from database.database import save_channel, delete_channel, get_channels
from config import *
from database.database import *
from helper_func import *
from datetime import datetime, timedelta

PAGE_SIZE = 6

# Revoke invite link after 5-10 minutes
async def revoke_invite_after_5_minutes(client: Bot, channel_id: int, link: str, is_request: bool = False):
    await asyncio.sleep(300)  # 10 minutes
    try:
        if is_request:
            await client.revoke_chat_invite_link(channel_id, link)
            print(f"Jᴏɪɴ ʀᴇǫᴜᴇsᴛ ʟɪɴᴋ ʀᴇᴠᴏᴋᴇᴅ ғᴏʀ ᴄʜᴀɴɴᴇʟ {channel_id}")
        else:
            await client.revoke_chat_invite_link(channel_id, link)
            print(f"Iɴᴠɪᴛᴇ ʟɪɴᴋ ʀᴇᴠᴏᴋᴇᴅ ғᴏʀ ᴄʜᴀɴɴᴇʟ {channel_id}")
    except Exception as e:
        print(f"Fᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴠᴏᴋᴇ ɪɴᴠɪᴛᴇ ғᴏʀ ᴄʜᴀɴɴᴇʟ {channel_id}: {e}")

# channel add cmnd
@Bot.on_message(filters.command('addch') & is_owner_or_admin)
async def set_channel(client: Bot, message: Message):
    try:
        channel_id = int(message.command[1])
    except (IndexError, ValueError):
        return await message.reply("<b><blockquote expandable>Iɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ID. Exᴀᴍᴘʟᴇ: <code>/setchannel &lt;channel_id&gt;</code></b>")
    
    try:
        chat = await client.get_chat(channel_id)

        if chat.permissions and not (chat.permissions.can_post_messages or chat.permissions.can_edit_messages):
            return await message.reply(f"<b><blockquote expandable>I ᴀᴍ ɪɴ {chat.title}, ʙᴜᴛ I ʟᴀᴄᴋ ᴘᴏsᴛɪɴɢ ᴏʀ ᴇᴅɪᴛɪɴɢ ᴘᴇʀᴍɪssɪᴏɴs.</b>")
        
        await save_channel(channel_id)
        base64_invite = await save_encoded_link(channel_id)
        normal_link = f"https://t.me/{client.username}?start={base64_invite}"
        base64_request = await encode(str(channel_id))
        await save_encoded_link2(channel_id, base64_request)
        request_link = f"https://t.me/{client.username}?start=req_{base64_request}"
        reply_text = (
            f"<b><blockquote expandable>✅ Cʜᴀɴɴᴇʟ {chat.title} ({channel_id}) ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.</b>\n\n"
            f"<b>🔗 Nᴏʀᴍᴀʟ Lɪɴᴋ:</b> <code>{normal_link}</code>\n"
            f"<b>🔗 Rᴇǫᴜᴇsᴛ Lɪɴᴋ:</b> <code>{request_link}</code>"
        )
        return await message.reply(reply_text)
    
    except UserNotParticipant:
        return await message.reply("<b><blockquote expandable>I ᴀᴍ ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜɪs ᴄʜᴀɴɴᴇʟ. Pʟᴇᴀsᴇ ᴀᴅᴅ ᴍᴇ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</b>")
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await set_channel(client, message)
    except RPCError as e:
        return await message.reply(f"RPC Error: {str(e)}")
    except Exception as e:
        return await message.reply(f"Unexpected Error: {str(e)}")

# Delete channel command
@Bot.on_message(filters.command('delch') & is_owner_or_admin)
async def del_channel(client: Bot, message: Message):
    try:
        channel_id = int(message.command[1])
    except (IndexError, ValueError):
        return await message.reply("<b><blockquote expandable>Iɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ ID. Exᴀᴍᴘʟᴇ: <code>/delch &lt;channel_id&gt;</code></b>")
    
    await delete_channel(channel_id)
    return await message.reply(f"<b><blockquote expandable>❌ Cʜᴀɴɴᴇʟ {channel_id} ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.</b>")

# Channel post command
@Bot.on_message(filters.command('ch_links') & is_owner_or_admin)
async def channel_post(client: Bot, message: Message):
    channels = await get_channels()
    if not channels:
        return await message.reply("<b><blockquote expandable>Nᴏ ᴄʜᴀɴɴᴇʟs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ. Pʟᴇᴀsᴇ ᴜsᴇ /addch ᴛᴏ ᴀᴅᴅ ᴀ ᴄʜᴀɴɴᴇʟ.</b>")

    await send_channel_page(client, message, channels, page=0)

async def send_channel_page(client, message, channels, page, edit=False):
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    buttons = []

    row = []
    for channel_id in channels[start_idx:end_idx]:
        try:
            base64_invite = await save_encoded_link(channel_id)
            button_link = f"https://t.me/{client.username}?start={base64_invite}"
            chat = await client.get_chat(channel_id)
            
            row.append(InlineKeyboardButton(chat.title, url=button_link))
            
            if len(row) == 2:
                buttons.append(row)
                row = [] 
        except Exception as e:
            print(f"Error for channel {channel_id}: {e}")

    if row: 
        buttons.append(row)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("• Pʀᴇᴠɪᴏᴜs •", callback_data=f"channelpage_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("• Nᴇxᴛ •", callback_data=f"channelpage_{page+1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(buttons)
    if edit:
        await message.edit_text("Sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀᴄᴄᴇss:", reply_markup=reply_markup)
    else:
        await message.reply("Sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀᴄᴄᴇss:", reply_markup=reply_markup)

@Bot.on_callback_query(filters.regex(r"channelpage_(\d+)"))
async def paginate_channels(client, callback_query):
    page = int(callback_query.data.split("_")[1])
    channels = await get_channels()
    await send_channel_page(client, callback_query.message, channels, page, edit=True)

# Request post command
@Bot.on_message(filters.command('reqlink') & is_owner_or_admin)
async def req_post(client: Bot, message: Message):
    channels = await get_channels()
    if not channels:
        return await message.reply("<b><blockquote expandable>Nᴏ ᴄʜᴀɴɴᴇʟs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ. Pʟᴇᴀsᴇ ᴜsᴇ /setchannel ᴛᴏ ᴀᴅᴅ ᴀ ᴄʜᴀɴɴᴇʟ</b>")

    await send_request_page(client, message, channels, page=0)

async def send_request_page(client, message, channels, page, edit=False):
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    buttons = []

    row = []
    for channel_id in channels[start_idx:end_idx]:
        try:
            base64_request = await encode(str(channel_id))
            await save_encoded_link2(channel_id, base64_request)
            button_link = f"https://t.me/{client.username}?start=req_{base64_request}"
            chat = await client.get_chat(channel_id)

            row.append(InlineKeyboardButton(chat.title, url=button_link))

            if len(row) == 2:
                buttons.append(row)
                row = [] 
        except Exception as e:
            print(f"Error generating request link for channel {channel_id}: {e}")

    if row: 
        buttons.append(row)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("• Pʀᴇᴠɪᴏᴜs •", callback_data=f"reqpage_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("• Nᴇxᴛ •", callback_data=f"reqpage_{page+1}"))

    if nav_buttons:
        buttons.append(nav_buttons) 
    reply_markup = InlineKeyboardMarkup(buttons)
    if edit:
        await message.edit_text("Sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ʀᴇǫᴜᴇsᴛ ᴀᴄᴄᴇss:", reply_markup=reply_markup)
    else:
        await message.reply("Sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ʀᴇǫᴜᴇsᴛ ᴀᴄᴄᴇss:", reply_markup=reply_markup)

@Bot.on_callback_query(filters.regex(r"reqpage_(\d+)"))
async def paginate_requests(client, callback_query):
    page = int(callback_query.data.split("_")[1])
    channels = await get_channels()
    await send_request_page(client, callback_query.message, channels, page, edit=True)

# Links command - show all links as text
@Bot.on_message(filters.command('links') & is_owner_or_admin)
async def show_links(client: Bot, message: Message):
    channels = await get_channels()
    if not channels:
        return await message.reply("<b><blockquote expandable>Nᴏ ᴄʜᴀɴɴᴇʟs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ. Pʟᴇᴀsᴇ ᴜsᴇ /addch ᴛᴏ ᴀᴅᴅ ᴀ ᴄʜᴀɴɴᴇʟ.</b>")

    await send_links_page(client, message, channels, page=0)

async def send_links_page(client, message, channels, page, edit=False):
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    
    links_text = "<b>➤ Aʟʟ Cʜᴀɴɴᴇʟ Lɪɴᴋs:</b>\n\n"
    
    for i, channel_id in enumerate(channels[start_idx:end_idx], start=start_idx + 1):
        try:
            chat = await client.get_chat(channel_id)
            base64_invite = await save_encoded_link(channel_id)
            normal_link = f"https://t.me/{client.username}?start={base64_invite}"
            base64_request = await encode(str(channel_id))
            await save_encoded_link2(channel_id, base64_request)
            request_link = f"https://t.me/{client.username}?start=req_{base64_request}"
            
            links_text += f"<b>{i}. {chat.title}</b>\n"
            links_text += f"<b>➥ Nᴏʀᴍᴀʟ:</b> <code>{normal_link}</code>\n"
            links_text += f"<b>➤ Rᴇǫᴜᴇsᴛ:</b> <code>{request_link}</code>\n\n"
            
        except Exception as e:
            print(f"Error for channel {channel_id}: {e}")
            links_text += f"<b>{i}. Channel {channel_id}</b> (Error)\n\n"

    # Add pagination info
    links_text += f"<b>📄 Pᴀɢᴇ {page + 1} ᴏғ {total_pages}</b>"
    
    # Create navigation buttons
    buttons = []
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("• Pʀᴇᴠɪᴏᴜs •", callback_data=f"linkspage_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("• Nᴇxᴛ •", callback_data=f"linkspage_{page+1}"))

    if nav_buttons:
        buttons.append(nav_buttons)
    
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    
    if edit:
        await message.edit_text(links_text, reply_markup=reply_markup)
    else:
        await message.reply(links_text, reply_markup=reply_markup)

@Bot.on_callback_query(filters.regex(r"linkspage_(\d+)"))
async def paginate_links(client, callback_query):
    page = int(callback_query.data.split("_")[1])
    channels = await get_channels()
    await send_links_page(client, callback_query.message, channels, page, edit=True)

# Bulk link generation command
@Bot.on_message(filters.command('bulklink') & is_owner_or_admin)
async def bulk_link(client: Bot, message: Message):
    user_id = message.from_user.id

    if len(message.command) < 2:
        return await message.reply("<b><blockquote expandable>ᴜsᴀɢᴇ: <code>/bulklink &lt;id1&gt; &lt;id2&gt; ...</code></b>")

    ids = message.command[1:]
    reply_text = "<b>➤ Bᴜʟᴋ Lɪɴᴋ Gᴇɴᴇʀᴀᴛɪᴏɴ:</b>\n\n"
    for idx, id_str in enumerate(ids, start=1):
        try:
            channel_id = int(id_str)
            chat = await client.get_chat(channel_id)
            base64_invite = await save_encoded_link(channel_id)
            normal_link = f"https://t.me/{client.username}?start={base64_invite}"
            base64_request = await encode(str(channel_id))
            await save_encoded_link2(channel_id, base64_request)
            request_link = f"https://t.me/{client.username}?start=req_{base64_request}"
            reply_text += f"<b>{idx}. {chat.title} ({channel_id})</b>\n"
            reply_text += f"<b>➥ Nᴏʀᴍᴀʟ:</b> <code>{normal_link}</code>\n"
            reply_text += f"<b>➤ Rᴇǫᴜᴇsᴛ:</b> <code>{request_link}</code>\n\n"
        except Exception as e:
            reply_text += f"<b>{idx}. Channel {id_str}</b> (Error: {e})\n\n"
    await message.reply(reply_text)



@Bot.on_message(filters.command('genlink') & filters.private & is_owner_or_admin)
async def generate_link_command(client: Bot, message: Message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return await message.reply("<b>Usage:</b> <code>/genlink &lt;link&gt;</code>")

    link = message.command[1]
    # Store the link in the database channel
    try:
        sent_msg = await client.send_message(DATABASE_CHANNEL, f"#LINK\n{link}")
        channel_id = sent_msg.id  # Use id as unique id for this link
        # Save encoded links
        base64_invite = await save_encoded_link(channel_id)
        base64_request = await encode(str(channel_id))
        await save_encoded_link2(channel_id, base64_request)
        # Store the original link in the database
        from database.database import channels_collection
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {"$set": {"original_link": link}},
            upsert=True
        )
        normal_link = f"https://t.me/{client.username}?start={base64_invite}"
        request_link = f"https://t.me/{client.username}?start=req_{base64_request}"
        reply_text = (
            f"<b>✅ Link stored and encoded successfully.</b>\n\n"
            f"<b>🔗 Normal Link:</b> <code>{normal_link}</code>\n"
            f"<b>🔗 Request Link:</b> <code>{request_link}</code>"
        )
        await message.reply(reply_text)
    except Exception as e:
        await message.reply(f"<b>Error storing link:</b> <code>{e}</code>")

@Bot.on_message(filters.command('channels') & is_owner_or_admin)
async def show_channel_ids(client: Bot, message: Message):
    channels = await get_channels()
    if not channels:
        return await message.reply("<b><blockquote expandable>Nᴏ ᴄʜᴀɴɴᴇʟs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ. Pʟᴇᴀsᴇ ᴜsᴇ /addch ᴛᴏ ᴀᴅᴅ ᴀ ᴄʜᴀɴɴᴇʟ.</b>")
    status_msg = await message.reply("<i>Please wait...</i>")
    await send_channel_ids_page(client, message, channels, page=0, status_msg=status_msg)

async def send_channel_ids_page(client, message, channels, page, status_msg=None, edit=False):
    PAGE_SIZE = 10
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    text = "<b>➤ Cᴏɴɴᴇᴄᴛᴇᴅ Cʜᴀɴɴᴇʟs (ID & Name):</b>\n\n"
    for idx, channel_id in enumerate(channels[start_idx:end_idx], start=start_idx + 1):
        try:
            chat = await client.get_chat(channel_id)
            text += f"<b>{idx}. {chat.title}</b> <code>({channel_id})</code>\n"
        except Exception as e:
            text += f"<b>{idx}. Channel {channel_id}</b> (Error)\n"
    text += f"\n<b>📄 Pᴀɢᴇ {page + 1} ᴏғ {total_pages}</b>"
    # Navigation buttons
    buttons = []
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("• Pʀᴇᴠɪᴏᴜs •", callback_data=f"channelids_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("• Nᴇxᴛ •", callback_data=f"channelids_{page+1}"))
    if nav_buttons:
        buttons.append(nav_buttons)
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    if edit:
        await message.edit_text(text, reply_markup=reply_markup)
    else:
        await message.reply(text, reply_markup=reply_markup)
    if status_msg:
        try:
            await status_msg.delete()
        except:
            pass

@Bot.on_callback_query(filters.regex(r"channelids_(\d+)"))
async def paginate_channel_ids(client, callback_query):
    page = int(callback_query.data.split("_")[1])
    channels = await get_channels()
    await send_channel_ids_page(client, callback_query.message, channels, page, edit=True)'''

