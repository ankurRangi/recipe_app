"""
Test for models
"""
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@example.com', password='test@12345'):
    """Create and return a new user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    """Test Models"""

    def test_create_user_with_email_successfull(self):
        """Test creating a user with an email is successfull"""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
                email=email,
                password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_modified(self):
        """Test email is normalised for new users"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test valid email for new user without raising for ValueError"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test for Creating superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test create a new recipe objects"""
        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test@123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample Recipe Tiltle',
            time_minutes=5,
            price=Decimal('5.50'),
            description='Sample Recipe Description',
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_recipe_tag(self):
        """Create a tag for the recipe"""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)
