from rest_framework import serializers
from .models import CustomUser, Profile, Hotel, HotelImage, Booking, Review, Transaction
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name','email', 'password']

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Only hash password if it's provided in the update
        if 'password' in validated_data and validated_data['password']:
            validated_data['password'] = make_password(validated_data['password'])
        return super().update(instance, validated_data)
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['phone_number']

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['name', 'address', 'city', 'description', 'price_per_night']

class HotelImageSerializer(serializers.ModelSerializer):
    hotel = HotelSerializer(read_only=True)
    hotel_id = serializers.PrimaryKeyRelatedField(
        queryset=Hotel.objects.all(), write_only=True, source='hotel'
    )

    class Meta:
        model = HotelImage
        fields = ['id', 'hotel', 'hotel_id', 'image', 'alt_text']
        read_only_fields = ['id', 'hotel']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['hotel', 'check_in', 'check_out']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['hotel', 'rating', 'comment']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['id', 'user', 'booking', 'amount', 'transaction_type', 'created_at']





    
