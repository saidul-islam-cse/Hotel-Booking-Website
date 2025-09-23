from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views
urlpatterns = [
    path('register/', views.user_registration, name='register'),
    path('profiles/', views.user_profile, name='profiles'),
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify-email'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('hotels/', views.hotel_list_create, name='hotels'),
    path('hotel-images/', views.hotel_image_list_create, name='hotel-images'),
    path('hotel-details/<int:pk>/', views.hotel_detail, name='hotel-details'),

    path('search/', views.search_hotels, name='hotel-search'),
    path('bookings/', views.booking_create, name='bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel-booking'),
    path('wallet/deposit/', views.wallet_deposit, name='wallet-deposit'),
]
