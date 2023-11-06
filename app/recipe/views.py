"""
Views for Recipes API
"""

from rest_framework import (
    viewsets,
    mixins,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core import models
from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
    IngredientSerializer,
)


# ModelViewSet supports all methods (GET, PUT, PATCH, DELETE, POST),
# but in some cases you may only need a handful of these. Using
# GenericViewSet allows you to explicitly specify these.
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe apis"""
    serializer_class = RecipeDetailSerializer
    queryset = models.Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrive recipes for auth users"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return serializer class for the request"""
        if self.action == 'list':
            return RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new Recipe"""
        serializer.save(user=self.request.user)


# Just Adding the mixins.UpdateModelMixin class, it will
# handle all the path/update requests automatically
class BaseRecipeAttrViewSet(mixins.DestroyModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    """Base viewset for recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = TagSerializer
    queryset = models.Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database"""
    serializer_class = IngredientSerializer
    queryset = models.Ingredient.objects.all()
