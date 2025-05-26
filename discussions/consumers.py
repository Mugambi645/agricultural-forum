
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Comment, ContentAttachment # Make sure you import ContentAttachment

class DiscussionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.discussion_id = self.scope['url_route']['kwargs']['discussion_pk']
        self.discussion_group_name = f'discussion_{self.discussion_id}'

        await self.channel_layer.group_add(
            self.discussion_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.discussion_group_name,
            self.channel_name
        )

    # Receive message from room group
    async def new_comment_notification(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_comment_notification',
            'message': message
        }))

    # You might also have a receive method if comments are posted directly via WebSocket
    # For now, we assume comments are posted via HTTP POST and then broadcasted.

# In your views.py, when sending the message:
# (Already updated in the previous `views.py` provided, just confirming the structure)
# channel_layer = get_channel_layer()
# async_to_sync(channel_layer.group_send)(
#     f'discussion_{pk}',
#     {
#         'type': 'new_comment_notification',
#         'message': {
#             'id': new_comment.id,
#             'author': new_comment.author.username,
#             'author_id': new_comment.author.id, # <-- Ensure this is sent!
#             'content': new_comment.content,
#             'created_at': new_comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#             'is_flagged': new_comment.is_flagged,
#             'flag_reason': new_comment.flag_reason,
#             'votes': new_comment.votes,
#             'parent_id': new_comment.parent.id if new_comment.parent else None, # <-- Send None if no parent
#             'attachments': attachments_data
#         }
#     }
# )