from rest_framework import serializers

from core.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Сериализатор для импорта косметики из бд сайта
    """
    class Meta:
        model = Product
        fields = [
            'name',
            'article_number'
        ]
