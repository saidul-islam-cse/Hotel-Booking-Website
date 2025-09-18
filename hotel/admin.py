from django.contrib import admin
from .models import CustomUser, Profile, Booking, Hotel, HotelImage, Review
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Booking)
admin.site.register(Hotel)
admin.site.register(HotelImage)
admin.site.register(Review)