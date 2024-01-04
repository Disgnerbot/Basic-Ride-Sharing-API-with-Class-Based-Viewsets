from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .serializers import UserSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import User, Ride
from .serializers import UserSerializer, RideSerializer
from django.utils.functional import SimpleLazyObject


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        try:
            user = User.objects.get(username=username, password=password)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.get_serializer(user)
        return Response(serializer.data)
    


    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required to create a ride.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Ensure that the user instance is a User model
        # rider = request.user
        if isinstance(request.user, SimpleLazyObject):
            # rider = User.objects.get(pk=request.user.pk)

         serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save( status='REQUESTED')  # Set the rider and initial status
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = RideSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RideSerializer(instance)
        return Response(serializer.data)
    def start_ride(self, request, pk=None):
        ride = self.get_object()
        if ride.status == 'REQUESTED':
            ride.status = 'IN_PROGRESS'
            ride.driver = request.user  # Assuming the driver is the authenticated user
            ride.save()
            serializer = RideSerializer(ride)
            return Response(serializer.data)
        return Response({'detail': 'Cannot start a ride that is not requested.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def complete_ride(self, request, pk=None):
        ride = self.get_object()
        if ride.status == 'IN_PROGRESS':
            ride.status = 'COMPLETED'
            ride.save()
            serializer = RideSerializer(ride)
            return Response(serializer.data)
        return Response({'detail': 'Cannot complete a ride that is not in progress.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'])
    def cancel_ride(self, request, pk=None):
        ride = self.get_object()
        if ride.status in ['REQUESTED', 'IN_PROGRESS']:
            ride.status = 'CANCELLED'
            ride.save()
            serializer = RideSerializer(ride)
            return Response(serializer.data)
        return Response({'detail': 'Cannot cancel a ride that is already completed or cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
