"""
Test for Recipe APIs
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Create and return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


# Helper Function
def create_recipe(user, **params):
    """Create and return a sample Recipe"""
    defaults = {
        'title': 'Sample Recipe Title',
        'time_minutes': 20,
        'price': Decimal('5.5'),
        'description': 'Sample recipe description.',
        'link': 'http://example.com/recipe.pdf',
    }
    # Overriding the params value to avoid any different Key-Value
    # pairs and use the default values to make the sample recipe
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeApiTest(TestCase):
    """Test unauthenticated APIs"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Test authorized recipe apis"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='test@12345',
            name='Test User',
        )
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        """Test retrive the recipes list"""
        create_recipe(self.user)
        create_recipe(self.user)
        res = self.client.get(RECIPE_URL)

        recipe = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipe, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_to_user(self):
        """Test list of recipes limited to the auth user"""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'test@12345',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipe = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipe, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe_id=recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating recipe from endpoint"""
        payload = {
            'title': 'Sample Recipe Title',
            'time_minutes': 20,
            'price': Decimal('5.5'),
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_create_recipe_with_new_tags(self):
        """Test create new recipe with new tags"""
        payload = {
            'title': 'Sample Recipe Title',
            'time_minutes': 10,
            'price': Decimal('5.5'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }
        res = self.client.post(RECIPE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)

        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tag.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tag.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)
