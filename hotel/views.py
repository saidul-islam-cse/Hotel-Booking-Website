from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .import serializers
from .models import CustomUser, Profile, Hotel, Booking, HotelImage, Review, Transaction
from .utils import send_verification_email
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator

# Create your views here.
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

