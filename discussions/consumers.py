
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DiscussionConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for real-time discussion updates.
    Each discussion has its own "group" for broadcasting comments.
    """
    async def connect(self):
        self.discussion_id = self.scope['url_route']['kwargs']['discussion_id']
        self.discussion_group_name = f'discussion_{self.discussion_id}'

        # Join discussion group
        await self.channel_layer.group_add(
            self.discussion_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave discussion group
        await self.channel_layer.group_discard(
            self.discussion_group_name,
            self.channel_name
        )

    # Receive message from WebSocket (not used for sending comments from client, but can be)
    async def receive(self, text_data):
        # This consumer is primarily for broadcasting new comments from the server
        # If you wanted to allow clients to send messages via WebSocket,
        # you would process text_data here.
        pass

    # Receive message from channel layer (e.g., a new comment from a view)
    async def new_comment_notification(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_comment_notification',
            'message': message
        }))