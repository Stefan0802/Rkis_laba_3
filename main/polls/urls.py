from tkinter.font import names

from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),


    path('post_list/', views.post_list, name='post_list'),  # URL для списка постов
    path('create/', views.create_post, name='create_post'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/like/', views.like_post, name='like_post'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),  # Маршрут для редактирования поста
    path('posts/<int:post_id>/delete/', views.delete_post, name='delete_post'),
]
