"""
Views for User APIs
"""

from rest_framework import generics

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Create/Add a new user to the system"""
    serializer_class = UserSerializer
