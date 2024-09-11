from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

app_name = 'core'

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
]
