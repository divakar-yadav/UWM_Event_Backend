from django.urls import path

from .views import Login, current_user

app_name = 'signin'

urlpatterns = [
    path('', Login.as_view(), name='signin'),
    path('me/', current_user, name='current_user'),
]