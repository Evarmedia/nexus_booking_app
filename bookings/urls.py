from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import confirm_email


urlpatterns = [
    # Web Views
    path('signup/', views.user_registration, name='signup'),
    path('login/', views.user_login, name='login'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),  # This is where the error was
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('confirm-email/<str:uidb64>/<str:token>/', confirm_email, name='confirm_email'),
    path('available-slots/', views.available_slots, name='available_slots'),
    path('book/<int:slot_id>/', views.create_booking, name='create_booking'),
    path('add-hairstylist/', views.add_hairstylist, name='add_hairstylist'),
    path('add-slot/', views.add_slot, name='add_slot'),
    path('delete-slot/<int:slot_id>/', views.delete_slot, name='delete_slot'),
    path('edit-slot/<int:slot_id>/', views.edit_slot, name='edit_slot'), 
    path('hairstylist-login/', views.hairstylist_login, name='hairstylist_login'),
    path('hairstylist-change-password/', views.hairstylist_change_password, name='hairstylist_change_password'),


    
    # API Views
    path('api/signup/', views.UserRegistrationAPI.as_view(), name='api_signup'),
    path('api/login/', views.UserLoginAPI.as_view(), name='api_login'),
    path('api/password-reset/', views.PasswordResetAPI.as_view(), name='api_password_reset'),
]
