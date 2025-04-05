from django.urls import path

from .views import HomeAPIView, populate_round_1_table, validate_token, StudentJudgeCountAPIView, StudentCreateAPIView

app_name = 'home'

urlpatterns = [
    path('', HomeAPIView.as_view(), name='home'),
    path('populate_round_1_table/', populate_round_1_table.as_view(),
         name='populate_round_1_table'),
    # path('populate_round_2_table/', populate_round_2_table.as_view(), name='populate_round_2_table'),
    path('validate_token/', validate_token.as_view(), name='validate_token'),
    path('show-judge-count/', StudentJudgeCountAPIView.as_view(), name='show-judge-count'),
    path('students/create/', StudentCreateAPIView.as_view(), name='create-student'),
] 
