from django.contrib import admin
from .models import CustomUser, Profile, Booking, Hotel, HotelImage, Review
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Profile)
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'hotel', 'check_in', 'check_out', 'adults','children','rooms', 'total_price', 'status', 'created_at')
    ordering = ('-created_at',)

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'total_rooms', 'available_rooms', 'capacity_per_room', 'price_per_night', 'created_at')
    search_fields = ('name', 'location')
    list_filter = ('location',)
    ordering = ('-created_at',)
admin.site.register(HotelImage)
admin.site.register(Review)