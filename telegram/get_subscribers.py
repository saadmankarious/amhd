from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon import TelegramClient, sync
from telethon.tl.types import PeerUser
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, PeerChannel

api_id = '27035360'          # Replace with your API ID
api_hash = 'f847031a4ac722848f1d3f7c7fb4c538'      # Replace with your API Hash
phone_number = '+13192414128'  # Replace with your phone number (e.g., +123456789)



# Function to fetch subscribers
async def fetch_subscribers(client, channel_username):
    await client.start(phone=phone_number)
    print("Client Created")

    print(f"Fetching subscribers of channel: {channel_username}")
    subscribers = []
    
    try:
        channel = await client.get_entity(channel_username)
        if not isinstance(channel, PeerChannel):
            print(f"{channel_username} is not a valid channel.")
            return []
        
        offset = 0
        limit = 100
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
    except Exception as e:
        print(f"Error fetching subscribers: {e}")
    
    return subscribers

# Function to fetch user messages
async def fetch_user_messages(client, user_id):
    messages = []
    try:
        async for dialog in client.iter_dialogs():
            async for message in client.iter_messages(dialog.id, from_user=user_id):
                messages.append(message)
    except Exception as e:
        print(f"Error fetching messages for user {user_id}: {e}")
    return messages

# Main function
async def main(channel_username, min_messages):
    async with TelegramClient('session_name', api_id, api_hash) as client:
        # Fetch subscribers
        subscribers = await fetch_subscribers(client, channel_username)
        print(f"Total subscribers: {len(subscribers)}")

        # Process each subscriber
        for subscriber in subscribers:
            user_id = subscriber.id
            user_name = f"{subscriber.first_name or ''} {subscriber.last_name or ''}".strip() or subscriber.username or 'Unknown'

            # Fetch messages for the subscriber
            messages = await fetch_user_messages(client, user_id)
            if len(messages) > min_messages:
                print(f"User: {user_name} (ID: {user_id}) has {len(messages)} messages:")
                for message in messages:
                    print(f"- {message.text or 'Media/Other Content'}")
                print("\n")

# Run the script
if __name__ == '__main__':
    # Input parameters
    CHANNEL_USERNAME = input("Enter the channel username (e.g., @example_channel): ")
    MIN_MESSAGES = int(input("Enter the minimum number of messages to display: "))
    
    asyncio.run(main(CHANNEL_USERNAME, MIN_MESSAGES))
