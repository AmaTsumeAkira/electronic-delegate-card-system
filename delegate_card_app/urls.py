# delegate_card_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DelegateViewSet
from .views import home_page_view

router = DefaultRouter()
router.register(r'delegates', DelegateViewSet, basename='delegate')
urlpatterns = [
    path('', include(router.urls)),
    # 如果你有其他非 ViewSet 的 API 视图，也放在这里
]
urlpatterns = [
    path('', include(router.urls)),
    path('card-display/', home_page_view, name='card_display_page'), # 例如，电子代表证展示页
]