from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import confirm_email
from .views import AddHairstylistAPI, HairstylistLoginAPI, AvailableSlotsAPI, AddSlotAPI, EditSlotAPI, DeleteSlotAPI, CreateBookingAPI, HairstylistChangePasswordAPI, ConfirmEmailAPI




urlpatterns = [
    # Web Views
    path('signup/', views.user_registration, name='signup'),
    path('login/', views.user_login, name='login'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),  
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
    path('api/add-hairstylist/', AddHairstylistAPI.as_view(), name='api_add_hairstylist'),
    path('api/hairstylist-login/', HairstylistLoginAPI.as_view(), name='api_hairstylist_login'),
    path('api/available-slots/', AvailableSlotsAPI.as_view(), name='api_available_slots'),
    path('api/add-slot/', AddSlotAPI.as_view(), name='api_add_slot'),
    path('api/edit-slot/<int:slot_id>/', EditSlotAPI.as_view(), name='api_edit_slot'),
    path('api/delete-slot/<int:slot_id>/', DeleteSlotAPI.as_view(), name='api_delete_slot'),
    path('api/create-booking/<int:slot_id>/', CreateBookingAPI.as_view(), name='api_create_booking'),
    path('api/hairstylist-change-password/', HairstylistChangePasswordAPI.as_view(), name='api_hairstylist_change_password'),
    path('api/confirm-email/<str:uidb64>/<str:token>/', ConfirmEmailAPI.as_view(), name='api_confirm_email'),
]
