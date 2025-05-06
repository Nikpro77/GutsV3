from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    CallbackQuery,
    Message
)
from datetime import datetime
from config import *
from bot import Bot
from database.database import *
import json

# Configuration
CHANNEL_ID = -1002635527933
ADMIN_IDS = [1993048420]
REQUESTS_FILE = "requests.json"

# Store admin response state
admin_responding_state = {}

# Rest of your existing functions remain the same until the callback handler

@Bot.on_callback_query()
async def handle_callback(client: Client, callback: CallbackQuery):
    try:
        # Verify if user is admin
        if callback.from_user.id not in ADMIN_IDS:
            await callback.answer("You don't have permission to perform this action.", show_alert=True)
            return

        data = callback.data
        requests = load_requests()
        
        if data.startswith(("accept_", "reject_")):
            action, request_id = data.split("_")
            if request_id not in requests:
                await callback.answer("Request not found!", show_alert=True)
                return
            
            request = requests[request_id]
            request["status"] = "accepted" if action == "accept" else "rejected"
            save_requests(requests)
            
            # Update channel message
            new_text = (
                f"📝 Request #{request_id}\n"
                f"From: {request['username']}\n"
                f"Request: {request['request_text']}\n"
                f"Status: {'✅ Accepted' if action == 'accept' else '❌ Rejected'}"
            )
            
            if request.get("admin_response"):
                new_text += f"\n\nAdmin Response: {request['admin_response']}"
            
            try:
                # Notify user
                await client.send_message(
                    request["user_id"],
                    f"Your request (ID: {request_id}) has been {'accepted' if action == 'accept' else 'rejected'}."
                )
            except Exception as e:
                print(f"Failed to notify user: {e}")
                await callback.answer(f"Could not notify user, but status updated.", show_alert=True)
            
            # Update message and show confirmation
            await callback.message.edit_text(new_text)
            await callback.answer("Request updated successfully!")
            
        elif data.startswith("respond_"):
            request_id = data.split("_")[1]
            # Store state in the global dict instead of nonexistent app object
            admin_responding_state[callback.from_user.id] = {
                "request_id": request_id
            }
            await callback.message.reply("Please send your response message:")
            await callback.answer()
    except Exception as e:
        print(f"Callback error: {e}")
        await callback.answer("An error occurred. Please try again.", show_alert=True)

@Bot.on_message(filters.private & filters.user(ADMIN_IDS))
async def handle_admin_response(client: Client, message: Message):
    try:
        admin_id = message.from_user.id
        if admin_id not in admin_responding_state:
            return
        
        request_id = admin_responding_state[admin_id]["request_id"]
        requests = load_requests()
        
        if request_id in requests:
            requests[request_id]["admin_response"] = message.text
            save_requests(requests)
            
            # Update channel message
            request = requests[request_id]
            updated_text = (
                f"📝 Request #{request_id}\n"
                f"From: {request['username']}\n"
                f"Request: {request['request_text']}\n"
                f"Status: {request['status']}\n\n"
                f"Admin Response: {message.text}"
            )
            
            # Notify user about the response
            try:
                await client.send_message(
                    request["user_id"],
                    f"Admin response for your request (ID: {request_id}):\n{message.text}"
                )
                await message.reply("Response added and user notified successfully!")
            except Exception as e:
                print(f"Failed to notify user: {e}")
                await message.reply("Response added but couldn't notify user!")
            
        # Clear the admin state
        del admin_responding_state[admin_id]
    except Exception as e:
        print(f"Admin response error: {e}")
        await message.reply("An error occurred while processing your response. Please try again.")
