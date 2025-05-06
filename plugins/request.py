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
CHANNEL_ID = -1002635527933  # Channel where requests will be posted
ADMIN_IDS = [1993048420]  # List of admin user IDs
REQUESTS_FILE = "requests.json"

# Store requests in a JSON file
def load_requests():
    try:
        with open(REQUESTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_requests(requests):
    with open(REQUESTS_FILE, 'w') as f:
        json.dump(requests, f)

# Command handler for /request
@Bot.on_message(filters.command("request") & filters.private)
async def handle_request(client: Client, message: Message):
    # Extract the query from the message
    if len(message.command) < 2:
        await message.reply("Please provide your request after the /request command.")
        return

    request_text = " ".join(message.command[1:])
    user = message.from_user
    request_id = f"req_{int(datetime.now().timestamp())}"
    
    # Create request entry
    request_data = {
        "id": request_id,
        "user_id": user.id,
        "username": user.username or "No username",
        "first_name": user.first_name,
        "request_text": request_text,
        "status": "pending",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "admin_response": ""
    }
    
    # Save request
    requests = load_requests()
    requests[request_id] = request_data
    save_requests(requests)

    # Create inline keyboard for admin actions
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Accept", callback_data=f"accept_{request_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{request_id}")
        ],
        [
            InlineKeyboardButton("💬 Add Response", callback_data=f"respond_{request_id}")
        ]
    ])

    # Send to channel
    channel_msg = (
        f"📝 New Request #{request_id}\n"
        f"From: {user.mention}\n"
        f"Request: {request_text}\n"
        f"Status: Pending"
    )
    
    # Send to channel and notify admins
    await client.send_message(CHANNEL_ID, channel_msg, reply_markup=keyboard)
    
    # Notify user
    await message.reply(
        "Your request has been submitted and will be reviewed by admins.\n"
        f"Request ID: {request_id}"
    )
    
    # Notify all admins
    for admin_id in ADMIN_IDS:
        try:
            await client.send_message(
                admin_id,
                f"New request from {user.mention}:\n{request_text}",
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")

# Callback handler for admin actions
@Bot.on_callback_query()
async def handle_callback(client: Client, callback: CallbackQuery):
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
        
        await callback.message.edit_text(new_text)
        await callback.answer("Request updated successfully!")
        
    elif data.startswith("respond_"):
        request_id = data.split("_")[1]
        # Set user state to waiting for response
        app.admin_responding = {
            "admin_id": callback.from_user.id,
            "request_id": request_id
        }
        await callback.message.reply("Please send your response message:")
        await callback.answer()

# Handler for admin responses
@Bot.on_message(filters.private & filters.user(ADMIN_IDS))
async def handle_admin_response(client: Client, message: Message):
    if not hasattr(app, "admin_responding") or not app.admin_responding:
        return
    
    if message.from_user.id != app.admin_responding["admin_id"]:
        return
    
    request_id = app.admin_responding["request_id"]
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
        except Exception as e:
            print(f"Failed to notify user: {e}")
        
        await message.reply("Response added successfully!")
        
    Bot.admin_responding = None  # Reset the state
