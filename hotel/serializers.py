from rest_framework import serializers
from .models import CustomUser, Profile, Hotel, HotelImage, Booking, Review, Transaction
from django.contrib.auth.hashers import make_password
from datetime import date
from django.db.models import Avg, Max

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
    user = UserSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = ['phone_number', 'wallet_balance', 'created_at', 'user',]
        read_only_fields = ['wallet_balance', 'created_at', 'user']

class HotelSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    max_rating = serializers.SerializerMethodField()
    class Meta:
        model = Hotel
        fields = ['id','name', 'address', 'location', 'description','total_rooms', 'price_per_night','image', 'average_rating', 'max_rating']
        read_only_fields = ['id', 'available_rooms','image']
    
    def get_image(self, obj):
        first_image = obj.images.first()  # related_name='images'
        if first_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_image.image.url)  # absolute URL
            return f"https://hotel-booking-website-46ia.onrender.com{first_image.image.url}"
        return None

    def get_average_rating(self, obj):
        avg_rating = obj.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else None

    def get_max_rating(self, obj):
        max_rating = obj.reviews.aggregate(Max('rating'))['rating__max']
        return max_rating if max_rating else None


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
    hotel_name = serializers.CharField(source="hotel.name", read_only=True) 
    class Meta:
        model = Booking
        fields = ['id', 'user','hotel', 'hotel_name', 'check_in', 'check_out', 'adults', 'children', 'rooms','total_price', 'status', 'created_at']
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
        fields = '__all__'
        read_only_fields = ['id', 'user','hotel', 'created_at', 'updated_at']

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



    
