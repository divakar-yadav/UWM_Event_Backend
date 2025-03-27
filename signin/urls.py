from django.urls import path

from .views import Login

app_name = 'signin'

urlpatterns = [
    path('', Login.as_view(), name='signin'),
]