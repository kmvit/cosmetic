from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_view, extend_schema, \
    OpenApiParameter, OpenApiExample
from rest_framework import viewsets, mixins

from .filters import DynamicProductFilter
from .models import Product
from .serializers import ProductSerializer


@extend_schema(tags=["Продукция"])
@extend_schema_view(
    list=extend_schema(
        summary="Получить список отфильтрованной продукции",
        description="Чтобы отфильтровать продукцию по "
                    "параметрам необходимо сделать запрос по "
                    "примеру '?Возраст=20&Температура=20&УФ ИНДЕКС=2&Тип кожи=Жирная'"
    ),
    create=extend_schema(
        summary="Создание продукции получаемой с сайта ВП списком",
        description="Чтобы создать продукцию в БД сервиса нужно отправить список словарей",
        parameters=[
            OpenApiParameter(
                name='release',
                type=OpenApiTypes.JSON_PTR,
                location=OpenApiParameter.QUERY,
                description='Filter by release date',
                examples=[
                    OpenApiExample(
                        'Example 1',
                        summary='short optional summary',
                        description='longer description',
                        value='1993-08-23'
                    ),
                ],
            ),
        ]
    ),
)
class ProductViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin):
    """
    Создание и получение продукции
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DynamicProductFilter

    def get_serializer(self, *args, **kwargs):
        """
        Переопределяем метод для поддержки сериализации списка объектов.
        """
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)
