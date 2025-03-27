from django.urls import path
from .views import Signup

app_name = 'signup'

urlpatterns = [
    path('', Signup.as_view(), name='signup'),
]
