
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/discussions/(?P<discussion_id>\d+)/$', consumers.DiscussionConsumer.as_asgi()),
]