from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Hotel Booking API",
      default_version='v1',
      description="API documentation for hotel booking, reviews, and wallet system",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
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
    path('transactions/', views.user_transactions, name='user-transactions'),

    path('hotels/<int:hotel_id>/reviews/', views.hotel_reviews, name='hotel-reviews'),
    path('hotels/<int:hotel_id>/reviews/<int:review_id>/', views.review_detail, name='review-detail'),


    
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
