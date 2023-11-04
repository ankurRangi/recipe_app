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
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


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

    def test_create_token_for_user(self):
        """Test for creating token for user in the system"""
        user_details = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'test-user-password',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertTrue('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credential(self):
        """Test returns error if credentials are invalid"""
        user_details = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'test-user-password',
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': 'incorrect',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_blank_password(self):
        """Test posting a blank password for user in the system"""
        payload = {
            'email': 'test@example.com',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unauthorized(self):
        """Test authentication for unauthorized user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='test@123',
            name='Test User',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_success(self):
        """"Test retriving profile for loged in user"""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test POST request not allowed on me endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test update the details for current user"""
        payload = {'name': 'Update Name', 'password': 'newpass123'}
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
