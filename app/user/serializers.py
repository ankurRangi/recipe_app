"""
Serializer for the User API
"""

from django.contrib.auth import get_user_model

from rest_framework import serializers


# Serializers are just a method to convert data from python objects.
# User gives a JSON input, then serializers validates the input and after
# converts the input to either python objects or a model to save into db
class UserSerializer(serializers.ModelSerializer):
    """Serializer to use the object"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'name']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # Create function will overwirte the defualt "objects.create()" function
    # with our own create_user() with the validated data
    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)
