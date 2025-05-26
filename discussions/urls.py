from django.urls import path
from . import views
app_name = "discussions"
urlpatterns = [
    path('', views.discussion_list, name='discussion_list'),
    path('new/', views.create_discussion, name='create_discussion'),
    path('<int:pk>/', views.discussion_detail, name='discussion_detail'),
    path('upvote_comment/<int:pk>/', views.upvote_comment, name='upvote_comment'),
    path('downvote_comment/<int:pk>/', views.downvote_comment, name='downvote_comment'),
    path('delete_comment/<int:pk>/', views.delete_comment, name='delete_comment'),
    path('<int:discussion_pk>/reply/<int:parent_pk>/', views.reply_to_comment, name='reply_to_comment'),
]