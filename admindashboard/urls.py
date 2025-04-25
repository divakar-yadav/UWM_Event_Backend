from django.urls import path
from . import views

urlpatterns = [
    path('sorted_scores/', views.sorted_scores_view),
    path('category_scores/', views.category_scores_view),
    path('judge_progress/', views.judge_progress),
    path('status/', views.student_judge_status),
    path('export_excel/', views.export_excel_view),
    path('aggregate/', views.category_aggregate_view),
]
