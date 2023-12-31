"""
URls for Recipe APIs
"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)


# """Viewset have all the endpoints along within
#     including Get, Put, Patch, Delete.
#     So, we just need to route the viewset in url"""

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]
