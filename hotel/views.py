from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .import serializers
from .models import CustomUser, Profile, Hotel, Booking, HotelImage, Review, Transaction
from .utils import send_verification_email, send_user_mail
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from decimal import Decimal
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.
@swagger_auto_schema(
    method='post',
    request_body=serializers.UserSerializer,
    responses={
        201: 'User registered successfully',
        400: 'Validation error'
    }
)
@swagger_auto_schema(
    method='get',
    responses={
        200: serializers.UserSerializer(many=True),
        401: 'Authentication required'
    }
)
@api_view(['POST', 'GET'])
def user_registration(request):
    if request.method == 'POST':
        serializer = serializers.UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)

            #create associated profile
            Profile.objects.create(
                user=user,
                phone_number=request.data.get('phone_number', ''),
                wallet_balance=0.00,
                email_verified=False
            )

            send_verification_email(request, user)

            return Response({'detail': 'User registered successfully. Please check your email to verify your account.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        if not request.user.is_authenticated:
            return Response({'detail' : 'Authentication credentials were not provided'}, status=401)
        users = CustomUser.objects.all()
        serializer = serializers.UserSerializer(users, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='get',
    responses={
        200: 'Email verified successfully',
        400: 'Invalid verification link'
    }
)
@api_view(['GET'])
def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.profile.email_verified = True
        user.profile.save()
        user.save()
        return Response({'detail': 'Email verified successfully. You can now log in.'}, status=status.HTTP_200_OK)
    else:
        return Response({'detail': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: serializers.ProfileSerializer(), 401: 'Authentication required'}
)
@swagger_auto_schema(
    method='put',
    request_body=serializers.ProfileSerializer,
    responses={200: serializers.ProfileSerializer(), 400: 'Validation error'}
)
@api_view(['GET', 'PUT'])
def user_profile(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required'}, status=401)
    
    profile = Profile.objects.get(user=request.user)
    
    if request.method == 'GET':
        serializer = serializers.ProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = serializers.ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@swagger_auto_schema(
    method='get',
    responses={200: serializers.HotelSerializer(many=True)}
)
@swagger_auto_schema(
    method='post',
    request_body=serializers.HotelSerializer,
    responses={201: serializers.HotelSerializer(), 400: 'Validation error'}
)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def hotel_list_create(request):
    if request.method == 'GET':
        hotels = Hotel.objects.all()
        serializer = serializers.HotelSerializer(hotels, many=True, context={'request': request})
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=401)
        
        serializer = serializers.HotelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='get',
    responses={200: serializers.HotelImageSerializer(many=True)}
)
@swagger_auto_schema(
    method='post',
    request_body=serializers.HotelImageSerializer,
    responses={201: serializers.HotelImageSerializer(), 400: 'Validation error'}
)
@api_view(['GET', 'POST'])
def hotel_image_list_create(request):
    if request.method == 'GET':
        images = HotelImage.objects.all()
        serializer = serializers.HotelImageSerializer(images, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=401)
        
        serializer = serializers.HotelImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@swagger_auto_schema(
    method='get',
    responses={200: serializers.HotelSerializer(), 404: 'Hotel not found'}
)
@swagger_auto_schema(
    method='put',
    request_body=serializers.HotelSerializer,
    responses={200: serializers.HotelSerializer(), 400: 'Validation error'}
)
@swagger_auto_schema(
    method='delete',
    responses={204: 'Hotel deleted successfully', 404: 'Hotel not found'}
)
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def hotel_detail(request, pk):
    try:
        hotel = Hotel.objects.get(pk=pk)
    except Hotel.DoesNotExist:
        return Response({'detail': 'Hotel not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = serializers.HotelSerializer(hotel)
        return Response(serializer.data)
    
    if request.user.is_superuser:
        if request.method == 'PUT':
            serializer = serializers.HotelSerializer(hotel, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            hotel.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        

def helper_functions(hotel, check_in, check_out, adults, children, rooms_requested):
    # 1. Overlapping bookings check
    overlapping_bookings = Booking.objects.filter(
        hotel=hotel,
        check_in__lt=check_out,
        check_out__gt=check_in,
        status='booked'
    )
    booked_rooms = sum(b.rooms for b in overlapping_bookings)
    available_rooms = hotel.total_rooms - booked_rooms
    if available_rooms < rooms_requested:
        return False, 'Not enough rooms available for the selected dates.'

    # 2. Capacity check
    total_capacity = rooms_requested * hotel.capacity_per_room
    if (adults + children) > total_capacity:
        return False, 'Selected rooms cannot accommodate the number of guests.'
      
    return True, {
        "available_rooms": available_rooms,
        "capacity_per_room": hotel.capacity_per_room,
        "price_per_night": hotel.price_per_night
    }


@swagger_auto_schema(
    method='get',
    query_serializer=serializers.HotelSearchSerializer,
    responses={200: 'List of available hotels', 400: 'Validation error'}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def search_hotels(request):
    serializer = serializers.HotelSearchSerializer(data=request.GET.dict())
    if serializer.is_valid():
        location = serializer.validated_data['location']
        check_in = serializer.validated_data['check_in']
        check_out = serializer.validated_data['check_out']
        adults = serializer.validated_data['adults']
        children = serializer.validated_data['children']
        rooms_requested = serializer.validated_data['rooms']

        # Filter hotels by location
        hotels = Hotel.objects.filter(location__icontains=location)
        available_hotels = []

        for hotel in hotels:
            is_available, data = helper_functions(hotel, check_in, check_out, adults, children, rooms_requested)

            # Add hotel to results
            if is_available:
                available_hotels.append({
                    "id": hotel.id,
                    "name": hotel.name,
                    "location": hotel.location,
                    "image": (f"http://127.0.0.1:8000{hotel.images.first().image.url}" if hotel.images.exists() else None),
                    "available_rooms": data['available_rooms'],
                    "capacity_per_room": data['capacity_per_room'],
                    "price_per_night": data['price_per_night']
                })

        return Response({"results": available_hotels}, status=200)

    return Response(serializer.errors, status=400)



@swagger_auto_schema(
    method='get',
    responses={200: serializers.BookingSerializer(many=True), 401: 'Authentication required'}
)
@swagger_auto_schema(
    method='post',
    request_body=serializers.BookingSerializer,
    responses={201: 'Booking created', 400: 'Validation error / Insufficient balance'}
)
@api_view(['POST', 'GET'])
def booking_create(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required'}, status=401)
    if request.method == 'GET':
        
        bookings = Booking.objects.filter(user=request.user)
        serializer = serializers.BookingSerializer(bookings, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = serializers.BookingSerializer(data=request.data)
        if serializer.is_valid():
            hotel = serializer.validated_data['hotel']
            check_in = serializer.validated_data['check_in']
            check_out = serializer.validated_data['check_out']
            adults = serializer.validated_data.get('adults', 1)
            children = serializer.validated_data.get('children', 0)
            rooms_requested = serializer.validated_data.get('rooms', 1)

            is_available, data =helper_functions(hotel, check_in, check_out, adults, children, rooms_requested)
        
            if not is_available:
                 return Response({'detail': data}, status=400)

            # Create booking
            nights = (check_out - check_in).days
            total_price = hotel.price_per_night * rooms_requested * nights

            profile = request.user.profile

            if profile.wallet_balance < total_price:
                return Response({'detail': 'Insufficient wallet balance.'}, status=400)
            
            profile.wallet_balance -= total_price
            profile.save()

            booking = Booking.objects.create(
                user=request.user,
                hotel=hotel,
                check_in=check_in,
                check_out=check_out,
                adults=adults,
                children=children,
                rooms=rooms_requested,
                total_price=total_price,
                status='booked'
            )

            Transaction.objects.create(
                user=request.user,
                booking=booking,
                amount=total_price,
                transaction_type="Booking Payment"
            )

            send_user_mail(
                request.user,
                "Booking Confirmed",
                f"Dear {request.user.first_name}, your booking for {hotel.name} "
                f"from {check_in} to {check_out} is confirmed.\nTotal Paid: {total_price}."
            )

            return Response(
                {
                    'detail': 'Booking created successfully.',
                    'booking_id': booking.id
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@swagger_auto_schema(
    method='post',
    responses={200: 'Booking cancelled and refunded', 404: 'Booking not found', 400: 'Already cancelled'}
)
@api_view(['POST'])
def cancel_booking(request, booking_id):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required'}, status=401)
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({'detail': 'Booking not found'}, status=404)
    
    if booking.status == 'cancelled':
        return Response({'detail': 'Booking is already cancelled'}, status=400)
    
    
    booking.status = 'cancelled'
    booking.save()
    
    profile = request.user.profile
    profile.wallet_balance += booking.total_price
    profile.save()

    Transaction.objects.create(
        user=request.user,
        booking=booking,
        amount=booking.total_price,
        transaction_type='Refund'
    )
    send_user_mail(
        request.user,
        "Booking Cancelled & Refund Processed",
        f"Dear {request.user.first_name}, your booking at {booking.hotel.name} "
        f"has been cancelled.\nRefund Amount: {booking.total_price} added back "
        f"to your wallet.\nNew Balance: {profile.wallet_balance}."
    )

    return Response({'detail': 'Booking cancelled and amount refunded'}, status=200)
    

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={'amount': openapi.Schema(type=openapi.TYPE_NUMBER)}
    ),
    responses={200: 'Deposit successful', 400: 'Validation error', 401: 'Authentication required'}
)
@api_view(['POST'])
def wallet_deposit(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required'}, status=401)
    amount = request.data.get('amount')
    try:
        amount = Decimal(amount)
    except:
        return Response({'detail': 'Invalid amount'}, status=400)
    
    if amount <= 500:
        return Response({'detail': 'Deposit amount must be  greater than or equal 500'}, status=400)
    
    profile = request.user.profile
    profile.wallet_balance += amount
    profile.save()
    Transaction.objects.create(
        user=request.user,
        amount=amount,
        transaction_type='Deposit'
    )

    send_user_mail(
        request.user,
        "Wallet Deposit Successful",
        f"Dear {request.user.first_name}, your deposit of {amount} was successful.\n"
        f"Your new wallet balance is {profile.wallet_balance}."
    )

    return Response({'detail': 'Deposit successful', 'new_balance': profile.wallet_balance}, status=200)


permission_classes([AllowAny])
@swagger_auto_schema(
    method='get',
    responses={200: serializers.ReviewSerializer(many=True), 404: 'Hotel not found'}
)
@swagger_auto_schema(
    method='post',
    request_body=serializers.ReviewSerializer,
    responses={201: serializers.ReviewSerializer(), 400: 'Validation error', 401: 'Authentication required'}
)
@api_view(['GET', 'POST'])
def hotel_reviews(request, hotel_id):
    try:
        hotel = Hotel.objects.get(id=hotel_id)
    except Hotel.DoesNotExist:
        return Response({'detail': 'Hotel not found'}, status=404)

    if request.method == 'GET':
        reviews = Review.objects.filter(hotel=hotel)
        serializer = serializers.ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    # POST (add review)
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required'}, status=401)

    serializer = serializers.ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, hotel=hotel)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@swagger_auto_schema(
    method='put',
    request_body=serializers.ReviewSerializer,
    responses={200: serializers.ReviewSerializer(), 400: 'Validation error', 404: 'Review not found'}
)
@swagger_auto_schema(
    method='delete',
    responses={204: 'Review deleted', 404: 'Review not found'}
)
@api_view(['PUT', 'DELETE'])
def review_detail(request, hotel_id, review_id):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required'}, status=401)
    
    try:
        review = Review.objects.get(id=review_id, user=request.user, hotel_id=hotel_id)
    except Review.DoesNotExist:
        return Response({'detail': 'Review not found or not authorized'}, status=404)

    if request.method == 'PUT':
        serializer = serializers.ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        review.delete()
        return Response({'detail': 'Review deleted successfully'}, status=204)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def user_transactions(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Authentication required'}, status=401)
    
    transactions = Transaction.objects.filter(user=request.user).order_by('-created_at')
    serializer = serializers.TransactionSerializer(transactions, many=True)
    return Response(serializer.data)