from django.urls import path

from .views import round1_pre_check, round1_pre_check_without_ID, round1_pre_check_edit, \
    round1_pre_check_edit_without_ID


app_name = 'precheckposter'

urlpatterns = [
    path('round1_pre_check/<str:poster_id>/',
         round1_pre_check.as_view(), name='round1_pre_check'),
    # path('round2_pre_check/<str:poster_id>/', round2_pre_check.as_view(), name='round2_pre_check'),
    path('round1_pre_check/', round1_pre_check_without_ID.as_view(),
         name='round1_pre_check_without_ID'),
    # path('round2_pre_check/', round2_pre_check_without_ID.as_view(), name='round2_pre_check_without_ID'),
    path('round1_pre_check_edit/<str:poster_id>/checkforall',
         round1_pre_check_edit.as_view(), name='round1_pre_check_edit'),
    # path('round2_pre_check_edit/<str:poster_id>/', round2_pre_check_edit.as_view(), name='round2_pre_check_edit'),
    path('round1_pre_check_edit/', round1_pre_check_edit_without_ID.as_view(),
         name='round1_pre_check_edit_without_ID'),
    # path('round2_pre_check_edit/', round2_pre_check_edit_without_ID.as_view(), name='round2_pre_check_edit_without_ID'),
]
