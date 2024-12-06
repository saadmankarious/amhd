from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
import json
import os
import asyncio

# Enter your own details
api_id = '27035360'          # Replace with your API ID
api_hash = 'f847031a4ac722848f1d3f7c7fb4c538'      # Replace with your API Hash
phone_number = '+13192414128'  # Replace with your phone number (e.g., +123456789)

# Channel to scrape messages from
channel_username = '@maharat_alhayah'  # Replace with the public channel username

# Initialize Telegram Client
client = TelegramClient('session_name', api_id, api_hash)

async def fetch_messages_across_dialogs(client, user_id):
    """Fetch all messages from a user across all accessible dialogs."""
    message_count = 0
    all_messages = []

    try:
        async for dialog in client.iter_dialogs():
            print(f"Scanning dialog: {dialog.name or dialog.title}")
            async for message in client.iter_messages(dialog.id, from_user=user_id):
                all_messages.append({
                    "dialog": dialog.name or dialog.title,
                    "date": message.date.strftime("%Y-%m-%d %H:%M:%S"),
                    "message": message.text or "Media/Other Content"
                })
                message_count += 1
    except Exception as e:
        print(f"Error fetching messages for user {user_id}: {e}")
    print(message_count)
    return all_messages, message_count

async def download_messages_and_analyze_subscribers():
    await client.start(phone=phone_number)
    print("Client Created")

    # Get the channel entity
    channel = await client.get_entity(channel_username)

    # Fetch subscribers
    print(f"Fetching subscribers of {channel_username}")
    subscribers = []
    offset = 0
    limit = 200

    while True:
        participants = await client(
            GetParticipantsRequest(
                channel=channel,
                filter=ChannelParticipantsSearch(''),
                offset=offset,
                limit=limit,
                hash=0
            )
        )
        subscribers.extend(participants.users)
        if len(participants.users) < limit:
            break
        offset += limit

    print(f"Total subscribers: {len(subscribers)}")

    # Analyze messages per subscriber
    active_subscribers = []
    for subscriber in subscribers:
        user_id = subscriber.id
        user_name = f"{subscriber.first_name or ''} {subscriber.last_name or ''}".strip() or subscriber.username or 'Unknown'
        print(f"Fetching messages for user: {user_name} (ID: {user_id})")

        messages, message_count = await fetch_messages_across_dialogs(client, user_id)
        if message_count > 5:
            active_subscribers.append({
                "id": user_id,
                "username": subscriber.username,
                "first_name": subscriber.first_name,
                "last_name": subscriber.last_name,
                "message_count": message_count,
                "messages": messages
            })
            print(f"User {user_name} has {message_count} messages.\n")

    print(f"Subscribers with more than 5 messages: {len(active_subscribers)}")

    # Save active subscribers to a JSON file
    os.makedirs("output", exist_ok=True)
    active_subscribers_file = f"output/{channel_username.strip('@')}_active_subscribers_with_messages.json"
    with open(active_subscribers_file, 'w', encoding='utf-8') as file:
        json.dump(active_subscribers, file, ensure_ascii=False, indent=4)

    print(f"Saved active subscribers to: {active_subscribers_file}")

with client:
    client.loop.run_until_complete(download_messages_and_analyze_subscribers())
