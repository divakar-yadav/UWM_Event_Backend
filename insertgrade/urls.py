from django.urls import path

from .views import round1_insert, round1_edit

app_name = 'insertgrade'

urlpatterns = [
    path('round1_insert/<str:poster_id>/',
         round1_insert.as_view(), name='round1_insert'),
    path('round1_insert/', round1_insert.as_view(), name='round1_insert'),
    # path('round2_insert/<str:poster_id>/', round2_insert.as_view(), name='round2_insert'),
    # path('round2_insert/', round2_insert.as_view(), name='round2_insert'),
    path('round1_edit/<str:poster_id>/',
         round1_edit.as_view(), name='round1_edit'),
    path('round1_edit/', round1_edit.as_view(), name='round1_edit'),
    # path('round2_edit/<str:poster_id>/', round2_edit.as_view(), name='round2_edit'),
    # path('round2_edit/', round2_edit.as_view(), name='round2_edit'),
]
