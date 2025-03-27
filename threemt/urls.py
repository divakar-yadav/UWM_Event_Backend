from django.urls import path

from .views import GetThreeMtAPIView, UpdateThreeMtAPIView, ComputeAndStoreThreeMTAggregatesAPIView

app_name = 'home'

urlpatterns = [
    path('', GetThreeMtAPIView.as_view(), name='get_three_mt'),
    path('update/', UpdateThreeMtAPIView.as_view(), name='update_three_mt'),
    path('aggregate/', ComputeAndStoreThreeMTAggregatesAPIView.as_view(), name='three-mt-aggregate'),
]
