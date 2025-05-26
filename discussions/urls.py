from . import views
from django.urls import path

app_name = "discussions"

urlpatterns = [
    path('', views.discussion_list, name='discussion_list'),
    path('discussion/<int:pk>/', views.discussion_detail, name='discussion_detail'),
    path('discussion/new/', views.create_discussion, name='create_discussion'),
]