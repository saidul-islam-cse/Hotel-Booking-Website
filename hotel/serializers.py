from rest_framework import serializers
from .models import CustomUser, Profile, Hotel, HotelImage, Booking, Review, Transaction
from django.contrib.auth.hashers import make_password
from datetime import date

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
        fields = ['id','name', 'address', 'location', 'description','total_rooms', 'price_per_night']
        read_only_fields = ['id', 'available_rooms']

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
    # hotel = HotelSerializer(read_only=True)
    class Meta:
        model = Booking
        fields = ['id', 'user','hotel', 'check_in', 'check_out', 'adults', 'children', 'rooms', 'status', 'created_at']
        read_only_fields = ['id', 'user', 'total_price', 'status', 'created_at']


        def validate(self, attrs):
            check_in = attrs.get('check_in')
            check_out = attrs.get('check_out')
            adults = attrs.get('adults', 1)
            rooms = attrs.get('rooms', 1)

            if check_in <date.today():
                raise serializers.ValidationError("Check-in date cannot be in the past.")
            
            if check_out <= check_in:
                raise serializers.ValidationError("Check-out date must be after check-in date.")
            
            if adults <1:
                raise serializers.ValidationError("At least one adult is required for booking.")
            
            if rooms <1:
                raise serializers.ValidationError("At least one room must be booked.")
            return attrs

        

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['hotel', 'rating', 'comment']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['id', 'user', 'booking', 'amount', 'transaction_type', 'created_at']

class HotelSearchSerializer(serializers.Serializer):
    location = serializers.CharField(max_length=50)
    check_in = serializers.DateField(input_formats=['%Y-%m-%d'])
    check_out = serializers.DateField(input_formats=['%Y-%m-%d'])
    adults = serializers.IntegerField(min_value=1)
    children = serializers.IntegerField(min_value=0)
    rooms = serializers.IntegerField(min_value=1)



    
