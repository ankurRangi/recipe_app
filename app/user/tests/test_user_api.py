"""
Test for the USER API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

# This will return the full URL path for create endpoint
CREATE_USER_URL = reverse('user:create')


# Create a HELPER FUNCTION for testing so we dont have to do write
# the same code over an over again
def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


# Diving the test cases based on Unauthorised(Public)
# and Authorised(Private) APIs

class PublicUserApiTests(TestCase):
    """Test the public features of User API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_new_user_successfull(self):
        """Test creating a user is successfull"""
        payload = {
            'email': 'test@example.com',
            'password': 'test@123',
            'name': 'Test User',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exist(self):
        """Test checking if user with email already exists"""
        payload = {
            'email': 'test@example.com',
            'password': 'test@123',
            'name': 'Test User',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned is password less than 5 chars"""
        payload = {
            'email': 'test@example.com',
            'password': 'pwd',
            'name': 'Test User',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)
