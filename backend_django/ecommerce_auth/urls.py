from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register/', views.register_user, name='register'),
    path('api/auth/login/', views.login_user, name='login'),
    path('api/auth/logout/', views.logout_user, name='logout'),
    path('api/auth/verify/', views.verify_token, name='verify_token'),
    path('api/admin/users/', views.list_users, name='list_users'),
    path('api/admin/users/<int:user_id>/toggle-block/', views.toggle_block_user, name='toggle_block_user'),
]
