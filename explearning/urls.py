from django.urls import path

from .views import GetExpLearningAPIView, UpdateExpLearningAPIView, ComputeAndStoreExpLearningAggregatesAPIView

app_name = 'home'

urlpatterns = [
    path('', GetExpLearningAPIView.as_view(), name='get_exp_learning'),
    path('update/', UpdateExpLearningAPIView.as_view(), name='update_exp_learning'),
    path('aggregate/', ComputeAndStoreExpLearningAggregatesAPIView.as_view(), name='exp-learning-aggregate')
]
